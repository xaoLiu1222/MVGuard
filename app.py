"""
EarGuard - 音乐MV合规性检测工具
Usage: python app.py
"""
import gradio as gr
from datetime import datetime

from config import SILICONFLOW_API_KEY, SILICONFLOW_VL_MODELS
from services.siliconflow_api import SiliconFlowClient
from services.report_generator import ReportGenerator
from utils.file_utils import get_video_files, move_file, ensure_dir
from utils.profiles import load_profiles, save_profile, delete_profile, get_profile_choices
from checkers import (
    LyricistChecker,
    AspectChecker,
    ContentChecker,
    NamingChecker,
    DurationChecker,
    ResolutionChecker,
    StaticChecker,
)


class MVComplianceChecker:
    """Main checker that runs all rules."""

    def __init__(self, api_key: str, model: str = None):
        client = SiliconFlowClient(api_key, model)
        self.checkers = [
            LyricistChecker(client),
            AspectChecker(),
            ContentChecker(client),
            NamingChecker(client),
            DurationChecker(client),
            ResolutionChecker(),
            StaticChecker(),
        ]

    def check_video(self, video_path: str) -> dict:
        """Run all checks on a single video."""
        violated = []
        for checker in self.checkers:
            result = checker.check(video_path)
            if not result.passed:
                violated.append(f"规则{result.rule_id}: {result.reason}")

        is_compliant = len(violated) == 0
        return ReportGenerator.create_result(
            video_path,
            is_compliant,
            violated,
            "; ".join(violated) if violated else "通过所有检测"
        )


def process_videos(input_path: str, compliant_path: str, non_compliant_path: str, api_key: str, model: str):
    """Process videos and yield results in real-time."""
    if not api_key:
        yield "❌ 错误：请输入硅基流动API密钥", [], None
        return
    if not input_path:
        yield "❌ 错误：请选择视频文件或文件夹", [], None
        return

    videos = get_video_files(input_path)
    if not videos:
        yield "❌ 错误：未找到支持的视频文件(.ts, .mp4, .mkv)", [], None
        return

    # Setup directories (default to source dir if not specified)
    from pathlib import Path
    video_parent = Path(videos[0]).parent
    comp_dir = ensure_dir(compliant_path) if compliant_path else ensure_dir(video_parent / "合规")
    non_comp_dir = ensure_dir(non_compliant_path) if non_compliant_path else ensure_dir(video_parent / "不合规")

    checker = MVComplianceChecker(api_key, model)
    results = []
    total = len(videos)

    for idx, video in enumerate(videos, 1):
        result = checker.check_video(str(video))
        results.append(result)

        # Move file based on result
        if result["status"] == "合规":
            move_file(str(video), str(comp_dir))
        else:
            move_file(str(video), str(non_comp_dir))
        result["details"] += " [已移动]"

        # Build real-time summary
        passed = sum(1 for r in results if r["status"] == "合规")
        failed = len(results) - passed
        summary = f"⏳ 检测进度: {idx}/{total}\n\n📊 当前统计\n• 合规: {passed} 个 ✓\n• 不合规: {failed} 个 ✗"

        # Build table
        table_data = [[r["filename"], "✅ 合规" if r["status"] == "合规" else "❌ 不合规", r["violated_rules"], r["details"]] for r in results]

        yield summary, table_data, None

    # Generate final report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"检测报告_{timestamp}.csv"
    ReportGenerator.generate_csv(results, report_path)

    passed = sum(1 for r in results if r["status"] == "合规")
    final_summary = f"✅ 检测完成！\n\n📊 统计结果\n• 总计: {total} 个视频\n• 合规: {passed} 个 ✓\n• 不合规: {total - passed} 个 ✗\n\n📁 报告已保存: {report_path}"

    yield final_summary, table_data, report_path


def create_ui():
    """Create Gradio interface with improved UX."""

    custom_css = """
    .header-title {font-size: 28px; font-weight: 700; color: #1e293b; margin-bottom: 4px;}
    .header-subtitle {font-size: 14px; color: #64748b;}
    .rule-item {padding: 10px 12px; border-left: 3px solid #3b82f6; margin: 6px 0; background: #f8fafc; border-radius: 0 6px 6px 0;}
    .rule-item b {color: #1e40af;}
    .config-section {background: #ffffff; border-radius: 12px; padding: 16px;}
    """

    def on_profile_select(profile_name):
        """Load selected profile."""
        if not profile_name:
            return SILICONFLOW_API_KEY, SILICONFLOW_VL_MODELS[0]
        for p in load_profiles():
            if p["name"] == profile_name:
                return p["api_key"], p["model"]
        return SILICONFLOW_API_KEY, SILICONFLOW_VL_MODELS[0]

    def on_save_profile(name, api_key, model):
        """Save current config as profile."""
        if not name:
            return gr.update(), "❌ 请输入配置名称"
        save_profile(name, api_key, model)
        return gr.update(choices=get_profile_choices(), value=name), f"✅ 已保存配置: {name}"

    def on_delete_profile(name):
        """Delete selected profile."""
        if not name:
            return gr.update(), "❌ 请选择要删除的配置"
        delete_profile(name)
        return gr.update(choices=get_profile_choices(), value=None), f"✅ 已删除配置: {name}"

    with gr.Blocks(title="MVGuard - MV合规检测", css=custom_css) as app:

        # Header
        gr.HTML('<div class="header-title">🎵 MVGuard - 音乐MV合规性检测工具</div>')
        gr.HTML('<div class="header-subtitle">专业视频内容审核平台 · 8项智能检测规则 · 支持批量处理</div>')
        gr.HTML('<hr style="margin: 16px 0; border: none; border-top: 1px solid #e2e8f0;">')

        with gr.Row():
            # 左侧配置区
            with gr.Column(scale=2):
                with gr.Group():
                    gr.Markdown("### 📋 检测配置")
                    with gr.Row():
                        profile_select = gr.Dropdown(
                            label="📂 已保存配置",
                            choices=get_profile_choices(),
                            value=None,
                            allow_custom_value=False,
                            scale=2
                        )
                        profile_name = gr.Textbox(label="配置名称", placeholder="输入名称保存当前配置", scale=2)
                        save_btn = gr.Button("💾 保存", scale=1)
                        del_btn = gr.Button("🗑️ 删除", scale=1)
                    profile_status = gr.Textbox(label="", visible=True, interactive=False, max_lines=1)

                    api_key = gr.Textbox(
                        label="🔑 硅基流动API密钥",
                        type="password",
                        value=SILICONFLOW_API_KEY,
                        placeholder="sk-xxxxxxxxxxxxxxxx",
                        info="用于AI视觉内容检测"
                    )
                    model_select = gr.Dropdown(
                        label="🤖 视觉模型",
                        choices=SILICONFLOW_VL_MODELS,
                        value=SILICONFLOW_VL_MODELS[0],
                        allow_custom_value=True,
                        info="选择或输入自定义模型"
                    )
                    input_path = gr.Textbox(
                        label="📁 视频路径",
                        placeholder="/home/user/videos 或 /home/user/video.mp4",
                        info="支持 .ts .mp4 .mkv 格式，可输入文件夹批量处理"
                    )
                    with gr.Row():
                        compliant_dir = gr.Textbox(
                            label="📂 合规文件目录",
                            placeholder="留空则在源目录创建'合规'文件夹",
                        )
                        non_compliant_dir = gr.Textbox(
                            label="📂 不合规文件目录",
                            placeholder="留空则在源目录创建'不合规'文件夹",
                        )

                btn = gr.Button("🚀 开始检测", variant="primary", size="lg")

            # 右侧规则区
            with gr.Column(scale=1):
                gr.Markdown("### 📊 检测规则")
                gr.HTML("""
<div class="rule-item">✓ <b>规则1</b> 林夕作词作曲</div>
<div class="rule-item">✓ <b>规则2</b> 竖屏/黑边>50%</div>
<div class="rule-item">✓ <b>规则4</b> 画面暴露/导向问题</div>
<div class="rule-item">✓ <b>规则5</b> 仅风景画背景</div>
<div class="rule-item">✓ <b>规则6</b> 含广告内容(不含音乐平台)</div>
<div class="rule-item">✓ <b>规则7</b> 含吸毒画面</div>
<div class="rule-item">✓ <b>规则8</b> 文件命名不一致</div>
<div class="rule-item">✓ <b>规则9</b> 非音乐MV内容</div>
<div class="rule-item">✓ <b>规则10</b> 时长>4分40秒/无歌词</div>
<div class="rule-item">✓ <b>规则11</b> 清晰度低于超清</div>
<div class="rule-item">✓ <b>规则12</b> 静态画面/动态壁纸</div>
                """)

        gr.HTML('<hr style="margin: 20px 0; border: none; border-top: 1px solid #e2e8f0;">')

        # 结果区
        gr.Markdown("### 📈 检测结果")
        summary = gr.Textbox(label="结果摘要", lines=6, show_label=False)

        results_table = gr.Dataframe(
            headers=["文件名", "状态", "违规规则", "详情"],
            label="详细结果",
            wrap=True,
            column_widths=["25%", "12%", "20%", "43%"]
        )

        report_file = gr.File(label="📥 下载CSV报告")

        # Event handlers
        profile_select.change(on_profile_select, inputs=[profile_select], outputs=[api_key, model_select])
        save_btn.click(on_save_profile, inputs=[profile_name, api_key, model_select], outputs=[profile_select, profile_status])
        del_btn.click(on_delete_profile, inputs=[profile_select], outputs=[profile_select, profile_status])

        btn.click(
            fn=process_videos,
            inputs=[input_path, compliant_dir, non_compliant_dir, api_key, model_select],
            outputs=[summary, results_table, report_file]
        )

    return app


if __name__ == "__main__":
    app = create_ui()
    app.launch(server_name="0.0.0.0", server_port=7860)
