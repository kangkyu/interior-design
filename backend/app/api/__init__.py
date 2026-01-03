from fastapi import APIRouter

from app.api.routes import projects, chat, images, export

api_router = APIRouter()

api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(chat.router, prefix="/projects", tags=["chat"])
api_router.include_router(images.router, prefix="/projects", tags=["images"])
api_router.include_router(export.router, prefix="/projects", tags=["export"])
