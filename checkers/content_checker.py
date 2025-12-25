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
            result = self._parse_response(response)

            # 二次确认：首次检测违规时，换角度再确认一次
            if not result.passed:
                confirm_result = self._confirm_violation(images, result.reason)
                if confirm_result.passed:
                    return self._pass()  # 二次确认通过，判定为合规
                return confirm_result
            return result
        except Exception as e:
            return self._pass(f"API调用失败: {e}")

    def _confirm_violation(self, images: list[str], violation: str) -> CheckResult:
        """二次确认违规内容"""
        prompt = f"""之前检测认为这些音乐MV画面存在问题："{violation}"

请重新仔细审视这些画面，判断上述问题是否真的存在。
注意：
- 正常的舞蹈动作、演唱表演不算暴露
- 艺术化的视觉效果不算导向问题
- 有歌手/演员出现的风景画面不算"纯风景"
- 音乐平台水印(酷狗、QQ音乐、网易云等)不算广告

请回答：上述问题是否确实存在？只回答"确认"或"误报"。"""

        try:
            response = self.client.analyze_images(images, prompt)
            if "误报" in response:
                return self._pass()
            return self._fail(violation)
        except:
            return self._fail(violation)

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
