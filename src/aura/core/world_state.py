"""世界状态与记忆维护。

核心职责：接收每次感知观测，累积成一个持续更新的环境表征，
供推理层与决策层使用。这是「感知跨时间累积」而非一次性输入的关键。
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from ..sensors.base import Observation

# 短期记忆的最大条数
_DEFAULT_MEMORY_SIZE = 20


@dataclass
class WorldState:
    """持续维护的世界状态。

    @param observations: 最近若干条观测（短期记忆）。
    @param last_summary: 最近一次汇总后的文本描述。
    """

    observations: deque[Observation] = field(default_factory=lambda: deque(maxlen=_DEFAULT_MEMORY_SIZE))
    last_summary: str = ""

    def update(self, observations: list[Observation]) -> None:
        """把新一轮观测写入世界状态。

        @param observations: 本轮采集到的观测列表。
        """
        # 1. 将每条观测加入短期记忆
        for obs in observations:
            self.observations.append(obs)
        # 2. 汇总出最新的文本摘要
        self.last_summary = self._summarize()

    def _summarize(self) -> str:
        """把近期观测汇总为简洁文本。

        @return: 汇总文本，用于拼接进推理提示词。
        """
        # 1. 无观测时返回占位
        if not self.observations:
            return "(暂无环境观测)"
        # 2. 取最近数条观测的摘要拼接
        lines = [obs.summary() for obs in list(self.observations)[-5:]]
        return "\n".join(lines)

    def context(self) -> str:
        """输出当前可用于提示词的世界状态文本。

        @return: 世界上下文字符串。
        """
        # 1. 优先返回最近摘要，缺省时回退为观测数量说明
        if self.last_summary:
            return self.last_summary
        # 2. 摘要为空时的兜底文本
        return f"(世界状态：{len(self.observations)} 条观测，暂无文本摘要)"
