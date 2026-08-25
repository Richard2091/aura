"""决策层：从动作空间中选择说 / 做 / 沉默。"""

from __future__ import annotations

import json
import re

from ..models.base import LLM
from .actions import Action, ActionKind, AVAILABLE_ACTIONS
from .world_state import WorldState


class Decider:
    """决策引擎：根据思考结果选择具体动作。

    @param llm: 语言模型实例。
    """

    def __init__(self, llm: LLM):
        # 1. 保存模型引用
        self.llm = llm

    def decide(self, thought: str, world: WorldState) -> Action:
        """根据思考结果与当前世界状态进行决策。

        @param thought: 思考层产出的文本。
        @param world: 当前世界状态。
        @return: 选定的动作。
        """
        # 1. 组装决策提示词，明确给出动作空间（含 noop）
        actions_desc = ", ".join(a.value for a in AVAILABLE_ACTIONS)
        prompt = (
            f"当前环境：\n{world.context()}\n\n"
            f"你的思考：\n{thought}\n\n"
            f"请从以下动作中选择一个并输出 JSON：\n"
            f'{{"kind": "{actions_desc}", "payload": "...", "reason": "..."}}\n'
            '规则：如果环境不需要你回应，kind 必须为 "noop"。\n'
            "只输出 JSON，不要额外文字。"
        )
        # 2. 调用模型，解析结果为结构化动作
        raw = self.llm.generate(prompt, system="你是决策器，输出严格 JSON。").strip()
        return self._parse(raw)

    def _parse(self, raw: str) -> Action:
        """解析模型输出的 JSON 为 Action 对象，失败时回退为 noop。

        @param raw: 模型原始输出文本。
        @return: 解析后的动作对象。
        """
        # 1. 从文本中提取 JSON 片段
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return Action(kind=ActionKind.NOOP, reason="解析失败，保持沉默")
        # 2. 解析 JSON 并校验动作类型
        try:
            data = json.loads(match.group(0))
            kind = ActionKind(data.get("kind", "noop"))
        except Exception:
            return Action(kind=ActionKind.NOOP, reason="解析失败，保持沉默")
        # 3. 组装并返回动作对象
        return Action(
            kind=kind,
            payload=str(data.get("payload", "")),
            reason=str(data.get("reason", "")),
        )
