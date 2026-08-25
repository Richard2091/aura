"""语音输入感知源（占位，后续实现）。

规划：采集麦克风音频，本地 ASR 转写为文本观测。
"""

from __future__ import annotations

from .base import Observation, Sensor


class AudioSensor(Sensor):
    """语音输入传感器（占位实现）。"""

    def __init__(self, interval: float = 1.0):
        self.interval = interval
        raise NotImplementedError("语音感知尚未实现，见 roadmap M5。")

    def capture(self) -> list[Observation]:
        raise NotImplementedError
