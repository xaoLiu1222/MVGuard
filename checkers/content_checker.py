from .base import BaseChecker, CheckResult
from services.video_processor import VideoProcessor
from services.siliconflow_api import SiliconFlowClient
from config import FRAME_SAMPLE_COUNT


class ContentChecker(BaseChecker):
    """Rules 4,5,6,7: Content analysis using VL model."""

    rule_id = 4
    rule_name = "内容合规检测"

    def __init__(self, client: SiliconFlowClient = None):
        self.client = client or SiliconFlowClient()
        self.processor = VideoProcessor()

    def check(self, video_path: str, **kwargs) -> CheckResult:
        frames = self.processor.extract_frames(video_path, FRAME_SAMPLE_COUNT)
        if not frames:
            return self._pass("无法提取帧")

        images = [self.processor.frame_to_base64(f) for f in frames]

        prompt = """请分析这些音乐MV画面，检查以下问题：
1. 画面是否有暴露内容（如过度裸露、色情暗示）
2. 画面是否有导向问题（如暴力、血腥、恐怖）
3. 画面是否只有风景（如纯粹的山水、天空、花草，没有人物或其他内容）
4. 画面是否包含广告（如品牌logo、产品推广、二维码）
5. 画面是否有吸毒相关内容（如吸食毒品的动作、毒品道具）

请按以下格式回答：
暴露:是/否
导向问题:是/否
纯风景:是/否
广告:是/否
吸毒:是/否

只需按格式回答，不要解释。"""

        try:
            response = self.client.analyze_images(images, prompt)
            return self._parse_response(response)
        except Exception as e:
            return self._pass(f"API调用失败: {e}")

    def _parse_response(self, response: str) -> CheckResult:
        violations = []

        checks = [
            ("暴露", "是", "画面暴露"),
            ("导向问题", "是", "导向问题"),
            ("纯风景", "是", "仅风景画背景"),
            ("广告", "是", "含广告内容"),
            ("吸毒", "是", "含吸毒画面"),
        ]

        for keyword, flag, desc in checks:
            if f"{keyword}:是" in response or f"{keyword}：是" in response:
                violations.append(desc)

        if violations:
            return self._fail(", ".join(violations))
        return self._pass()
