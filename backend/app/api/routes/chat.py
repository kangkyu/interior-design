"""
Chat routes for design conversations
"""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import get_db, Project, RoomPhoto, Message, DesignVersion
from app.models.schemas import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatResponse,
    RoomAnalysis,
    MessageRole,
)
from app.services.orchestrator import orchestrator, DesignSession, DesignResponse

router = APIRouter()


async def get_session_from_project(
    project_id: UUID,
    db: AsyncSession,
) -> tuple[Project, DesignSession]:
    """Build a DesignSession from project data"""
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

    # Build session
    room_analysis = None
    if project.room_photo and project.room_photo.analysis:
        try:
            room_analysis = RoomAnalysis(**project.room_photo.analysis)
        except Exception:
            pass

    # Get current image
    current_image_url = None
    original_image_url = None
    depth_map_url = None

    if project.room_photo:
        original_image_url = project.room_photo.image_url
        depth_map_url = project.room_photo.depth_map_url

    if project.versions:
        latest_version = max(project.versions, key=lambda v: v.version_number)
        current_image_url = latest_version.image_url
    elif project.room_photo:
        current_image_url = project.room_photo.image_url

    # Build conversation history
    conversation_history = [
        {"role": m.role, "content": m.content}
        for m in sorted(project.messages, key=lambda m: m.created_at)
    ]

    current_version = max(
        [v.version_number for v in project.versions],
        default=0,
    )

    session = DesignSession(
        project_id=str(project_id),
        room_analysis=room_analysis,
        current_image_url=current_image_url,
        original_image_url=original_image_url,
        depth_map_url=depth_map_url,
        current_version=current_version,
        conversation_history=conversation_history,
    )

    return project, session


@router.post("/{project_id}/chat", response_model=ChatResponse)
async def send_message(
    project_id: UUID,
    message: ChatMessageCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Send a chat message and get AI response with design
    """
    project, session = await get_session_from_project(project_id, db)

    # Save user message
    user_message = Message(
        project_id=project_id,
        role="user",
        content=message.content,
    )
    db.add(user_message)

    # Process with orchestrator
    response: DesignResponse = await orchestrator.process_message(
        user_message=message.content,
        session=session,
    )

    # Save assistant response
    assistant_message = Message(
        project_id=project_id,
        role="assistant",
        content=response.message,
        image_url=response.image_url,
        version_number=response.version,
    )
    db.add(assistant_message)

    # If we got a new design, save the version
    if response.type == "design" and response.image_url:
        new_version = DesignVersion(
            project_id=project_id,
            version_number=response.version,
            image_url=response.image_url,
            thumbnail_url=response.thumbnail_url,
            changes=[c.model_dump() for c in response.changes] if response.changes else None,
        )
        db.add(new_version)

    await db.flush()

    return ChatResponse(
        type=response.type,
        message=response.message,
        image_url=response.image_url,
        version=response.version,
        changes=response.changes,
    )


@router.get("/{project_id}/chat/history", response_model=list[ChatMessageResponse])
async def get_chat_history(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get chat history for a project"""
    query = (
        select(Message)
        .where(Message.project_id == project_id)
        .order_by(Message.created_at)
    )

    result = await db.execute(query)
    messages = result.scalars().all()

    return [
        ChatMessageResponse(
            id=m.id,
            role=MessageRole(m.role),
            content=m.content,
            image_url=m.image_url,
            uploaded_image_url=m.uploaded_image_url,
            version_number=m.version_number,
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.websocket("/{project_id}/ws")
async def websocket_chat(
    websocket: WebSocket,
    project_id: UUID,
):
    """
    WebSocket endpoint for real-time chat
    """
    await websocket.accept()

    # We need to create a new session for each connection
    from app.models.database import AsyncSessionLocal

    try:
        while True:
            data = await websocket.receive_json()

            async with AsyncSessionLocal() as db:
                try:
                    if data.get("type") == "message":
                        # Send status update
                        await websocket.send_json({
                            "type": "status",
                            "status": "understanding",
                            "message": "Understanding your request...",
                        })

                        # Get session
                        project, session = await get_session_from_project(
                            UUID(str(project_id)),
                            db,
                        )

                        # Save user message
                        user_message = Message(
                            project_id=project_id,
                            role="user",
                            content=data.get("content", ""),
                        )
                        db.add(user_message)

                        # Send generating status
                        await websocket.send_json({
                            "type": "status",
                            "status": "generating",
                            "message": "Creating your new design...",
                        })

                        # Process message
                        response = await orchestrator.process_message(
                            user_message=data.get("content", ""),
                            session=session,
                        )

                        # Save assistant response
                        assistant_message = Message(
                            project_id=project_id,
                            role="assistant",
                            content=response.message,
                            image_url=response.image_url,
                            version_number=response.version,
                        )
                        db.add(assistant_message)

                        # Save version if new design
                        if response.type == "design" and response.image_url:
                            new_version = DesignVersion(
                                project_id=project_id,
                                version_number=response.version,
                                image_url=response.image_url,
                                thumbnail_url=response.thumbnail_url,
                                changes=[c.model_dump() for c in response.changes] if response.changes else None,
                            )
                            db.add(new_version)

                        await db.commit()

                        # Send response
                        await websocket.send_json({
                            "type": "response",
                            "response_type": response.type,
                            "message": response.message,
                            "image_url": response.image_url,
                            "version": response.version,
                        })

                except Exception as e:
                    await db.rollback()
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Error processing message: {str(e)}",
                    })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Connection error: {str(e)}",
            })
        except Exception:
            pass
