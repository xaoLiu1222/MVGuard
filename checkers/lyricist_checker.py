from .base import BaseChecker, CheckResult
from services.video_processor import VideoProcessor
from services.siliconflow_api import SiliconFlowClient


class LyricistChecker(BaseChecker):
    """Rule 1: Reject if lyricist/composer is 林夕."""

    rule_id = 1
    rule_name = "林夕作词作曲检测"

    def __init__(self, client: SiliconFlowClient = None):
        self.client = client or SiliconFlowClient()
        self.processor = VideoProcessor()

    def check(self, video_path: str, **kwargs) -> CheckResult:
        # Extract frames from first 10 seconds
        frames = self.processor.extract_first_frames(video_path, seconds=10, count=3)
        if not frames:
            return self._pass("无法提取帧")

        prompt = """请仔细查看这些图片，识别其中是否显示了作词人或作曲人的信息。
如果看到"作词"、"作曲"、"词"、"曲"等字样后面跟着"林夕"，请回答"是"。
如果没有看到林夕的名字，或者没有作词作曲信息，请回答"否"。
只需回答"是"或"否"。"""

        images = [self.processor.frame_to_base64(f) for f in frames]

        try:
            response = self.client.analyze_images(images, prompt)
            if "是" in response:
                return self._fail("检测到林夕作词/作曲")
            return self._pass()
        except Exception as e:
            return self._pass(f"API调用失败: {e}")
