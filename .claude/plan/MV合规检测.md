# MV合规检测项目执行计划

## 项目概述
开发一个自动识别音乐MV是否合规的工具，基于8条审核规则进行检测。

## 技术栈
- Python 3.10+
- Gradio (Web界面)
- FFmpeg + OpenCV (视频处理)
- 硅基流动 Qwen3-VL-32B-Instruct (视觉分析)

## 8条审核规则
1. 林夕作词作曲 → 不合规
2. 竖屏/黑边 → 不合规
3. 音量突变 → 不合规
4. 画面暴露/导向问题 → 不合规
5. 仅风景画背景 → 不合规
6. 含广告内容 → 不合规
7. 含吸毒画面 → 不合规
8. 文件命名与内容不一致 → 不合规

## 项目结构
```
EarGuard/
├── app.py                    # Gradio主入口
├── config.py                 # 配置文件
├── requirements.txt          # 依赖
├── checkers/                 # 规则检测器
│   ├── base.py
│   ├── lyricist_checker.py
│   ├── aspect_checker.py
│   ├── audio_checker.py
│   ├── content_checker.py
│   └── naming_checker.py
├── services/
│   ├── video_processor.py
│   ├── siliconflow_api.py
│   └── report_generator.py
└── utils/
    └── file_utils.py
```

## 输入输出
- 输入：本地视频文件/文件夹 (.ts, .mp4, .mkv)
- 输出：CSV检测报告 + 不合规文件移动

## 执行状态
- [x] 项目结构搭建
- [x] 视频处理模块
- [x] 硅基流动API封装
- [x] 8条规则检测器
- [x] Gradio Web界面
- [ ] 集成测试
