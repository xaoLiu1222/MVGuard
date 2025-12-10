# MVGuard

音乐MV合规性自动检测工具，基于视觉AI模型进行内容审核。

## 功能特性

- 🎵 支持 `.ts`, `.mp4`, `.mkv` 视频格式
- 📁 支持单文件和批量文件夹处理
- 🤖 集成硅基流动 Qwen3-VL 视觉模型
- 📊 自动生成CSV检测报告
- 📂 自动移动不合规文件
- 🌐 Gradio Web界面

## 检测规则

| # | 规则 | 检测方式 |
|---|------|----------|
| 1 | 林夕作词作曲 | OCR识别 |
| 2 | 竖屏/黑边 | 视频分析 |
| 3 | 音量突变 | 音频分析 |
| 4 | 画面暴露/导向问题 | VL模型 |
| 5 | 仅风景画背景 | VL模型 |
| 6 | 含广告内容 | VL模型 |
| 7 | 含吸毒画面 | VL模型 |
| 8 | 文件命名不一致 | OCR对比 |

## 安装

```bash
# 克隆项目
git clone https://github.com/YOUR_USERNAME/MVGuard.git
cd MVGuard

# 安装依赖
pip install -r requirements.txt

# 安装FFmpeg (Ubuntu/Debian)
sudo apt install ffmpeg
```

## 使用

```bash
# 设置API密钥（可选）
export SILICONFLOW_API_KEY="sk-xxx"

# 启动Web界面
python app.py

# 访问 http://localhost:7860
```

## 配置

编辑 `config.py` 修改：
- API密钥
- 检测阈值
- 支持的视频格式

## License

MIT
