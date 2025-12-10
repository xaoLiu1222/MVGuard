# EarGuard Configuration
import os

# SiliconFlow API
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1"
SILICONFLOW_MODEL = "Qwen/Qwen2.5-VL-32B-Instruct"

# Video Processing
SUPPORTED_FORMATS = [".ts", ".mp4", ".mkv"]
FRAME_SAMPLE_COUNT = 5  # Number of frames to sample for content analysis
AUDIO_CHUNK_DURATION = 1.0  # seconds

# Detection Thresholds
BLACK_BORDER_THRESHOLD = 0.15  # 15% black pixels considered as border
AUDIO_SPIKE_THRESHOLD = 3.0  # Standard deviations for volume spike
ASPECT_RATIO_VERTICAL = 1.0  # Width/Height < 1 is vertical

# File Naming
EXPECTED_NAME_FORMAT = "{artist}-{song}"  # Expected: artist-song.ext
