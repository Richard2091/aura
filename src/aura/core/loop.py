"""自主感知 Agent 主循环。

组织「感知 → 更新世界状态 → 思考 → 决策 → 行动/沉默」的完整循环，
并支持通过 noop 保持沉默（不产生对外副作用）。
"""

from __future__ import annotations

import time

from ..config import AgentConfig
from ..models.base import LLM
from ..sensors.base import Sensor
from .act import Actor
from .actions import Action, ActionKind
from .decide import Decider
from .reason import Reasoner
from .world_state import WorldState


class AutonomousAgent:
    """具备「可沉默」能力的环境感知 Agent。

    @param sensors: 传感器列表。
    @param llm: 语言模型。
    @param config: Agent 配置。
    @param self_model: 自我模型描述。
    """

    def __init__(self, sensors: list[Sensor], llm: LLM, config: AgentConfig, self_model: str = ""):
        # 1. 初始化各组件
        self.sensors = sensors
        self.world = WorldState()
        self.reasoner = Reasoner(llm)
        self.decider = Decider(llm)
        self.actor = Actor()
        self.config = config
        self.self_model = self_model

    def run(self) -> None:
        """启动自主循环，直到达到最大步数或收到中断信号。"""
        # 1. 记录起始时间与步数
        start = time.time()
        steps = 0
        try:
            # 2. 进入持续循环
            while steps < self.config.max_steps:
                # 2.1 感知：采集所有传感器观测
                observations = self._perceive()
                # 2.2 更新世界状态
                self.world.update(observations)
                # 2.3 思考
                thought = self.reasoner.reason(self.world, self.self_model)
                # 2.4 决策
                action = self.decider.decide(thought, self.world)
                # 2.5 执行（若为 noop/observe 则不产生副作用）
                self.actor.execute(action)
                # 2.6 输出本轮日志
                self._log(step=steps, thought=thought, action=action)
                # 2.7 按节拍等待
                steps += 1
                time.sleep(self.config.loop_interval)
        except KeyboardInterrupt:
            # 3. 被用户中断时优雅退出
            print("\n[停止] Agent 已结束（用户中断）。")

    def _perceive(self) -> list:
        """从所有启用的传感器采集观测。

        @return: 合并后的观测列表。
        """
        # 1. 遍历传感器采集，并允许单个传感器失败不影响整体
        results = []
        for sensor in self.sensors:
            try:
                obs = sensor.capture()
                if obs:
                    results.extend(obs)
            except Exception:
                continue
        # 2. 返回本轮全部观测
        return results

    def _log(self, step: int, thought: str, action: Action) -> None:
        """输出本轮运行日志。

        @param step: 当前循环步数。
        @param thought: 思考文本。
        @param action: 决策动作。
        """
        # 1. 打印步数与动作类型
        kind = action.kind.value
        print(f"\n[{step}] 动作类型 = {kind}  (reason: {action.reason})")
        # 2. 打印思考内容
        print(f"    思考：{thought}")
        # 3. 对 noop 做特殊提示，强调「可沉默」行为已发生
        if action.kind == ActionKind.NOOP:
            print("    （AI 选择保持沉默，未对外输出。）")

