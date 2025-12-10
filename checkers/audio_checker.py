import numpy as np
from .base import BaseChecker, CheckResult
from services.video_processor import VideoProcessor
from config import AUDIO_SPIKE_THRESHOLD


class AudioChecker(BaseChecker):
    """Rule 3: Reject if audio has sudden volume spikes."""

    rule_id = 3
    rule_name = "音量突变检测"

    def __init__(self):
        self.processor = VideoProcessor()

    def check(self, video_path: str, **kwargs) -> CheckResult:
        levels = self.processor.extract_audio_levels(video_path)

        if len(levels) < 10:
            return self._pass("音频数据不足")

        arr = np.array(levels)
        mean, std = arr.mean(), arr.std()

        if std == 0:
            return self._pass()

        # Detect spikes (values beyond threshold * std from mean)
        spikes = np.abs(arr - mean) > AUDIO_SPIKE_THRESHOLD * std

        if spikes.any():
            spike_count = spikes.sum()
            return self._fail(f"检测到{spike_count}处音量突变")

        return self._pass()
