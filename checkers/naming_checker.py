import re
from pathlib import Path
from .base import BaseChecker, CheckResult
from services.video_processor import VideoProcessor
from services.siliconflow_api import SiliconFlowClient


class NamingChecker(BaseChecker):
    """Rule 8: Check filename-content consistency and song ownership."""

    rule_id = 8
    rule_name = "文件命名检测"

    def __init__(self, client: SiliconFlowClient = None):
        self.client = client or SiliconFlowClient()
        self.processor = VideoProcessor()

    def check(self, video_path: str, **kwargs) -> CheckResult:
        filename = Path(video_path).stem

        # Parse format: "artist：song" or "artist-song"
        match = re.match(r"^(.+?)[：:-](.+)$", filename)
        if not match:
            return self._fail(f"文件名格式不符合'歌手名-歌曲名': {filename}")

        artist, song = match.groups()
        artist, song = artist.strip(), song.strip()

        # Extract frames from beginning
        frames = self.processor.extract_first_frames(video_path, seconds=10, count=3)
        if not frames:
            return self._check_ownership(artist, song)

        images = [self.processor.frame_to_base64(f) for f in frames]

        # Step 1: Check if MV shows song title
        prompt1 = f"""查看这些MV开头画面，是否显示了歌曲名称？
如果显示了歌名，请回答"歌名：XXX"（XXX为看到的歌名）。
如果没有显示歌名，回答"无歌名"。"""

        try:
            response = self.client.analyze_images(images, prompt1)

            if "无歌名" not in response:
                # Has song title in MV, check consistency
                if song.lower() not in response.lower():
                    return self._fail(f"MV显示歌名与文件名不一致: {response}")

            # Step 2: Check song ownership
            return self._check_ownership(artist, song)

        except Exception as e:
            return self._pass(f"API调用失败: {e}")

    def _check_ownership(self, artist: str, song: str) -> CheckResult:
        """Check if song belongs to the artist."""
        prompt = f"""请判断歌曲《{song}》是否为歌手"{artist}"的作品？
如果是该歌手的作品，回答"是"。
如果不是或不确定，回答"否"并说明原因。"""

        try:
            response = self.client.chat(prompt)
            if response.startswith("否") or "不是" in response:
                return self._fail(f"《{song}》非{artist}作品: {response}")
            return self._pass()
        except Exception as e:
            return self._pass(f"归属判断失败: {e}")
