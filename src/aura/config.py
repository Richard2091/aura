"""集中式配置管理与加载。

支持从 config.yaml 读取运行时配置，并提供合理的默认值，
避免在业务代码中硬编码模型地址、采样间隔等参数。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# 默认配置文件的查找顺序：环境变量指定 > 项目根目录 > 包内默认
_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config.yaml"


@dataclass
class EndpointConfig:
    """单个模型后端的连接配置。"""

    backend: str = "ollama"  # 推理后端：ollama / llamacpp / vllm / transformers
    base_url: str = "http://localhost:11434/v1"  # OpenAI 兼容服务地址
    model: str = "qwen2.5:7b"  # 模型名
    timeout: float = 60.0  # 单次推理超时（秒）


@dataclass
class ModelConfig:
    """模型相关配置（llm / vision 等子后端）。"""

    llm: EndpointConfig = field(default_factory=EndpointConfig)
    vision: EndpointConfig | None = field(default=None)  # 视觉模型，可选


@dataclass
class SensorConfig:
    """传感器相关配置。"""

    enabled: list[str] = field(default_factory=lambda: ["screen"])  # 启用的传感源
    screen_interval: float = 2.0  # 屏幕采样间隔（秒）
    camera_interval: float = 1.0  # 摄像头采样间隔（秒）


@dataclass
class AgentConfig:
    """Agent 主循环配置。"""

    loop_interval: float = 3.0  # 主循环节拍（秒）
    max_steps: int = 50  # 单次会话最大循环步数
    system_prompt: str = (
        "你是一个具备自主性的环境感知助手。"
        "你会持续观察环境并思考，但并非每次都要对外回应。"
        "只有当环境确实需要你时才表态，否则保持沉默。"
    )


@dataclass
class AppConfig:
    """应用级配置聚合。"""

    models: ModelConfig = field(default_factory=ModelConfig)
    sensors: SensorConfig = field(default_factory=SensorConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)


def _deep_update(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """递归合并配置字典：override 优先于 base。"""
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = _deep_update(base[key], value)
        else:
            base[key] = value
    return base


def _build_endpoint(raw: dict[str, Any]) -> EndpointConfig:
    """从字典构建一个后端连接配置。

    @param raw: 后端配置字典。
    @return: 端点配置对象。
    """
    # 1. 只保留 EndpointConfig 声明的字段，避免多余键报错
    allowed = {f for f in EndpointConfig.__dataclass_fields__}
    kwargs = {k: v for k, v in raw.items() if k in allowed}
    # 2. 返回端点配置
    return EndpointConfig(**kwargs)


def load_config(path: str | Path | None = None) -> AppConfig:
    """从 YAML 文件加载配置并转换为 AppConfig。

    @param path: 配置文件路径，默认使用项目根目录 config.yaml。
    @return: 解析后的应用配置对象。
    """
    # 1. 确定配置文件路径：优先显式传入，其次项目根目录，最后包内默认
    config_path = Path(path) if path else _DEFAULT_CONFIG_PATH
    if not config_path.exists():
        config_path = Path(__file__).resolve().parent / "config.default.yaml"

    # 2. 读取 YAML 内容（文件不存在时使用空字典）
    raw: dict[str, Any] = {}
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            parsed = yaml.safe_load(f) or {}
            raw = _deep_update(raw, parsed)

    # 3. 构建模型配置：llm 必填，vision 可选
    models_raw = raw.get("models", {})
    llm_cfg = _build_endpoint(models_raw.get("llm", {}))
    vision_raw = models_raw.get("vision")
    vision_cfg = _build_endpoint(vision_raw) if vision_raw else None
    model_cfg = ModelConfig(llm=llm_cfg, vision=vision_cfg)

    # 4. 构建传感器与 Agent 配置
    sensors_raw = raw.get("sensors", {})
    agent_raw = raw.get("agent", {})
    sensor_cfg = SensorConfig(**{k: v for k, v in sensors_raw.items() if k in SensorConfig.__dataclass_fields__})
    agent_cfg = AgentConfig(**{k: v for k, v in agent_raw.items() if k in AgentConfig.__dataclass_fields__})

    # 5. 返回聚合后的配置对象
    return AppConfig(models=model_cfg, sensors=sensor_cfg, agent=agent_cfg)
