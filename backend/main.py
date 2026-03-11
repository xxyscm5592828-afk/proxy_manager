from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from pathlib import Path

from api.routes import router as routes_router, init_task_manager
from api.websocket import router as ws_router
from core.task_manager import TaskManager


BASE_DIR = Path(__file__).parent
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"


task_manager = TaskManager(
    uploads_dir=str(UPLOADS_DIR),
    outputs_dir=str(OUTPUTS_DIR),
    ffmpeg_path="ffmpeg"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_task_manager(task_manager)
    yield


app = FastAPI(
    title="视频转码管理器 API",
    description="Web版视频转码任务管理系统",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_router)
app.include_router(ws_router)


@app.get("/")
async def root():
    return {
        "message": "视频转码管理器 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
