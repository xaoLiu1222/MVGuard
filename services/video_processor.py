import subprocess
import base64
import tempfile
import json
from pathlib import Path
import cv2
import numpy as np


class VideoProcessor:
    """Video processing utilities using FFmpeg and OpenCV."""

    @staticmethod
    def get_video_info(video_path: str) -> dict:
        """Get video metadata using ffprobe."""
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return {}

        data = json.loads(result.stdout)
        video_stream = next((s for s in data.get("streams", []) if s["codec_type"] == "video"), {})

        return {
            "width": int(video_stream.get("width", 0)),
            "height": int(video_stream.get("height", 0)),
            "duration": float(data.get("format", {}).get("duration", 0)),
            "codec": video_stream.get("codec_name", ""),
        }

    @staticmethod
    def extract_frame(video_path: str, timestamp: float) -> np.ndarray | None:
        """Extract a single frame at given timestamp."""
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
        ret, frame = cap.read()
        cap.release()
        return frame if ret else None

    @staticmethod
    def extract_frames(video_path: str, count: int = 5) -> list[np.ndarray]:
        """Extract evenly distributed frames from video."""
        info = VideoProcessor.get_video_info(video_path)
        duration = info.get("duration", 0)
        if duration <= 0:
            return []

        timestamps = [duration * i / (count + 1) for i in range(1, count + 1)]
        frames = []
        for ts in timestamps:
            frame = VideoProcessor.extract_frame(video_path, ts)
            if frame is not None:
                frames.append(frame)
        return frames

    @staticmethod
    def extract_first_frames(video_path: str, seconds: float = 10, count: int = 3) -> list[np.ndarray]:
        """Extract frames from first N seconds."""
        timestamps = [seconds * i / (count + 1) for i in range(1, count + 1)]
        frames = []
        for ts in timestamps:
            frame = VideoProcessor.extract_frame(video_path, ts)
            if frame is not None:
                frames.append(frame)
        return frames

    @staticmethod
    def frame_to_base64(frame: np.ndarray) -> str:
        """Convert frame to base64 string."""
        _, buffer = cv2.imencode(".jpg", frame)
        return base64.b64encode(buffer).decode("utf-8")

    @staticmethod
    def extract_audio_levels(video_path: str) -> list[float]:
        """Extract audio RMS levels using ffmpeg."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_path = f.name

        cmd = [
            "ffmpeg", "-i", video_path, "-af",
            "astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=" + temp_path,
            "-f", "null", "-"
        ]
        subprocess.run(cmd, capture_output=True)

        levels = []
        try:
            with open(temp_path, "r") as f:
                for line in f:
                    if "RMS_level" in line:
                        val = line.split("=")[-1].strip()
                        if val != "-inf":
                            levels.append(float(val))
        except:
            pass
        finally:
            Path(temp_path).unlink(missing_ok=True)

        return levels
