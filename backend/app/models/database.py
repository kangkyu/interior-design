"""
SQLAlchemy database models for the Interior Design application
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Integer,
    Boolean,
    JSON,
    Float,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship

from app.config import settings


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models"""
    pass


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    """Design project - represents one room redesign session"""
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    name = Column(String(255), default="Untitled Project")
    status = Column(String(50), default="in_progress")  # in_progress, finalized, archived
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="projects")
    room_photo = relationship("RoomPhoto", back_populates="project", uselist=False, cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="project", cascade="all, delete-orphan", order_by="Message.created_at")
    versions = relationship("DesignVersion", back_populates="project", cascade="all, delete-orphan", order_by="DesignVersion.version_number")


class RoomPhoto(Base):
    """Original room photo uploaded by user"""
    __tablename__ = "room_photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, unique=True)

    # Image URLs
    image_url = Column(Text, nullable=False)
    thumbnail_url = Column(Text, nullable=True)
    depth_map_url = Column(Text, nullable=True)
    segmentation_url = Column(Text, nullable=True)

    # Room analysis from Vision AI
    analysis = Column(JSON, nullable=True)
    room_type = Column(String(100), nullable=True)

    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="room_photo")


class Message(Base):
    """Chat message in a design session"""
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)

    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)

    # For assistant messages with generated images
    image_url = Column(Text, nullable=True)
    version_number = Column(Integer, nullable=True)

    # For user messages with uploaded images
    uploaded_image_url = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="messages")


class DesignVersion(Base):
    """A version of the design (each iteration)"""
    __tablename__ = "design_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)

    version_number = Column(Integer, nullable=False)
    image_url = Column(Text, nullable=False)
    thumbnail_url = Column(Text, nullable=True)

    # What was changed
    prompt_used = Column(Text, nullable=True)
    changes = Column(JSON, nullable=True)  # Structured changes made
    change_type = Column(String(50), nullable=True)  # minor, moderate, major

    # Generation metadata
    seed = Column(Integer, nullable=True)
    generation_params = Column(JSON, nullable=True)

    # Status
    is_favorite = Column(Boolean, default=False)
    is_final = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="versions")


# Database connection setup
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
