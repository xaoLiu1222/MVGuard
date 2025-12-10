"""
EarGuard - 音乐MV合规性检测工具
Usage: python app.py
"""
import gradio as gr
from datetime import datetime

from config import SILICONFLOW_API_KEY
from services.siliconflow_api import SiliconFlowClient
from services.report_generator import ReportGenerator
from utils.file_utils import get_video_files, move_file, ensure_dir
from checkers import (
    LyricistChecker,
    AspectChecker,
    AudioChecker,
    ContentChecker,
    NamingChecker,
)


class MVComplianceChecker:
    """Main checker that runs all rules."""

    def __init__(self, api_key: str):
        client = SiliconFlowClient(api_key)
        self.checkers = [
            LyricistChecker(client),   # Rule 1
            AspectChecker(),            # Rule 2
            AudioChecker(),             # Rule 3
            ContentChecker(client),     # Rules 4,5,6,7
            NamingChecker(client),      # Rule 8
        ]

    def check_video(self, video_path: str) -> dict:
        """Run all checks on a single video."""
        results = []
        violated = []

        for checker in self.checkers:
            result = checker.check(video_path)
            results.append(result)
            if not result.passed:
                violated.append(f"规则{result.rule_id}: {result.reason}")

        is_compliant = len(violated) == 0
        return ReportGenerator.create_result(
            video_path,
            is_compliant,
            violated,
            "; ".join(violated) if violated else "通过所有检测"
        )


def process_videos(
    input_path: str,
    output_dir: str,
    api_key: str,
    progress=gr.Progress()
) -> tuple[str, str]:
    """Process videos and return results."""
    if not api_key:
        return "错误：请输入硅基流动API密钥", ""

    if not input_path:
        return "错误：请选择视频文件或文件夹", ""

    videos = get_video_files(input_path)
    if not videos:
        return "错误：未找到支持的视频文件(.ts, .mp4, .mkv)", ""

    checker = MVComplianceChecker(api_key)
    results = []
    non_compliant_dir = ensure_dir(output_dir) if output_dir else None

    for video in progress.tqdm(videos, desc="检测中"):
        result = checker.check_video(str(video))
        results.append(result)

        # Move non-compliant files
        if result["status"] == "不合规" and non_compliant_dir:
            move_file(str(video), str(non_compliant_dir))
            result["details"] += f" [已移动到 {non_compliant_dir}]"

    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"检测报告_{timestamp}.csv"
    ReportGenerator.generate_csv(results, report_path)

    # Format summary
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "合规")
    failed = total - passed

    summary = f"""检测完成！
- 总计: {total} 个视频
- 合规: {passed} 个
- 不合规: {failed} 个
- 报告已保存: {report_path}"""

    # Format table
    table_data = [[r["filename"], r["status"], r["violated_rules"], r["details"]] for r in results]

    return summary, table_data, report_path


def create_ui():
    """Create Gradio interface."""
    with gr.Blocks(title="EarGuard - MV合规检测", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🎵 EarGuard - 音乐MV合规性检测工具")
        gr.Markdown("自动检测MV是否符合8条审核规则")

        with gr.Row():
            with gr.Column(scale=2):
                api_key = gr.Textbox(
                    label="硅基流动API密钥",
                    type="password",
                    value=SILICONFLOW_API_KEY,
                    placeholder="sk-xxx"
                )
                input_path = gr.Textbox(
                    label="视频路径",
                    placeholder="输入视频文件路径或文件夹路径"
                )
                output_dir = gr.Textbox(
                    label="不合规文件移动目录",
                    placeholder="留空则不移动文件"
                )
                btn = gr.Button("🚀 开始检测", variant="primary")

            with gr.Column(scale=1):
                gr.Markdown("""### 检测规则
1. 林夕作词作曲 ❌
2. 竖屏/黑边 ❌
3. 音量突变 ❌
4. 画面暴露/导向问题 ❌
5. 仅风景画背景 ❌
6. 含广告内容 ❌
7. 含吸毒画面 ❌
8. 文件命名不一致 ❌""")

        summary = gr.Textbox(label="检测结果摘要", lines=5)

        results_table = gr.Dataframe(
            headers=["文件名", "状态", "违规规则", "详情"],
            label="检测详情"
        )

        report_file = gr.File(label="下载CSV报告")

        btn.click(
            fn=process_videos,
            inputs=[input_path, output_dir, api_key],
            outputs=[summary, results_table, report_file]
        )

    return app


if __name__ == "__main__":
    app = create_ui()
    app.launch(server_name="0.0.0.0", server_port=7860)
