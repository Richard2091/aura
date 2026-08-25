"""项目入口：根据配置启动自主感知 Agent。"""

from __future__ import annotations

import sys
# 统一标准输出为 UTF-8，避免 Windows 控制台 GBK 编码导致中文/emoji 报错
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


from aura.config import load_config
from aura.core.loop import AutonomousAgent
from aura.models.llm import OpenAICompatLLM
from aura.sensors.screen import ScreenSensor


def build_sensors(enabled: list[str]) -> list:
    """根据配置构建启用的传感器列表。

    @param enabled: 启用的感知源名称列表。
    @return: 传感器实例列表。
    """
    # 1. 按名称映射创建传感器，未知名称跳过
    sensors = []
    for name in enabled:
        if name == "screen":
            sensors.append(ScreenSensor())
        # 未来可在此扩展 camera / audio
    # 2. 返回已创建的传感器
    return sensors


def main() -> None:
    """启动 Agent 主程序。"""
    # 1. 加载配置
    config = load_config()
    # 2. 构建模型与传感器
    llm = OpenAICompatLLM(config.models.llm)
    sensors = build_sensors(config.sensors.enabled)
    # 3. 构建自主 Agent 并运行
    agent = AutonomousAgent(
        sensors=sensors,
        llm=llm,
        config=config.agent,
        self_model="一个主动感知电脑屏幕并思考是否回应的环境助手，懂得保持沉默。",
    )
    agent.run()


if __name__ == "__main__":
    # 4. 模块被直接执行时启动主程序
    main()

