# 本地模型选型与接入

## 1. 为什么用本地模型

- **隐私**：感知的是用户屏幕/环境，应默认本地处理。
- **离线**：不依赖网络，稳定可控。
- **成本可控**：长期运行、持续循环，云端 API 代价高。
- **可定制**：可针对本任务做量化、裁剪、微调。

## 2. 推理后端选型

| 后端 | 适合 | 说明 |
|---|---|---|
| **Ollama** | 快速起步、LLM | 一条命令拉起，OpenAI 兼容接口，易于集成 |
| **llama.cpp** | 低资源、量化 | CPU/GPU 都能跑，GGUF 量化 |
| **vLLM** | 高吞吐、多并发 | 适合本地做服务，OpenAI 兼容 |
| **transformers + torch** | 实验/自定义 | 最灵活，可做 VLM（视觉语言模型） |

**推荐**：MVP 用 **Ollama**（或 llama.cpp）跑 LLM；后续读屏升级 VLM 时用 **transformers / Ollama 的视觉模型**。

## 3. 本地模型角色划分

本项目主要需要两类本地模型能力：

### 3.1 文本推理（LLM）
负责「思考」「决策」「说话内容规划」。
- 建议模型：`Qwen2.5-7B-Instruct` / `Llama-3.1-8B-Instruct` / `Mistral-7B`。
- 大小：7B 量化后（Q4）约 4~5 GB，普通显卡/16G 内存可跑。

### 3.2 视觉理解（VLM，可选/后续）
负责理解屏幕/摄像头画面内容。
- 建议模型：`Qwen2.5-VL-7B`、`InternVL2`、`LLaVA` 等。
- 读屏初期可先用 **OCR（tesseract / Windows OCR）** 降低门槛，再平滑升级到 VLM。

### 3.3 语音（后续）
- ASR：`faster-whisper` 本地转写。
- TTS：`edge-tts` / `piper` / `kokoro`。

## 4. 模型抽象接口

屏蔽后端差异，核心循环只依赖抽象：

```python
class LLM:
    """本地语言模型抽象。"""
    def generate(self, prompt: str, system: str | None = None) -> str:
        ...

class VisionModel:
    """本地视觉语言模型抽象。"""
    def describe(self, image, prompt: str) -> str:
        ...
```

## 5. OpenAI 兼容层

Ollama / vLLM / llama.cpp 均提供 OpenAI 兼容 `/v1/chat/completions`。因此可以用统一客户端（如 `openai` SDK）访问所有本地后端，只需改 `base_url` 与模型名。本项目 `models/` 层封装这一细节。

```python
# 示例：Ollama 默认地址
LLMConfig(base_url="http://localhost:11434/v1", model="qwen2.5:7b")
```

## 6. 硬件与性能预估

| 场景 | 硬件 | 帧率/延迟 |
|---|---|---|
| 纯文本循环 | CPU + 8G 内存 | 秒级每轮 |
| 读屏 OCR | 任意 | 2~3 秒/次可用 |
| 视觉 VLM | GPU ≥ 6G 显存 | 1~3 秒/帧 |
| 语音 ASR | CPU/GPU | 实时 |

## 7. 模型配置

通过 `config.yaml` 配置，不硬编码：

```yaml
models:
  llm:
    backend: ollama        # ollama / llamacpp / vllm / transformers
    base_url: http://localhost:11434/v1
    model: qwen2.5:7b
  vision:
    backend: ollama
    model: qwen2.5-vl:7b
  asr:
    backend: faster-whisper
    model: base
```

## 8. 接入步骤（MVP）

1. 安装 Ollama，`ollama pull qwen2.5:7b`。
2. 本项目 `models/llm.py` 封装 OpenAI 兼容调用。
3. `config.yaml` 指向本地地址即可跑通「思考/决策」循环。
4. 读屏用 OCR 起步，后续换 VLM。
