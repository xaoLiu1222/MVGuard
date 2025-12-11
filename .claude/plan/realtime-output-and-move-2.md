# MVGuard 功能增强实施规划文档 v3

## 1. 目标定义

### 1.1 需求概述
| 需求编号 | 需求描述 |
|---------|---------|
| REQ-01 | 每审查完一个视频后在UI界面实时输出审查结果 |
| REQ-02 | 默认移动文件，合规/不合规分别移动到对应目录 |
| REQ-03 | 若未指定目录，在视频源目录下自动创建子目录 |

### 1.2 目标状态

- 每完成一个视频检测，UI 立即显示结果
- **默认行为**：检测完成后自动移动文件
- 未指定目录时，在视频所在目录下创建 `合规` 和 `不合规` 子目录

---

## 2. 实施步骤

### 步骤 1: 修改 UI（app.py）

- 添加"合规文件移动目录"输入框
- 修改 placeholder 提示：留空则自动在源目录创建

### 步骤 2: 修改 process_videos 函数（app.py）

```python
# 目录处理逻辑
video_parent = Path(videos[0]).parent
compliant_dir = ensure_dir(compliant_path) if compliant_path else ensure_dir(video_parent / "合规")
non_compliant_dir = ensure_dir(non_compliant_path) if non_compliant_path else ensure_dir(video_parent / "不合规")

# 文件移动（每个视频检测完后）
if result["status"] == "合规":
    move_file(str(video), str(compliant_dir))
else:
    move_file(str(video), str(non_compliant_dir))
```

### 步骤 3: 改为 generator 实现实时输出

每处理完一个视频 `yield` 当前结果

---

## 3. 验收标准

| 测试项 | 验收标准 |
|-------|---------|
| 实时输出 | 每完成一个视频，UI 立即更新 |
| 默认移动 | 不指定目录时自动创建并移动 |
| 自定义目录 | 指定目录时移动到指定位置 |
| 目录命名 | 自动创建的目录名为"合规"和"不合规" |
