from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import shutil
from pathlib import Path

from models.schemas import TaskCreate, TaskResponse
from core.task_manager import TaskManager


router = APIRouter(prefix="/api", tags=["tasks"])

task_manager: Optional[TaskManager] = None


def init_task_manager(manager: TaskManager):
    global task_manager
    task_manager = manager


@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    files: List[UploadFile] = File(...),
    name: Optional[str] = Form(None),
    codec: str = Form("libx264"),
    resolution: str = Form("1280x720"),
    video_bitrate: str = Form("2000k"),
    audio_bitrate: str = Form("128k")
):
    if not task_manager:
        raise HTTPException(status_code=500, detail="任务管理器未初始化")
    
    if not files:
        raise HTTPException(status_code=400, detail="请至少选择一个文件")
    
    saved_files = []
    for file in files:
        if file.filename:
            file_path = task_manager.uploads_dir / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(str(file_path))
    
    task_data = TaskCreate(
        name=name,
        codec=codec,
        resolution=resolution,
        video_bitrate=video_bitrate,
        audio_bitrate=audio_bitrate
    )
    
    task = task_manager.create_task(task_data, saved_files)
    return task


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks():
    if not task_manager:
        raise HTTPException(status_code=500, detail="任务管理器未初始化")
    return task_manager.list_tasks()


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    if not task_manager:
        raise HTTPException(status_code=500, detail="任务管理器未初始化")
    
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.post("/tasks/{task_id}/start")
async def start_task(task_id: str):
    if not task_manager:
        raise HTTPException(status_code=500, detail="任务管理器未初始化")
    
    success = task_manager.start_task(task_id)
    if not success:
        raise HTTPException(status_code=400, detail="无法启动任务，任务可能已在运行或已完成")
    return {"message": "任务已启动", "task_id": task_id}


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    if not task_manager:
        raise HTTPException(status_code=500, detail="任务管理器未初始化")
    
    success = task_manager.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=400, detail="无法取消任务，任务可能已完成或未在运行")
    return {"message": "任务已取消", "task_id": task_id}


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    if not task_manager:
        raise HTTPException(status_code=500, detail="任务管理器未初始化")
    
    success = task_manager.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"message": "任务已删除", "task_id": task_id}


@router.get("/outputs/{filename}")
async def download_output(filename: str):
    if not task_manager:
        raise HTTPException(status_code=500, detail="任务管理器未初始化")
    
    file_path = task_manager.outputs_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/octet-stream"
    )


@router.get("/uploads")
async def list_uploads():
    if not task_manager:
        raise HTTPException(status_code=500, detail="任务管理器未初始化")
    
    files = []
    for f in task_manager.uploads_dir.iterdir():
        if f.is_file():
            files.append({
                "name": f.name,
                "size": f.stat().st_size,
                "path": str(f.absolute())
            })
    return files


@router.get("/outputs")
async def list_outputs():
    if not task_manager:
        raise HTTPException(status_code=500, detail="任务管理器未初始化")
    
    files = []
    for f in task_manager.outputs_dir.iterdir():
        if f.is_file():
            files.append({
                "name": f.name,
                "size": f.stat().st_size,
                "path": str(f.absolute())
            })
    return files
