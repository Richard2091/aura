"""行动与表达层：执行对环境的副效用动作。"""

from __future__ import annotations

import json

from .actions import Action, ActionKind


class Actor:
    """动作执行器：把决策结果落到外部副作用。"""

    def execute(self, action: Action) -> str:
        """执行一个动作，返回执行结果描述。

        @param action: 待执行动作。
        @return: 执行结果文本，供记录/反馈。
        """
        # 1. 按动作类型分发处理
        if action.kind == ActionKind.SPEAK:
            return self._speak(action.payload)
        if action.kind == ActionKind.ACT:
            return self._act(action.payload)
        # 2. 其它动作（observe/noop）不产生外部副作用
        return f"[静默] reason={action.reason}"

    def _speak(self, payload: str) -> str:
        """输出一段语言表达。

        @param payload: 要说的话。
        @return: 输出结果文本。
        """
        # 1. 实际环境可接 TTS / 日志；当前打印到 stdout
        print(f"\n[AI说话] {payload}")
        return f"speak: {payload}"

    def _act(self, payload: str) -> str:
        """执行一个动作（预留工具调用）。

        @param payload: 工具调用参数（JSON 字符串）。
        @return: 执行结果文本。
        """
        # 1. 尝试解析工具调用参数
        try:
            data = json.loads(payload)
            tool = data.get("tool", "unknown")
            args = data.get("args", {})
        except Exception:
            tool, args = "unknown", {}
        # 2. 当前为占位实现，仅打印；后续可接 API/机器人
        print(f"\n[AI行动] tool={tool} args={args}")
        return f"act: {tool}"

