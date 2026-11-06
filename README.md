# AURA：自主环境感知 Agent

> **AURA** = **A**utonomous **U**nderstanding & **R**eactive **A**wareness（自主理解与响应性觉察）

一个面向「自主性」的最小实验项目：让 AI 不再被动等待人类指令，而是**主动感知环境、自主思考，并自主决定「说 / 做 / 还是保持沉默」**。

> 标语：**AURA · 在你不察觉时，它已看懂世界。**

> 核心主张：**不输出 ≠ 不思考**。思考可以持续进行，但对环境的副作用（说话、动作）是可选的、可被抑制的。

> **当前代码是 v0.1，v2 尚在设计阶段**。先读 [demo 能力边界与完成标准](docs/v2/demo-capability.md)，再读 [实施契约](docs/v2/demo.md)；[v2 文档入口](docs/v2/README.md) 区分长期目标与本次交付。

v2 计划验证：在至少两类应用上，以本地感知和决策发现帮助机会，按需思考，等断点表达，采纳后给出具体建议。先做可回放骨架，再做真实闭环，最终达到可在本人电脑上试用的实验原型。动作执行、长期学习、全软件覆盖暂不属于这次 demo。

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
- ✅ 屏幕截图感知源；OCR 为可选的 `pytesseract` 路径，需另装引擎与语言包，默认依赖安装不保证可读正文
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

## 快速开始（现有 v1 模拟示例）

以下示例使用模拟感知和模拟模型，不需要密钥或真实模型，也不证明 v2 已实现。Windows PowerShell：

```powershell
# 选择本机已安装且依赖兼容的 Python（示例为 3.10）
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe examples/silent_agent_demo.py
```

macOS / Linux 使用 `python3 -m venv .venv` 创建环境，再用 `.venv/bin/python` 执行相同的安装和示例命令。v2 的回放命令、客户端和真实模型配置均为待实现内容，见实施契约。

## 运行测试

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## 文档

- [v2 文档入口](docs/v2/README.md)
- [demo 做到什么程度](docs/v2/demo-capability.md)
- [demo 实施契约](docs/v2/demo.md)
- [长期设计](docs/v2/design.md)
- [调研与待核验线索](docs/v2/research.md)

以下是 v1 历史设计，部分接口与路线已过时；v2 规划以以上文档为准。

- [总体架构](docs/architecture.md)
- [环境感知方案](docs/environment-perception.md)
- [自主决策循环](docs/agent-loop.md)
- [本地模型选型](docs/local-model.md)
- [开发路线图](docs/roadmap.md)

## 许可证

MIT License
