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

        prompt = """请分析这些音乐MV画面（按顺序编号1-5），检查以下问题：
1. 画面是否有暴露内容（如过度裸露、色情暗示）
2. 画面是否有导向问题（如暴力、血腥、恐怖）
3. 画面是否只有风景（如纯粹的山水、天空、花草，没有人物或其他内容）
4. 画面是否包含广告（如品牌logo、产品推广、二维码）。注意：音乐平台logo不算广告（如酷狗、QQ音乐、网易云、酷我、咪咕等）
5. 画面是否有吸毒相关内容（如吸食毒品的动作、毒品道具）
6. 这明显不是音乐MV（如电影片段、综艺节目、新闻、教程、游戏视频等非音乐MV内容）

请按以下格式回答：
暴露:是/否
导向问题:是/否
纯风景:是/否
广告:是/否[如果是，说明：第X张，广告内容描述]
吸毒:是/否
非MV:是/否

只需按格式回答，不要解释。"""

        try:
            response = self.client.analyze_images(images, prompt)
            return self._parse_response(response)
        except Exception as e:
            return self._pass(f"API调用失败: {e}")

    def _parse_response(self, response: str) -> CheckResult:
        violations = []

        checks = [
            ("暴露", "画面暴露"),
            ("导向问题", "导向问题"),
            ("纯风景", "仅风景画背景"),
            ("吸毒", "含吸毒画面"),
            ("非MV", "非音乐MV内容"),
        ]

        for keyword, desc in checks:
            if f"{keyword}:是" in response or f"{keyword}：是" in response:
                violations.append(desc)

        # Special handling for ad detection with details
        import re
        ad_match = re.search(r"广告[:：]是[,，\[]?(.+?)(?:\n|$)", response)
        if ad_match:
            ad_detail = ad_match.group(1).strip().rstrip("]")
            violations.append(f"含广告内容({ad_detail})" if ad_detail else "含广告内容")
        elif "广告:是" in response or "广告：是" in response:
            violations.append("含广告内容")

        if violations:
            return self._fail(", ".join(violations))
        return self._pass()
