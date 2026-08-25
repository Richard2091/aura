"""模型抽象基类。

屏蔽本地推理后端差异（Ollama / vLLM / llama.cpp / transformers），
核心循环只需依赖 LLM / VisionModel 抽象，无需关心具体后端。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLM(ABC):
    """语言模型抽象接口。"""

    @abstractmethod
    def generate(self, prompt: str, system: str | None = None) -> str:
        """生成一段文本回复。

        @param prompt: 用户/任务提示词。
        @param system: 可选系统提示词。
        @return: 模型输出文本。
        """
        raise NotImplementedError  # pragma: no cover


class VisionModel(ABC):
    """视觉语言模型抽象接口（后续读屏升级用）。"""

    @abstractmethod
    def describe(self, image: Any, prompt: str) -> str:
        """描述一张图像。

        @param image: 图像对象（PIL Image 或路径）。
        @param prompt: 描述指令。
        @return: 图像的文字描述。
        """
        raise NotImplementedError  # pragma: no cover
