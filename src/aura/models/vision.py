"""视觉语言模型占位（后续读屏升级用）。"""

from __future__ import annotations

from typing import Any

from .base import VisionModel


class PlaceholderVisionModel(VisionModel):
    """视觉模型占位实现。"""

    def describe(self, image: Any, prompt: str) -> str:
        raise NotImplementedError("视觉模型尚未接入，见 roadmap M3。")
