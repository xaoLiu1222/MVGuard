import cv2
import numpy as np
from .base import BaseChecker, CheckResult
from services.video_processor import VideoProcessor
from config import BLACK_BORDER_THRESHOLD, ASPECT_RATIO_VERTICAL


class AspectChecker(BaseChecker):
    """Rule 2: Reject vertical videos or videos with excessive black borders."""

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

        result = self._check_black_borders(frame)
        if result:
            return self._fail(result)

        return self._pass()

    def _check_black_borders(self, frame: np.ndarray) -> str | None:
        """Check black borders: left/right >50% or top/bottom >50% is violation."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        threshold = 15

        # Check left/right borders (>50% total width = violation)
        left_cols = 0
        for i in range(w // 2):
            if (gray[:, i] < threshold).mean() > 0.9:
                left_cols += 1
            else:
                break

        right_cols = 0
        for i in range(w - 1, w // 2, -1):
            if (gray[:, i] < threshold).mean() > 0.9:
                right_cols += 1
            else:
                break

        lr_ratio = (left_cols + right_cols) / w
        if lr_ratio > 0.5:
            return f"左右黑边占比过大 ({lr_ratio:.0%})"

        # Check top/bottom borders (>50% total height = violation)
        top_rows = 0
        for i in range(h // 2):
            if (gray[i, :] < threshold).mean() > 0.9:
                top_rows += 1
            else:
                break

        bottom_rows = 0
        for i in range(h - 1, h // 2, -1):
            if (gray[i, :] < threshold).mean() > 0.9:
                bottom_rows += 1
            else:
                break

        tb_ratio = (top_rows + bottom_rows) / h
        if tb_ratio > 0.5:
            return f"上下黑边占比过大 ({tb_ratio:.0%})"

        return None
