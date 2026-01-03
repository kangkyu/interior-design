"""
Export routes for generating specifications and reports
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import get_db, Project, RoomPhoto, DesignVersion, Message
from app.models.schemas import (
    ExportRequest,
    ExportFormat,
    DesignSpecification,
)
from app.services.spec_generator import spec_generator

router = APIRouter()


@router.post("/{project_id}/export")
async def export_design(
    project_id: UUID,
    request: ExportRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Export design specifications in various formats
    """
    # Get project with all related data
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

    if not project.room_photo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No room photo uploaded yet",
        )

    # Get the final or latest version
    final_version = None
    for v in project.versions:
        if v.is_final:
            final_version = v
            break

    if not final_version and project.versions:
        final_version = max(project.versions, key=lambda v: v.version_number)

    if not final_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No design versions created yet. Make some changes first!",
        )

    # Get conversation summary (changes made)
    conversation_summary = []
    for msg in project.messages:
        if msg.role == "user" and msg.content:
            conversation_summary.append(msg.content)

    # Generate specification
    spec = await spec_generator.generate_spec(
        final_image_url=final_version.image_url,
        original_image_url=project.room_photo.image_url,
        project_id=str(project_id),
        project_name=project.name,
        conversation_summary=conversation_summary[-5:],  # Last 5 changes
    )

    # Return based on format
    if request.format == ExportFormat.PDF:
        pdf_bytes = await spec_generator.generate_pdf(spec)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={project.name.replace(' ', '_')}_specification.pdf"
            },
        )

    elif request.format == ExportFormat.SHOPPING_LIST:
        return {
            "project_name": project.name,
            "furniture": [f.model_dump() for f in spec.furniture],
            "decor": spec.decor,
            "estimated_total": {
                "low": spec.total_budget_low,
                "high": spec.total_budget_high,
            },
        }

    elif request.format == ExportFormat.COLORS:
        return {
            "project_name": project.name,
            "paint_specifications": [p.model_dump() for p in spec.paint],
        }

    elif request.format == ExportFormat.JSON:
        return spec.model_dump()

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown format: {request.format}",
        )


@router.get("/{project_id}/specification", response_model=DesignSpecification)
async def get_specification(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the full design specification (JSON)
    """
    # Get project with all related data
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

    if not project.room_photo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No room photo uploaded yet",
        )

    # Get the final or latest version
    final_version = None
    for v in project.versions:
        if v.is_final:
            final_version = v
            break

    if not final_version and project.versions:
        final_version = max(project.versions, key=lambda v: v.version_number)

    if not final_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No design versions created yet",
        )

    # Get conversation summary
    conversation_summary = []
    for msg in project.messages:
        if msg.role == "user" and msg.content:
            conversation_summary.append(msg.content)

    # Generate and return specification
    spec = await spec_generator.generate_spec(
        final_image_url=final_version.image_url,
        original_image_url=project.room_photo.image_url,
        project_id=str(project_id),
        project_name=project.name,
        conversation_summary=conversation_summary[-5:],
    )

    return spec


@router.get("/{project_id}/export/pdf")
async def download_pdf(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Quick endpoint to download PDF specification
    """
    request = ExportRequest(format=ExportFormat.PDF)
    return await export_design(project_id, request, db)
