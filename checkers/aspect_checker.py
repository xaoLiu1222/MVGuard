import cv2
import numpy as np
from .base import BaseChecker, CheckResult
from services.video_processor import VideoProcessor
from config import BLACK_BORDER_THRESHOLD, ASPECT_RATIO_VERTICAL


class AspectChecker(BaseChecker):
    """Rule 2: Reject vertical videos or videos with black borders."""

    rule_id = 2
    rule_name = "竖屏/黑边检测"

    def __init__(self):
        self.processor = VideoProcessor()

    def check(self, video_path: str, **kwargs) -> CheckResult:
        info = self.processor.get_video_info(video_path)
        width, height = info.get("width", 0), info.get("height", 0)

        if width == 0 or height == 0:
            return self._pass("无法获取视频尺寸")

        # Check vertical aspect ratio
        if width / height < ASPECT_RATIO_VERTICAL:
            return self._fail(f"竖屏视频 ({width}x{height})")

        # Check black borders
        frame = self.processor.extract_frame(video_path, info.get("duration", 0) / 2)
        if frame is None:
            return self._pass()

        if self._has_black_borders(frame):
            return self._fail("检测到黑边")

        return self._pass()

    def _has_black_borders(self, frame: np.ndarray) -> bool:
        """Check if frame has significant black borders."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # Check top/bottom borders
        top_border = gray[:int(h * 0.1), :]
        bottom_border = gray[int(h * 0.9):, :]

        # Check left/right borders
        left_border = gray[:, :int(w * 0.1)]
        right_border = gray[:, int(w * 0.9):]

        threshold = 15  # Pixel value threshold for "black"

        borders = [top_border, bottom_border, left_border, right_border]
        black_ratios = [(b < threshold).mean() for b in borders]

        # If any border is mostly black
        return any(r > BLACK_BORDER_THRESHOLD for r in black_ratios)
