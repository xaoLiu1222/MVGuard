from .base import BaseChecker, CheckResult
from services.video_processor import VideoProcessor
from services.siliconflow_api import SiliconFlowClient


class DurationChecker(BaseChecker):
    """Rule 10: Check video duration and lyrics presence."""

    rule_id = 10
    rule_name = "时长/歌词检测"

    MAX_DURATION = 280  # 4min40s
    LYRICS_CHECK_INTERVAL = 60  # Check every 60 seconds

    def __init__(self, client: SiliconFlowClient = None):
        self.client = client or SiliconFlowClient()
        self.processor = VideoProcessor()

    def check(self, video_path: str, **kwargs) -> CheckResult:
        info = self.processor.get_video_info(video_path)
        duration = info.get("duration", 0)

        # Check duration
        if duration > self.MAX_DURATION:
            return self._fail(f"时长超过4分40秒 ({duration:.0f}秒)")

        # Check lyrics presence (sample every 60s)
        if duration > 60:
            no_lyrics_count = 0
            for t in range(30, int(duration) - 30, 60):
                frame = self.processor.extract_frame(video_path, t)
                if frame is None:
                    continue
                img = self.processor.frame_to_base64(frame)
                if not self._has_lyrics(img):
                    no_lyrics_count += 1
                    if no_lyrics_count >= 1:  # 1 minute without lyrics
                        return self._fail("连续一分钟无歌词")
                else:
                    no_lyrics_count = 0

        return self._pass()

    def _has_lyrics(self, image: str) -> bool:
        """Check if frame has lyrics/subtitles."""
        prompt = "这张图片底部或画面中是否有歌词字幕？只回答'有'或'无'。"
        try:
            response = self.client.analyze_images([image], prompt)
            return "有" in response
        except:
            return True  # Assume has lyrics on error
