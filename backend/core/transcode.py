import subprocess
import os
import threading
import time
import uuid
from pathlib import Path
from typing import Dict, Optional, Callable, List
from datetime import datetime


class TranscodeEngine:
    def __init__(self, ffmpeg_path: str = "ffmpeg", uploads_dir: str = "uploads", outputs_dir: str = "outputs"):
        self.ffmpeg_path = ffmpeg_path
        self.uploads_dir = Path(uploads_dir)
        self.outputs_dir = Path(outputs_dir)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

    def get_video_info(self, video_path: str) -> dict:
        cmd = [
            self.ffmpeg_path,
            "-i", video_path,
            "-hide_banner"
        ]
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=30
            )
            output = result.stderr
            
            duration = None
            for line in output.split('\n'):
                if 'Duration:' in line:
                    try:
                        duration_str = line.split('Duration:')[1].split(',')[0].strip()
                        parts = duration_str.split(':')
                        duration = int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
                    except:
                        pass
            
            return {
                "duration": duration,
                "info": output
            }
        except Exception as e:
            return {"error": str(e)}

    def transcode_video(
        self,
        input_path: str,
        output_path: str,
        codec: str = "libx264",
        resolution: str = "1280x720",
        video_bitrate: str = "2000k",
        audio_bitrate: str = "128k",
        progress_callback: Optional[Callable[[int, str], None]] = None,
        cancel_event: Optional[threading.Event] = None
    ) -> tuple[bool, Optional[str]]:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        duration = self.get_video_info(input_path).get("duration")
        
        cmd = [
            self.ffmpeg_path,
            "-i", input_path,
            "-c:v", codec,
            "-s", resolution,
            "-b:v", video_bitrate,
            "-c:a", "aac",
            "-b:a", audio_bitrate,
            "-y",
            output_path
        ]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            while True:
                if cancel_event and cancel_event.is_set():
                    process.terminate()
                    return False, "已取消"

                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break

                if "time=" in line and duration and duration > 0:
                    try:
                        time_str = line.split("time=")[1].split(" ")[0].strip()
                        parts = time_str.split(":")
                        current_time = int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
                        progress = min(int((current_time / duration) * 100), 100)
                        if progress_callback:
                            progress_callback(progress, time_str)
                    except:
                        pass

            process.wait()
            
            if process.returncode == 0:
                return True, None
            else:
                return False, f"FFmpeg 错误，退出码: {process.returncode}"

        except Exception as e:
            return False, str(e)

    def scan_videos(self, directory: str):
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.m4v', '.mxf', '.webm', '.flv', '.wmv', '.mpg'}
        videos = []
        
        dir_path = Path(directory)
        if not dir_path.exists():
            return videos

        for file in dir_path.iterdir():
            if file.suffix.lower() in video_extensions:
                videos.append({
                    "id": str(uuid.uuid4()),
                    "name": file.name,
                    "original_path": str(file.absolute()),
                    "size": file.stat().st_size
                })
        
        return videos
