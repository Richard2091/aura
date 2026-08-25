"""基于 OpenAI 兼容接口的语言模型实现。

Ollama / vLLM / llama.cpp 等本地后端均提供 /v1/chat/completions，
因此统一通过 openai SDK 访问，只需替换 base_url 与 model 名。
"""

from __future__ import annotations

from ..config import EndpointConfig
from .base import LLM


class OpenAICompatLLM(LLM):
    """使用 OpenAI 兼容接口调用本地/远程语言模型。

    @param config: 模型配置对象。
    """

    def __init__(self, config: EndpointConfig):
        # 1. 保存配置
        self.config = config
        # 2. 延迟导入 openai，避免未安装时影响其它功能
        from openai import OpenAI  # type: ignore

        self._client = OpenAI(base_url=config.base_url, timeout=config.timeout)

    def generate(self, prompt: str, system: str | None = None) -> str:
        """调用模型生成文本。

        @param prompt: 用户提示词。
        @param system: 可选系统提示词。
        @return: 模型输出文本。
        """
        # 1. 组装消息列表
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        # 2. 发起对话补全请求
        resp = self._client.chat.completions.create(
            model=self.config.model,
            messages=messages,
        )
        # 3. 返回首个候选文本
        return resp.choices[0].message.content or ""

