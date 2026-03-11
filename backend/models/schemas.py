from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TranscodeSettings(BaseModel):
    codec: str = "libx264"
    resolution: str = "1280x720"
    video_bitrate: Optional[str] = "2000k"
    audio_bitrate: Optional[str] = "128k"


class TaskCreate(BaseModel):
    name: Optional[str] = None
    codec: str = "libx264"
    resolution: str = "1280x720"
    video_bitrate: Optional[str] = "2000k"
    audio_bitrate: Optional[str] = "128k"


class VideoFile(BaseModel):
    id: str
    name: str
    original_path: str
    output_path: Optional[str] = None
    size: int
    status: str = "pending"
    progress: int = 0
    error: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    name: str
    status: TaskStatus
    progress: int = 0
    total_files: int = 0
    completed_files: int = 0
    failed_files: int = 0
    current_file: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    videos: List[VideoFile] = []
    settings: TranscodeSettings
