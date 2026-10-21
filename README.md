# AURA：自主环境感知 Agent

> **AURA** = **A**utonomous **U**nderstanding & **R**eactive **A**wareness（自主理解与响应性觉察）

一个面向「自主性」的最小实验项目：让 AI 不再被动等待人类指令，而是**主动感知环境、自主思考，并自主决定「说 / 做 / 还是保持沉默」**。

> 标语：**AURA · 在你不察觉时，它已看懂世界。**

> 核心主张：**不输出 ≠ 不思考**。思考可以持续进行，但对环境的副作用（说话、动作）是可选的、可被抑制的。

> 核心主张：**不输出 ≠ 不思考**。思考可以持续进行，但对环境的副作用（说话、动作）是可选的、可被抑制的。

> **v2 设计进行中**：加入决策模型、事件驱动感知和内心活动，见 [docs/v2](docs/v2/README.md)。

## 这是什么

本项目基于 **ReAct（Reasoning + Acting）** 范式，并做了关键扩展：在动作空间中显式引入 **`noop`（不动作 / 保持沉默）** 这个一等公民，使「想完可以不动、不说」成为合法且自然的决策，而非失败。

理想形态（目标）：

```
感知环境 → 更新世界状态 → 思考（关注什么？该不该回应？）
→ 决策（说 / 做 / 沉默）→ （可选）对外输出 → 观察结果 → 循环…
```

## 当前阶段（v0.1）

- ✅ 项目骨架与核心抽象
- ✅ 最小「感知 → 思考 → 决策 → 行动/沉默」循环
- ✅ **读屏**（screen）感知源（Windows OCR / 图像捕获）
- 🚧 后续：多视频源（摄像头等）扩展
- 🚧 后续：语音输入
- 🚧 后续：本地模型（本地 LLM / 视觉模型）接入

## 设计原则

1. **感知是主动流，不是被喂**：感知源持续提供输入，而非等待人类 prompt。
2. **行动发起权在模型**：是否输出由 agent 根据内在动机与环境判断，而非被强制要求响应。
3. **世界状态是核心**：维护一个持续更新的环境表征与记忆，让「感知」能跨时间累积。
4. **可扩展的传感器抽象**：读屏、摄像头、麦克风都实现同一接口，便于未来接入多路视频源。
5. **可静默**：`noop` 是合法动作，agent 可以自主选择不产生任何对外副作用。

## 目录结构

```
aura/
├── docs/                 # 设计与文档
│   ├── architecture.md   # 总体架构
│   ├── environment-perception.md  # 环境感知方案（读屏/多源/语音）
│   ├── agent-loop.md     # 自主决策循环（含 noop）
│   ├── local-model.md    # 本地模型选型与接入
│   └── roadmap.md        # 开发路线图
├── src/aura/
│   ├── core/             # 感知→世界状态→思考→决策→行动循环
│   ├── sensors/          # 传感器抽象与实现（screen/camera/audio）
│   ├── models/           # 模型抽象（本地 LLM/视觉）
│   └── main.py           # 入口
├── examples/             # 可直接运行的示例
├── tests/                # 单元测试
└── scripts/              # 辅助脚本（感知采集、演示）
```

## 快速开始

```bash
# 1. 创建虚拟环境
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行示例（先跑通「思考 → 可沉默」的逻辑，不接真实摄像头）
python examples/silent_agent_demo.py
```

## 运行测试

`ash
python -m pytest
`

## 文档

- [总体架构](docs/architecture.md)
- [环境感知方案](docs/environment-perception.md)
- [自主决策循环](docs/agent-loop.md)
- [本地模型选型](docs/local-model.md)
- [开发路线图](docs/roadmap.md)

## 许可证

MIT License
