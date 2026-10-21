# AURA v2 调研依据

> 整理日期：2026-10-21（两轮调研）。本文记录 v2 设计所依据的模型、论文和开源项目，以及哪些结论**还没核实**。
> 大部分资料来自厂商博客和二手报道，数字（价格、延迟、准确率）以官方文档为准，使用前要再确认。

## 1. 决策模型

**决策模型**（也叫 typed decision model）不生成自由文本：调用方给出状态、问题和答案形式，模型返回结构化结果，例如在给定选项里选一个并给出每个选项的概率、打分、是/否概率。它比大模型快、便宜，适合"持续判断"。

**关键限制：选项由调用方提供，模型不会自己想出新选项。** AURA 的"方向清单""习惯"等动态选项，要由 AURA 每次自己准备好再传进去。

| 模型 | 出品方 | 输入模态 | 权重 | 托管价格（输入 / 输出） | 台式机（4070S 12GB）能否本地跑 |
|---|---|---|---|---|---|
| **Jev** 1.13 / 1.14 | TypeSafe AI | 文本；1.14 起图片为**实验功能**（要加请求头 `TypeSafe-Danger-Zone-Images: true`），并新增 Box 题型（边界框） | 不公开 | $0.042 / 百万 token；输出免费 | 不能，只有托管 API，可能要排队申请 |
| **Clef-omni** | Cloudflare | 文本、图片；音频、视频在部分托管渠道显示"即将推出" | 开放（Apache 2.0），基于 Qwen3-Omni-30B-A3B | $0.15 / 百万 token；输出免费；上下文 64K | 基本不能：第三方估算 INT4 约 19GB |
| **Clef-flash** | Cloudflare | 文本 | 开放 | $0.038 / 百万 token | 不能：据报道至少要 41GB 显存 |
| **Decision 3.0**（d3 系列） | vLLM Semantic Router | 6 个型号里 5 个支持图片和视频（具体哪个不支持未确认） | 开放（Hugging Face），只有 BF16 | 未找到官方托管价格 | 只能跑小号：d3-nano 2.21B（约 4.4GB）、d3-lite 0.85B、d3-edge 0.59B；d3-mini 4.54B 很紧；需要 vLLM nightly，Windows 上要用 WSL2 |
| **Laya** | ConvAI Innovations | 只有文本 | 开放（Apache 2.0） | — | 可以，但不支持图片 |

**选型结论（2026-10-21 由用户决定）**
- 决策模型用**本地开源模型**：首选 **d3-nano**，在台式机 WSL2 里用 vLLM nightly 运行；先确认它支持图片，再用自己的数据评估准确率。不够时试 d3-mini；只需要文本时可以用 Laya。
- Clef-omni、Jev 保留为可选的云端后端，默认不用。
- 大模型用线上 **glm-5.3-flash**（OpenAI 兼容接口）。
- 所有决策模型都通过 AURA 的 `DecisionModel` 抽象接入，随时可以换。这些模型都刚发布一两个月，变化会很快。

## 2. 主动式 Agent 相关研究

### 2.1 清华 ProactiveAgent（THUNLP 等，2024）

- 论文：*Proactive Agent: Shifting LLM Agents from Reactive Responses to Active Assistance*（arXiv 2410.12361）
- 代码：`thunlp/ProactiveAgent`（Apache 2.0；2026-10-21 查看时有 677 星，最近推送 2026-05-12）

**做法**
- 感知：用开源工具 **ActivityWatch** 记录前台窗口、是否离开电脑（afk），加浏览器插件和 VS Code 插件；用 `pynput` 拼接键盘鼠标事件。只关注浏览器和 VS Code，忽略其他软件。
- 主动：每隔约 15 秒把整理好的事件交给大模型，预测"用户可能需要什么帮助"，然后弹出 Windows 桌面通知，用户可以接受或拒绝。
- 奖励模型：用 1,760 条人工标注（1,640 条训练、120 条测试）微调 LLaMA-3.1-8B，判断"提议和时机是否合适"。
- **ProactiveBench**：一套"该不该主动提议"的数据和评估脚本。

**AURA 借用的部分**
1. **ActivityWatch 作为感知底座**：它是成熟的开源软件，自带本地 REST API（默认端口 5600）。但它读不到窗口里的文字，所以 AURA 还要自己补 UIA 文字和截图。
2. **键盘事件拼接**：用来识别"写了又删、迟迟不发"这类犹豫行为。隐私非常敏感，见设计文档第 8 节。
3. **ProactiveBench 作为离线测试集**：用来检验决策模型"该不该出手"判断得准不准。数据具体内容和许可**还没核实**。
4. **Windows 通知**：它的代码里有注册 AUMID、带按钮通知的实现（`agent/register_hkey_aumid.py`），客户端可以参考。

**不借用的部分**
- 主循环：它每一轮都调用大模型，再判断合不合适。AURA 反过来：决策模型先判断，需要时才调用大模型。
- 感知范围：它只看浏览器和 VS Code；AURA 要覆盖所有软件。

### 2.2 Purdue / Microsoft 等：主动式 Agent 是否需要大模型决定何时唤醒（2026-05）

- 论文：*Do Proactive Agents Really Need an LLM to Decide When to Wake and What to Anchor?*（arXiv 2605.30152）
- 观点：活动日志本身是结构化数据，没必要转成文字再让大模型解析。他们用一个小型时序图模型给每个事件打"触发概率"，只有触发时才调用大模型，把一份简短的结构化交接内容写成给用户看的话。
- 报告结果（**只看了摘要，未核实**）：在 14 个基础模型上 F1 都有提升（平均 +16.7）；每个事件约 11~14 毫秒，普通笔记本也能跑。

**对 AURA 的意义**
- 支持"小模型判断、大模型只在需要时出场"的分工。
- 指出了长期方向：等 AURA 攒下足够多的"情境 → 决策 → 你的反应"数据，可以训练一个专门的小模型，替换或辅助通用决策模型。

### 2.3 其他相关研究（第二轮调研）

| 研究 | 要点 | 对 AURA 的改进 |
|---|---|---|
| **GUM：从电脑使用中建立通用用户模型**（斯坦福，arXiv 2505.10831，2025） | 只靠观察（主要是截图），把对用户的了解写成一条条**带置信度的自然语言判断句**；新观察到来时检索相关判断句并修改。开源 Python 包 `gum-ai`（MIT）。论文报告推断是校准的 | 关于你的知识改为带把握程度的判断句（design 4.6）；统计概率校准度（design 4.3、demo 16.2）；阶段 2 评估 `gum-ai` |
| **Fogarty 等 2005：预测人的可打扰程度**；**Iqbal & Bailey 2006（CHI）：任务断点** | 键鼠活动、窗口切换等简单信号预测"能不能打扰"的准确度与人接近；在小任务之间的断点打扰代价最低 | 感知层检测断点；中档表达等断点；明确情况下用程序规则判断时机（design 4.1.4、4.5.1，demo 6.4、8.3） |
| **Need Help? 编程中的主动 AI 助手**（CMU、微软等，CHI 2025） | 主动助手总体上提高了完成任务数和体验，但提示的时机和介入程度会明显影响交互；建议在不打断人的时刻、结合工作状态给出 | 表达分轻、中、重三档（design 4.5.1，demo 第 10 节） |
| **ContextAgent**（NeurIPS 2025）、**ProAgent**（arXiv 2512.06721） | 可穿戴设备上的主动 Agent：先从感知推断意图，再判断要不要帮忙；ProAgent 按需启用感知 | 情境摘要（design 4.2）；感知源"按需加深"（design 4.1.1） |
| **Horvitz 1999：混合主动界面原则**（CHI 99，LookOut） | 根据用户目标的概率和代价，在直接做、先对话、不做之间选择；把握不够时缩小服务范围；考虑打扰时机 | 按把握和代价决定做还是问（design 4.5.2） |
| **Sleep-time compute**（Letta、伯克利，2025） | 让模型在空闲时预处理信息；二手资料报告同等准确率下测试时计算量减少约 2.5 倍（未核实原文） | 后台整理时增加"预想"（design 4.8） |
| **键盘行为与情绪研究**（多篇，2016~2022） | 打字时长、停顿、删除等与情绪、压力有关，但效应小、个体差异大；个性化基准更可靠 | 犹豫、疲惫要与个人基准比较（design 4.7）；事件保存结构化数据（design 4.1.3） |

## 3. 人脑机制与 AURA 的对应

只借**功能**，不模仿神经元或脑区结构。有些理论还有争议，这里只作为设计灵感。

| 人脑机制 | 要点 | AURA 中的对应 |
|---|---|---|
| 全局工作空间（意识舞台） | 很多过程并行，意识一次只关注少数内容；胜出的内容被"广播"去记忆、思考和行动 | **注意焦点**：外部事件和内部念头竞争，胜出者才进入思考 |
| 显著性网络 | 判断什么值得注意，在"向外专注"和"向内走神"之间切换 | 决策模型的"值不值得想" |
| 预测加工 | 大脑持续预测，注意力被"意外"吸引 | 学习你的日常规律，偏离规律时才值得注意 |
| 快思考和慢思考 | 自动的快速判断 vs 费力的深入思考 | 决策模型 vs 大模型 |
| 心智理论 | 推测别人的意图和状态 | 维护"你现在的状态"：专注、疲惫、犹豫…… |
| 基底节选择与前额叶抑制 | 从候选行为中放行一个，冲突时踩刹车 | 判断时机、待说列表（想说但先忍住） |
| 多巴胺奖励预测误差 | 结果好于或差于预期，会调整下次的选择 | 你的反应（采纳、关掉、忽略、👍👎）作为奖励 |
| 互补学习系统 | 海马体快速记下具体经历，新皮层慢慢整理成知识 | 事件日志快速写入；空闲或夜里整理成小抄和长期知识 |
| 程序记忆、习惯 | 熟练后不再需要思考 | 被反复采纳的做法变成"习惯"，不再调用大模型 |
| 默认网络（走神） | 空闲时回想、联想、规划 | 外部安静时，内部念头赢得注意焦点 |
| 情绪和内在动力 | 精力、好奇、表达欲影响注意和行动 | 内在状态值：好奇心、精力（思考预算）、表达欲、关心 |

## 4. 还没核实、动手前要确认的事

1. Clef-omni 托管 API 的调用方式、图片输入格式，以及音频、视频是否已开放。
2. Clef-omni 和 Decision 3.0 是否支持"一次调用问多道题"（Jev 文档说支持并行）。
3. d3 系列中哪一个**不**支持图片；d3-nano 在 4070S 上的延迟。
4. ProactiveBench 数据的内容、格式和许可。
5. ActivityWatch 在台式机上能否正常运行，各个插件（浏览器、VS Code）的可用性。
6. UIA 在常用软件里能读到多少文字（VS Code、Windows Terminal、浏览器、微信等）。
7. Purdue 论文的完整实验细节。
8. `gum-ai` 能否直接用于 AURA（依赖、成本、是否必须截图）。
9. Sleep-time compute 约 2.5 倍的数字（只看了二手资料）。
10. Need Help? 论文中具体的时机条件和结果（只看了摘要）。
11. 托盘图标和带按钮的 Windows 通知用哪个 Python 库。
12. glm-5.3-flash 在复杂请求下的延迟和费用（2026-10-21 已在台式机调通：推理模型，简单请求约 4 秒）。

## 5. 来源

决策模型
- Jev：[Runware](https://runware.ai/models/typesafe-jev)、[eesel 价格](https://www.eesel.ai/blog/typesafe-jev-pricing)、[flaviocopes 价格](https://flaviocopes.com/jev-pricing/)、[cloudprice](https://cloudprice.net/models/typesafe-jev)、[Jev 1.14 发布（remio）](https://www.remio.ai/post/jev-1-14-0-release-expands-what-jev-can-see-but-typesafe-wont-call-it-production)、[Jev 1.14 图片输入（SmartScope）](https://smartscope.blog/en/blog/jev-image-input-guide-asset-handling-choice-box-2026/)、[Jev 1.14 Box（RuntimeWire）](https://runtimewire.com/article/typesafe-jev-1-14-danger-zone-experiments)
- Clef-omni：[Cloudflare 博客](https://blog.cloudflare.com/clef-faster-cheaper-multimodal)、[AI Weekly](https://aiweekly.co/alerts/cloudflare-ships-multimodal-clef-omni-cuts-flash-to-0038m)、[TechEnclave](https://techenclave.com/news/items/cloudflare-adds-clef-omni-and-cuts-clef-flash-pricing-with-a-shorter-hosted-context)、[Spheron 显存估算](https://www.spheron.network/tools/gpu-recommender/Cloudflare/clef-omni/)、[llmreference](https://www.llmreference.com/model/clef-omni)
- Decision 3.0：[vLLM recipes d3](https://recipes.vllm.ai/vllm-sr/d3)、[d3-nano](https://recipes.vllm.ai/vllm-sr/d3-nano)、[d3-edge](https://recipes.vllm.ai/vllm-sr/d3-edge)、[MarkTechPost](https://www.marktechpost.com/2026/10/11/what-is-decision-3-0-vllm-semantic-routers-new-open-decision-models/)、[OrcaRouter](https://www.orcarouter.ai/blog/decision-3-0-open-multimodal-decision-models)
- Laya：[gradually.ai](https://www.gradually.ai/en/ai-models/laya/)、[eesel](https://www.eesel.ai/blog/laya-ai)

主动式 Agent
- [Proactive Agent 论文（arXiv 2410.12361）](https://arxiv.org/abs/2410.12361)
- [thunlp/ProactiveAgent](https://github.com/thunlp/ProactiveAgent)
- [Do Proactive Agents Really Need an LLM to Decide When to Wake and What to Anchor?（arXiv 2605.30152）](https://arxiv.org/abs/2605.30152)

人脑机制
- [Salience network（Wikipedia）](https://en.wikipedia.org/wiki/Salience_network)
- [Goulden et al. 2014：显著性网络驱动网络切换](https://e-space.mmu.ac.uk/617647/6/Goulden%20et%20al%202015-1.pdf)
- [Menon & Uddin 2010（PMC）](https://pmc.ncbi.nlm.nih.gov/articles/PMC2899886)
- [LIDA 认知架构（Wikipedia）](https://en.wikipedia.org/wiki/LIDA_(cognitive_architecture))
- [Gurney et al. 2001：基底节动作选择](https://pubmed.ncbi.nlm.nih.gov/11417052/)
- [Wiecki & Frank 2013：抑制控制模型](https://ski.clps.brown.edu/papers/WieckiFrank_psyrev.pdf)
- [默认网络与意外（PMC）](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7815915/)
- [Kumaran, Hassabis & McClelland 2016：互补学习系统更新](https://psych205.stanford.edu/papers/KumaranHassabisMcC16CLSUpdate.pdf)

第二轮调研
- [Creating General User Models from Computer Use（GUM，arXiv 2505.10831）](https://arxiv.org/abs/2505.10831)、[gum-ai（PyPI）](https://pypi.org/project/gum-ai/)
- [Fogarty et al. 2005：Predicting Human Interruptibility](https://interruptions.net/literature/Fogarty-TOCHI05.pdf)
- [Iqbal & Bailey CHI 2006：任务断点与打扰代价](https://interruptions.net/literature/Iqbal-CHI06-p741-iqbal.pdf)
- [Intelligent Notification Systems 综述（arXiv 1711.10171）](https://arxiv.org/pdf/1711.10171)
- [Need Help? Designing Proactive AI Assistants for Programming（arXiv 2410.04596）](https://arxiv.org/abs/2410.04596)
- [ContextAgent（NeurIPS 2025）](https://proceedings.neurips.cc/paper_files/paper/2025/hash/f4e5cd2079f5a6cf5176818add841531-Abstract-Conference.html)、[ProAgent（arXiv 2512.06721）](https://arxiv.org/abs/2512.06721)
- [Principles of Mixed-Initiative User Interfaces（Horvitz CHI 99）](https://www.erichorvitz.com/chi99horvitz.pdf)
- [Sleep-time compute（Letta 博客）](https://letta.com/blog/sleep-time-compute)
- [程序员压力与键盘行为（FedCSIS 2016）](https://annals-csis.org/proceedings/2016/pliks/263.pdf)、[情绪对键盘输入的影响（阳明交大）](https://ir.lib.nycu.edu.tw/handle/11536/24927)、[写消息时的情绪预测（SciTePress 2022）](https://www.scitepress.org/Papers/2022/113673/113673.pdf)
