"""动作定义与动作空间。

定义 Agent 可执行的动作集合，并显式包含「不动作 / 沉默」，
使保持沉默成为合法决策而非失败。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ActionKind(str, Enum):
    """动作类型枚举。"""

    SPEAK = "speak"  # 语言输出
    ACT = "act"  # 执行动作 / 调用工具
    OBSERVE = "observe"  # 继续观察
    NOOP = "noop"  # 保持沉默，不产生对外副作用


@dataclass
class Action:
    """一次决策产生的动作。

    @param kind: 动作类型。
    @param payload: 动作负载（说话文本 / 工具调用参数）。
    @param reason: 决策理由（供可解释性）。
    """

    kind: ActionKind
    payload: str = ""
    reason: str = ""


# 可被模型选择的所有动作类型（用于提示词约束）
AVAILABLE_ACTIONS = list(ActionKind)
