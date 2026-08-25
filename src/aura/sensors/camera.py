"""摄像头感知源（占位，后续实现）。

规划：基于 OpenCV 采集摄像头画面，输出 Observation。
"""

from __future__ import annotations

from .base import Observation, Sensor


class CameraSensor(Sensor):
    """摄像头传感器（占位实现）。"""

    def __init__(self, interval: float = 1.0):
        self.interval = interval
        raise NotImplementedError("摄像头感知尚未实现，见 roadmap M5。")

    def capture(self) -> list[Observation]:
        raise NotImplementedError
