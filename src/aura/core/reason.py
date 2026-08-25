"""思考层：结合世界状态与自我模型，判断当前应当关注什么。"""

from __future__ import annotations

from ..models.base import LLM
from .world_state import WorldState


class Reasoner:
    """推理引擎：根据世界状态生成「我该关注什么 / 是否值得回应」的判断。

    @param llm: 语言模型实例。
    """

    def __init__(self, llm: LLM):
        # 1. 保存模型引用
        self.llm = llm

    def reason(self, world: WorldState, self_model: str = "") -> str:
        """基于当前世界状态进行思考。

        @param world: 当前世界状态。
        @param self_model: 自我模型描述（我是谁 / 我要成为什么）。
        @return: 思考文本（关注点与意向）。
        """
        # 1. 组装提示词：包含环境上下文与自我模型
        prompt = (
            f"当前环境观测：\n{world.context()}\n\n"
            f"你的自我定位：{self_model or '一个自主环境感知助手'}\n\n"
            "请思考：此刻有什么值得你关注？是否值得对外回应？"
            "如果环境没有需要你处理的事情，就明确表示保持沉默。"
        )
        # 2. 调用模型生成思考
        return self.llm.generate(prompt).strip()
