import threading
import uuid
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from enum import Enum

from models.schemas import TaskStatus, TaskCreate, TaskResponse, VideoFile, TranscodeSettings
from core.transcode import TranscodeEngine


class TaskManager:
    def __init__(self, uploads_dir: str, outputs_dir: str, ffmpeg_path: str = "ffmpeg"):
        self.uploads_dir = Path(uploads_dir)
        self.outputs_dir = Path(outputs_dir)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        
        self.engine = TranscodeEngine(ffmpeg_path, uploads_dir, outputs_dir)
        self.tasks: Dict[str, dict] = {}
        self.workers: Dict[str, threading.Thread] = {}
        self._lock = threading.Lock()

    def create_task(self, task_data: TaskCreate, files: List[str]) -> TaskResponse:
        task_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = task_data.name or f"转码任务_{timestamp}"
        
        videos: List[VideoFile] = []
        for file_path in files:
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                videos.append(VideoFile(
                    id=str(uuid.uuid4()),
                    name=file_path_obj.name,
                    original_path=str(file_path_obj.absolute()),
                    size=file_path_obj.stat().st_size
                ))
        
        task = {
            "id": task_id,
            "name": name,
            "status": TaskStatus.PENDING,
            "progress": 0,
            "total_files": len(videos),
            "completed_files": 0,
            "failed_files": 0,
            "current_file": None,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "videos": [v.dict() for v in videos],
            "settings": {
                "codec": task_data.codec,
                "resolution": task_data.resolution,
                "video_bitrate": task_data.video_bitrate,
                "audio_bitrate": task_data.audio_bitrate
            },
            "cancel_event": threading.Event()
        }
        
        with self._lock:
            self.tasks[task_id] = task
        
        return self._task_to_response(task)

    def start_task(self, task_id: str) -> bool:
        with self._lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            if task["status"] != TaskStatus.PENDING:
                return False
            
            task["status"] = TaskStatus.RUNNING
            task["started_at"] = datetime.now().isoformat()
        
        worker = threading.Thread(target=self._run_task, args=(task_id,))
        worker.daemon = True
        worker.start()
        
        with self._lock:
            self.workers[task_id] = worker
        
        return True

    def _run_task(self, task_id: str):
        task = self.tasks.get(task_id)
        if not task:
            return
        
        cancel_event = task["cancel_event"]
        settings = task["settings"]
        
        completed = 0
        failed = 0
        
        for i, video in enumerate(task["videos"]):
            if cancel_event.is_set():
                with self._lock:
                    self.tasks[task_id]["status"] = TaskStatus.CANCELLED
                break
            
            with self._lock:
                self.tasks[task_id]["current_file"] = video["name"]
                self.tasks[task_id]["videos"][i]["status"] = "running"
            
            input_path = video["original_path"]
            output_name = Path(video["name"]).stem + "_proxy.mp4"
            output_path = str(self.outputs_dir / output_name)
            
            def progress_callback(progress: int, time_str: str):
                with self._lock:
                    if task_id in self.tasks:
                        self.tasks[task_id]["videos"][i]["progress"] = progress
            
            success, error = self.engine.transcode_video(
                input_path=input_path,
                output_path=output_path,
                codec=settings["codec"],
                resolution=settings["resolution"],
                video_bitrate=settings.get("video_bitrate", "2000k"),
                audio_bitrate=settings.get("audio_bitrate", "128k"),
                progress_callback=progress_callback,
                cancel_event=cancel_event
            )
            
            with self._lock:
                if task_id not in self.tasks:
                    return
                
                if success:
                    self.tasks[task_id]["videos"][i]["status"] = "completed"
                    self.tasks[task_id]["videos"][i]["progress"] = 100
                    self.tasks[task_id]["videos"][i]["output_path"] = output_path
                    completed += 1
                else:
                    self.tasks[task_id]["videos"][i]["status"] = "failed"
                    self.tasks[task_id]["videos"][i]["error"] = error
                    failed += 1
                
                self.tasks[task_id]["completed_files"] = completed
                self.tasks[task_id]["failed_files"] = failed
                
                total = self.tasks[task_id]["total_files"]
                if total > 0:
                    self.tasks[task_id]["progress"] = int(((completed + failed) / total) * 100)
        
        with self._lock:
            if task_id in self.tasks:
                if cancel_event.is_set():
                    self.tasks[task_id]["status"] = TaskStatus.CANCELLED
                elif failed > 0 and completed == 0:
                    self.tasks[task_id]["status"] = TaskStatus.FAILED
                else:
                    self.tasks[task_id]["status"] = TaskStatus.COMPLETED
                self.tasks[task_id]["completed_at"] = datetime.now().isoformat()

    def cancel_task(self, task_id: str) -> bool:
        with self._lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            if task["status"] != TaskStatus.RUNNING:
                return False
            
            task["cancel_event"].set()
            return True

    def delete_task(self, task_id: str) -> bool:
        with self._lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            if task["status"] == TaskStatus.RUNNING:
                task["cancel_event"].set()
            
            del self.tasks[task_id]
            if task_id in self.workers:
                del self.workers[task_id]
            
            return True

    def get_task(self, task_id: str) -> Optional[TaskResponse]:
        with self._lock:
            task = self.tasks.get(task_id)
            if task:
                return self._task_to_response(task)
        return None

    def list_tasks(self) -> List[TaskResponse]:
        with self._lock:
            return [self._task_to_response(t) for t in self.tasks.values()]

    def _task_to_response(self, task: dict) -> TaskResponse:
        videos = [VideoFile(**v) for v in task["videos"]]
        return TaskResponse(
            id=task["id"],
            name=task["name"],
            status=task["status"],
            progress=task["progress"],
            total_files=task["total_files"],
            completed_files=task["completed_files"],
            failed_files=task["failed_files"],
            current_file=task["current_file"],
            created_at=task["created_at"],
            started_at=task.get("started_at"),
            completed_at=task.get("completed_at"),
            videos=videos,
            settings=TranscodeSettings(**task["settings"])
        )
