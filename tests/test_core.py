# -*- coding: utf-8 -*-
"""核心逻辑测试：验证「可沉默」是合法动作。"""

from aura.core.actions import Action, ActionKind
from aura.core.decide import Decider
from aura.core.world_state import WorldState
from aura.models.base import LLM
from aura.sensors.base import Observation


class _FakeLLM(LLM):
    """测试用假模型：决策阶段总是返回 noop。"""

    def generate(self, prompt: str, system: str | None = None) -> str:
        """返回 noop 决策，供测试验证。"""
        return '{"kind": "noop", "payload": "", "reason": "测试静默"}'

    def close(self) -> None:
        """无需释放。"""
        return None


def test_noop_is_valid_action():
    """验证 noop 是合法动作类型。"""
    # 1. 校验枚举定义
    assert ActionKind.NOOP.value == "noop"
    # 2. 构造一个 noop 动作
    action = Action(kind=ActionKind.NOOP, reason="保持沉默")
    assert action.kind == ActionKind.NOOP


def test_decider_returns_noop():
    """验证决策器在环境无需回应时产出 noop。"""
    # 1. 准备世界状态与假模型
    world = WorldState()
    world.update([Observation(source="mock", timestamp=0.0, text="环境很安静。")])
    decider = Decider(_FakeLLM())
    # 2. 决策
    action = decider.decide("环境平稳，保持沉默。", world)
    # 3. 断言
    assert action.kind == ActionKind.NOOP
