"""传感器抽象基类。

所有感知源（读屏、摄像头、语音）都实现 Sensor 接口，
核心循环只消费 Observation，从而做到感知源可插拔、可扩展。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Observation:
    """一次感知观测的统一数据结构。

    @param source: 感知来源标识，如 screen / camera / audio。
    @param timestamp: 观测时间戳（秒）。
    @param text: 文本描述（OCR / ASR 结果），可能为空。
    @param image: 可选图像帧或路径。
    @param metadata: 其它元信息，如帧率、区域、置信度。
    """

    source: str
    timestamp: float
    text: str | None = None
    image: Any | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        """生成面向推理层的简洁文本摘要。

        @return: 观测的文本摘要，便于拼接进提示词。
        """
        # 1. 优先使用文本内容，缺省时回退到元信息
        if self.text:
            return f"[{self.source}] {self.text}"
        # 2. 无文本时返回来源与元信息占位
        return f"[{self.source}] (no text, meta={self.metadata})"


class Sensor(ABC):
    """传感器抽象接口。

    子类需实现 capture()，返回当前时刻的一个或多个观测。
    """

    @abstractmethod
    def capture(self) -> list[Observation]:
        """采集当前时刻的一个或多个观测。

        @return: 观测列表（允许为空，表示本轮无有效感知）。
        """
        raise NotImplementedError  # pragma: no cover

    def close(self) -> None:
        """释放传感器资源。默认无操作，子类可按需覆盖。"""
        return None
