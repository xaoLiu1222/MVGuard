from .base import BaseChecker, CheckResult
from services.video_processor import VideoProcessor


class ResolutionChecker(BaseChecker):
    """Rule 11: Check video resolution (must be at least 720p)."""

    rule_id = 11
    rule_name = "清晰度检测"

    MIN_HEIGHT = 720  # 超清标准

    def __init__(self):
        self.processor = VideoProcessor()

    def check(self, video_path: str, **kwargs) -> CheckResult:
        info = self.processor.get_video_info(video_path)
        height = info.get("height", 0)
        width = info.get("width", 0)

        if height == 0:
            return self._pass("无法获取分辨率")

        # Use the smaller dimension for vertical videos
        resolution = min(width, height) if width < height else height

        if resolution < self.MIN_HEIGHT:
            return self._fail(f"清晰度低于超清 ({width}x{height})")

        return self._pass()
