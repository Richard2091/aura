"""最小可沉默 Agent 演示。

不接真实传感器，用一个「模拟感知」提供环境变化，
验证核心逻辑：Agent 能思考，且能自主选择「不输出（noop）」。
运行前需本地有 OpenAI 兼容服务（如 Ollama / vLLM）或云端点。
"""

from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


import random

from aura.config import AgentConfig, load_config
from aura.core.actions import Action, ActionKind
from aura.core.loop import AutonomousAgent
from aura.models.base import LLM
from aura.sensors.base import Observation, Sensor

# 模拟的环境事件池（供感知源随机生成）
_EVENTS = [
    "屏幕显示：用户正在写代码。",
    "屏幕显示：桌面很安静，没有变化。",
    "屏幕显示：出现了一个新的提示窗口。",
    "屏幕显示：用户打开了浏览器。",
]


class MockSensor(Sensor):
    """模拟感知源：随机产生环境观测，用于无硬件演示。"""

    def capture(self) -> list[Observation]:
        """随机模拟一次环境观测。

        @return: 包含一条随机事件的观测列表。
        """
        # 1. 从事件池随机选一条
        text = random.choice(_EVENTS)
        # 2. 返回观测对象
        return [Observation(source="mock", timestamp=0.0, text=text)]


class MockLLM(LLM):
    """模拟语言模型：无需真模型即可验证循环逻辑。

    行为策略：遇到「安静」类事件倾向 noop，遇到「提示/浏览器」倾向 speak。
    """

    def generate(self, prompt: str, system: str | None = None) -> str:
        """生成模拟回复：思考阶段返回自然语言，决策阶段返回 JSON。

        @param prompt: 提示词。
        @param system: 系统提示词（忽略）。
        @return: 思考文本或决策 JSON。
        """
        # 1. 决策阶段：要求输出 JSON，返回结构化决策
        if "只能输出 JSON" in prompt or "动作中选择" in prompt:
            if "提示窗口" in prompt:
                return '{"kind": "speak", "payload": "检测到一个新的提示窗口，可能需要处理。", "reason": "环境变化值得关注"}'
            if "没有变化" in prompt or "安静" in prompt:
                return '{"kind": "noop", "payload": "", "reason": "环境无变化，无需回应"}'
            return '{"kind": "observe", "payload": "", "reason": "继续观察"}'
        # 2. 思考阶段：返回自然语言思考文本
        if "提示窗口" in prompt:
            return "检测到新的提示窗口，这可能是需要关注的变化，值得考虑是否回应。"
        if "没有变化" in prompt or "安静" in prompt:
            return "环境没有明显变化，当前无需采取行动，可以保持沉默继续观察。"
        return "环境平稳，先继续观察，暂不打扰。"

    def close(self) -> None:
        """无需释放资源。"""
        return None


def main() -> None:
    """运行模拟感知的可沉默 Agent 演示。"""
    # 1. 加载配置（可含真实模型配置），此处使用默认
    config = load_config()
    cfg = config.agent
    cfg.max_steps = 10  # 演示设定运行 10 轮

    # 2. 使用模拟感知源与模拟模型组装 Agent
    sensors = [MockSensor()]
    llm = MockLLM()

    agent = AutonomousAgent(
        sensors=sensors,
        llm=llm,
        config=cfg,
        self_model="一个会思考的演示 Agent，能判断何时保持沉默。",
    )

    # 3. 运行循环，观察 Agent 是否出现「不输出」轮次
    print("=" * 60)
    print(" 自主可沉默 Agent 演示（模拟感知 + 模拟模型）")
    print("=" * 60)
    agent.run()
    print("\n演示结束：注意观察是否有 AI 选择保持沉默（noop）的轮次。")


if __name__ == "__main__":
    # 4. 模块被直接执行时运行演示
    main()
