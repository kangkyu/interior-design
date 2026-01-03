"""
Project management routes
"""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import get_db, Project, RoomPhoto, Message, DesignVersion
from app.models.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectDetailResponse,
    RoomAnalysis,
    DesignVersionResponse,
)

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new design project"""
    project = Project(
        name=project_data.name or "Untitled Project",
    )
    db.add(project)
    await db.flush()
    await db.refresh(project)

    return ProjectResponse(
        id=project.id,
        name=project.name,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        has_room_photo=False,
        current_version=None,
        message_count=0,
    )


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """List all projects"""
    # Query projects with counts
    query = (
        select(Project)
        .options(selectinload(Project.room_photo))
        .options(selectinload(Project.versions))
        .options(selectinload(Project.messages))
        .order_by(Project.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    projects = result.scalars().all()

    return [
        ProjectResponse(
            id=p.id,
            name=p.name,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at,
            has_room_photo=p.room_photo is not None,
            current_version=max([v.version_number for v in p.versions], default=None),
            message_count=len(p.messages),
        )
        for p in projects
    ]


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get project details"""
    query = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.room_photo))
        .options(selectinload(Project.versions))
        .options(selectinload(Project.messages))
    )

    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Get current image (latest version or original)
    current_image_url = None
    original_image_url = None

    if project.room_photo:
        original_image_url = project.room_photo.image_url

    if project.versions:
        latest_version = max(project.versions, key=lambda v: v.version_number)
        current_image_url = latest_version.image_url
    elif project.room_photo:
        current_image_url = project.room_photo.image_url

    # Parse room analysis
    room_analysis = None
    if project.room_photo and project.room_photo.analysis:
        try:
            room_analysis = RoomAnalysis(**project.room_photo.analysis)
        except Exception:
            pass

    return ProjectDetailResponse(
        id=project.id,
        name=project.name,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        has_room_photo=project.room_photo is not None,
        current_version=max([v.version_number for v in project.versions], default=None),
        message_count=len(project.messages),
        room_analysis=room_analysis,
        current_image_url=current_image_url,
        original_image_url=original_image_url,
    )


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update project details"""
    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if project_data.name is not None:
        project.name = project_data.name
    if project_data.status is not None:
        project.status = project_data.status.value

    await db.flush()
    await db.refresh(project)

    return ProjectResponse(
        id=project.id,
        name=project.name,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        has_room_photo=False,
        current_version=None,
        message_count=0,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a project"""
    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    await db.delete(project)


@router.get("/{project_id}/versions", response_model=list[DesignVersionResponse])
async def get_versions(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get all design versions for a project"""
    query = (
        select(DesignVersion)
        .where(DesignVersion.project_id == project_id)
        .order_by(DesignVersion.version_number)
    )

    result = await db.execute(query)
    versions = result.scalars().all()

    return [
        DesignVersionResponse(
            id=v.id,
            version_number=v.version_number,
            image_url=v.image_url,
            thumbnail_url=v.thumbnail_url,
            changes=v.changes,
            is_favorite=v.is_favorite,
            is_final=v.is_final,
            created_at=v.created_at,
        )
        for v in versions
    ]


@router.post("/{project_id}/versions/{version_number}/favorite")
async def toggle_favorite(
    project_id: UUID,
    version_number: int,
    db: AsyncSession = Depends(get_db),
):
    """Toggle favorite status for a version"""
    query = (
        select(DesignVersion)
        .where(DesignVersion.project_id == project_id)
        .where(DesignVersion.version_number == version_number)
    )

    result = await db.execute(query)
    version = result.scalar_one_or_none()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )

    version.is_favorite = not version.is_favorite
    await db.flush()

    return {"is_favorite": version.is_favorite}


@router.post("/{project_id}/versions/{version_number}/finalize")
async def finalize_version(
    project_id: UUID,
    version_number: int,
    db: AsyncSession = Depends(get_db),
):
    """Mark a version as the final design"""
    # First, unmark any existing final versions
    query = (
        select(DesignVersion)
        .where(DesignVersion.project_id == project_id)
        .where(DesignVersion.is_final == True)
    )
    result = await db.execute(query)
    for v in result.scalars().all():
        v.is_final = False

    # Mark the selected version as final
    query = (
        select(DesignVersion)
        .where(DesignVersion.project_id == project_id)
        .where(DesignVersion.version_number == version_number)
    )
    result = await db.execute(query)
    version = result.scalar_one_or_none()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )

    version.is_final = True

    # Update project status
    project_query = select(Project).where(Project.id == project_id)
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()
    if project:
        project.status = "finalized"

    await db.flush()

    return {"message": "Design finalized", "version": version_number}
