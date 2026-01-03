"""
Image upload and management routes
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db, Project, RoomPhoto, Message
from app.models.schemas import ImageUploadResponse, RoomAnalysis
from app.services.storage import storage_service
from app.services.room_analyzer import room_analyzer
from app.services.image_generator import image_generator

router = APIRouter()


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/heic",
}

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


@router.post("/{project_id}/upload", response_model=ImageUploadResponse)
async def upload_room_photo(
    project_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a room photo to start a design project
    """
    # Validate project exists
    project_query = select(Project).where(Project.id == project_id)
    result = await db.execute(project_query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Validate content type
    content_type = file.content_type or "image/jpeg"
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )

    # Read file
    image_bytes = await file.read()

    # Validate file size
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB",
        )

    # Validate it's a room photo
    is_valid, validation_message = await room_analyzer.validate_room_photo(image_bytes)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation_message,
        )

    # Upload to storage
    image_url = await storage_service.upload_image(
        image_bytes=image_bytes,
        folder="rooms",
        content_type=content_type,
    )

    # Create thumbnail
    thumbnail_url = await storage_service.create_thumbnail(
        image_bytes=image_bytes,
        folder="thumbnails",
    )

    # Analyze the room
    analysis, conversation_response = await room_analyzer.analyze_room(
        image_bytes=image_bytes,
    )

    # Generate depth map for better generation
    depth_map_url = None
    try:
        depth_map_url = await image_generator.generate_depth_map(image_url)
    except Exception:
        # Depth map is optional
        pass

    # Check if room photo already exists for this project
    existing_query = select(RoomPhoto).where(RoomPhoto.project_id == project_id)
    existing_result = await db.execute(existing_query)
    existing_photo = existing_result.scalar_one_or_none()

    if existing_photo:
        # Update existing
        existing_photo.image_url = image_url
        existing_photo.thumbnail_url = thumbnail_url
        existing_photo.analysis = analysis.model_dump()
        existing_photo.room_type = analysis.room_type
        existing_photo.depth_map_url = depth_map_url
    else:
        # Create new
        room_photo = RoomPhoto(
            project_id=project_id,
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            analysis=analysis.model_dump(),
            room_type=analysis.room_type,
            depth_map_url=depth_map_url,
        )
        db.add(room_photo)

    # Add the AI's initial response as a message
    initial_message = Message(
        project_id=project_id,
        role="assistant",
        content=conversation_response,
    )
    db.add(initial_message)

    await db.flush()

    return ImageUploadResponse(
        image_url=image_url,
        thumbnail_url=thumbnail_url,
        analysis=analysis,
        message=conversation_response,
    )


@router.get("/{project_id}/image")
async def get_current_image(
    project_id: UUID,
    version: int = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the current or specific version of the design image
    """
    from app.models.database import DesignVersion

    # Get project with room photo and versions
    project_query = select(Project).where(Project.id == project_id)
    result = await db.execute(project_query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Get room photo
    room_photo_query = select(RoomPhoto).where(RoomPhoto.project_id == project_id)
    room_photo_result = await db.execute(room_photo_query)
    room_photo = room_photo_result.scalar_one_or_none()

    if not room_photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No room photo uploaded yet",
        )

    # Get specific version or latest
    if version is not None:
        version_query = (
            select(DesignVersion)
            .where(DesignVersion.project_id == project_id)
            .where(DesignVersion.version_number == version)
        )
        version_result = await db.execute(version_query)
        design_version = version_result.scalar_one_or_none()

        if not design_version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {version} not found",
            )

        return {
            "image_url": design_version.image_url,
            "thumbnail_url": design_version.thumbnail_url,
            "version": design_version.version_number,
            "is_original": False,
        }
    else:
        # Get latest version
        versions_query = (
            select(DesignVersion)
            .where(DesignVersion.project_id == project_id)
            .order_by(DesignVersion.version_number.desc())
            .limit(1)
        )
        versions_result = await db.execute(versions_query)
        latest_version = versions_result.scalar_one_or_none()

        if latest_version:
            return {
                "image_url": latest_version.image_url,
                "thumbnail_url": latest_version.thumbnail_url,
                "version": latest_version.version_number,
                "is_original": False,
            }
        else:
            # Return original if no versions
            return {
                "image_url": room_photo.image_url,
                "thumbnail_url": room_photo.thumbnail_url,
                "version": 0,
                "is_original": True,
            }


@router.get("/{project_id}/original")
async def get_original_image(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the original room photo
    """
    room_photo_query = select(RoomPhoto).where(RoomPhoto.project_id == project_id)
    result = await db.execute(room_photo_query)
    room_photo = result.scalar_one_or_none()

    if not room_photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No room photo uploaded yet",
        )

    analysis = None
    if room_photo.analysis:
        try:
            analysis = RoomAnalysis(**room_photo.analysis)
        except Exception:
            pass

    return {
        "image_url": room_photo.image_url,
        "thumbnail_url": room_photo.thumbnail_url,
        "analysis": analysis,
        "room_type": room_photo.room_type,
    }
