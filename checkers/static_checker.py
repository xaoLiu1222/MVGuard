import cv2
import numpy as np
from .base import BaseChecker, CheckResult
from services.video_processor import VideoProcessor


class StaticChecker(BaseChecker):
    """Rule 12: Check if video has static/unchanging content."""

    rule_id = 12
    rule_name = "静态画面检测"

    SIMILARITY_THRESHOLD = 0.95  # 95% similar = static

    def __init__(self):
        self.processor = VideoProcessor()

    def check(self, video_path: str, **kwargs) -> CheckResult:
        info = self.processor.get_video_info(video_path)
        duration = info.get("duration", 0)
        if duration < 30:
            return self._pass()

        # Sample frames at different points
        timestamps = [duration * i / 6 for i in range(1, 6)]
        frames = [self.processor.extract_frame(video_path, t) for t in timestamps]
        frames = [f for f in frames if f is not None]

        if len(frames) < 3:
            return self._pass()

        # Compare consecutive frames
        static_count = 0
        for i in range(len(frames) - 1):
            if self._frames_similar(frames[i], frames[i + 1]):
                static_count += 1

        # If most frames are similar, it's static
        if static_count >= len(frames) - 2:
            return self._fail("画面长时间无变化(动态壁纸)")

        return self._pass()

    def _frames_similar(self, f1: np.ndarray, f2: np.ndarray) -> bool:
        """Check if two frames are very similar."""
        # Resize for faster comparison
        size = (64, 64)
        g1 = cv2.cvtColor(cv2.resize(f1, size), cv2.COLOR_BGR2GRAY)
        g2 = cv2.cvtColor(cv2.resize(f2, size), cv2.COLOR_BGR2GRAY)

        # Calculate structural similarity
        diff = cv2.absdiff(g1, g2)
        similarity = 1 - (np.mean(diff) / 255)
        return similarity > self.SIMILARITY_THRESHOLD
