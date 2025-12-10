import re
from pathlib import Path
from .base import BaseChecker, CheckResult
from services.video_processor import VideoProcessor
from services.siliconflow_api import SiliconFlowClient


class NamingChecker(BaseChecker):
    """Rule 8: Check if filename matches artist-song format and content."""

    rule_id = 8
    rule_name = "文件命名检测"

    def __init__(self, client: SiliconFlowClient = None):
        self.client = client or SiliconFlowClient()
        self.processor = VideoProcessor()

    def check(self, video_path: str, **kwargs) -> CheckResult:
        filename = Path(video_path).stem

        # Parse expected format: artist-song
        match = re.match(r"^(.+?)-(.+)$", filename)
        if not match:
            return self._fail(f"文件名格式不符合'歌手名-歌曲名': {filename}")

        expected_artist, expected_song = match.groups()

        # Extract frames from beginning to verify
        frames = self.processor.extract_first_frames(video_path, seconds=10, count=2)
        if not frames:
            return self._pass("无法提取帧进行验证")

        images = [self.processor.frame_to_base64(f) for f in frames]

        prompt = f"""请查看这些MV画面，识别其中显示的歌手名和歌曲名。
文件名显示歌手是"{expected_artist}"，歌曲是"{expected_song}"。

请判断画面中显示的信息是否与文件名一致。
如果画面中没有显示歌手或歌曲信息，回答"无法判断"。
如果一致，回答"一致"。
如果不一致，回答"不一致"并说明实际看到的内容。"""

        try:
            response = self.client.analyze_images(images, prompt)
            if "不一致" in response:
                return self._fail(f"文件命名与内容不一致: {response}")
            return self._pass()
        except Exception as e:
            return self._pass(f"API调用失败: {e}")
