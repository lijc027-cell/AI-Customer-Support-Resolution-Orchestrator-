# AI Customer Support Resolution Orchestrator 简历与 STAR 话术

## 1. 简历项目标题

```text
AI Customer Support Resolution Orchestrator
技术栈：Python · FastAPI · LangGraph · PostgreSQL · Redis · pgvector · MCP · OpenAI Agents SDK
```

## 2. 简历项目一句话描述

```text
设计并实现面向企业客服与技术支持团队的 AI 工单解决编排系统，整合多 Agent workflow、RAG 检索、MCP/原生工具接入、审批与审计、离线评测与全链路追踪，支持高风险场景的可控自动化处理。
```

## 3. 简历项目描述

### 3.1 版本一：适合简历正文

```text
• 设计并实现企业级 AI 工单解决编排系统，覆盖工单分类、证据收集、解决建议生成、人工审批、结果回写与审计全链路，支撑客服/售后/技术支持场景的自动化处理

• 基于 LangGraph 设计 Triage / Investigator / Resolver / Verifier 多 Agent Workflow，将分类、调查、生成、验证解耦；支持 checkpoint、暂停审批、恢复执行等长任务控制能力

• 构建 Retrieval + Evidence Bundle 机制，整合知识库、历史工单、CRM、日志与账单信息，要求所有结论均可追溯到来源，降低无依据回复和高置信错误判断风险

• 设计 Tool Gateway 与 Connector 层，统一接入原生业务 API 与 MCP Server，支持 schema 校验、权限控制、timeout/retry、审计日志和结果标准化

• 设计 Skill Registry 与 Policy Engine，将退款、账务争议、企业 SSO、集成故障等领域处理流程沉淀为可版本化 skill，并将高风险动作纳入审批与升级边界

• 搭建离线 Eval Harness 与 Trace/Audit 体系，对分类准确率、grounded resolution rate、升级正确率、工具调用成功率、延迟和成本做版本回归分析
```

### 3.2 版本二：适合投大厂时压缩

```text
设计并实现 AI 工单解决编排系统，基于 LangGraph 构建多 Agent Workflow，整合 RAG、MCP/原生工具接入、审批流、审计日志和离线评测；支持企业客服/技术支持场景的 evidence-based resolution 与高风险动作可控自动化。
```

## 4. 项目亮点指标模板

做完项目后，建议把下面这些指标替换成真实数据：

```text
• 自动处理低风险工单占比：XX%
• grounded resolution rate：XX%
• 高风险工单越权自动关闭：0
• 平均处理时延较人工流程下降：XX%
• 工具调用成功率：XX%
• 工单全链路 trace 完整率：100%
```

## 5. STAR 结构化项目表述

### 5.1 标准 STAR 版本

**Situation**  
企业客服和技术支持团队的工单处理流程高度依赖人工排查，需要同时查知识库、历史工单、账户状态、账单信息和系统日志。现有 FAQ 或聊天机器人只能回答通用问题，无法在高风险业务场景里提供有证据、可审计、可升级的处理链路。

**Task**  
设计一个 AI 工单解决编排系统，不只是生成回复，而是能够完成工单分类、证据收集、解决建议生成、审批与升级、结果回写和离线评测，满足企业对可靠性、权限边界和审计能力的要求。

**Action**  
我把系统拆成 4 个职责明确的 agent：Triage 负责分类与风险识别，Investigator 负责 retrieval 与业务工具取证，Resolver 负责生成 diagnosis 和结构化处理建议，Verifier 负责 grounding、policy 和自动处理边界检查。  
在架构上，我用 LangGraph 做 workflow orchestration，支持 checkpoint、interrupt 和 resume；用 Tool Gateway 统一收口 native connector 和 MCP server；用 Skill Registry 固化账单争议、企业 SSO、集成排障等领域流程；再通过 Approval Service、Audit Log 和 Eval Harness 形成治理闭环。

**Result**  
最终系统能够形成一个可追踪、可审批、可评测的 AI 工单处理后端。项目不仅证明了多 Agent workflow 在企业支持场景中的适用性，也体现了我在 retrieval、tool integration、MCP 选型、权限边界、审计设计和 offline evals 上的系统设计能力。  
做完后可替换为真实结果，例如低风险工单自动处理比例、grounded resolution rate、平均时延下降幅度和工具调用成功率。

### 5.2 面试 90 秒口语版

```text
我做过一个 AI Customer Support Resolution Orchestrator，目标不是做 FAQ 机器人，而是把企业客服和技术支持的工单处理流程做成一个可控的 AI workflow。这个场景的难点在于，模型不能只会回答，它必须先分类，再查知识库、历史工单、CRM、账单或者日志，拿到证据之后才能生成解决建议，而且高风险场景还要审批和审计。

我把这个系统拆成 4 个 agent：Triage、Investigator、Resolver 和 Verifier。Triage 做分类和风险判断，Investigator 去做 retrieval 和工具调用，Resolver 负责生成 diagnosis 和用户回复，Verifier 专门做 grounding 和 policy 检查，决定是自动处理、审批还是升级人工。底层用 LangGraph 做编排，接了 Tool Gateway，把 native connector 和 MCP server 统一起来，同时用 Skill Registry 固化领域处理流程。最后我还设计了 trace、audit 和 eval harness，确保这个系统不只是能跑 demo，而是能被回放、评估和持续优化。
```

## 6. 面试追问与回答模板

### Q1：为什么这个项目要用多 Agent，而不是一个 Agent 解决？

**回答模板**

```text
我不是为了炫技上多 Agent，而是因为这个场景的职责边界非常清晰。分类和风险判断是一类问题，证据收集是一类问题，解决建议生成是一类问题，最后的 grounding 和 policy 校验又是另一类问题。如果把这些逻辑都塞进一个 Agent，输出会更难稳定，边界也更难审计。拆成 4 个 agent 后，每个环节都有清晰输入输出，更适合做测试、trace 和人工接管。
```

### Q2：这个项目里 MCP 的作用是什么？

**回答模板**

```text
我把 MCP 放在 Tool Gateway 下面，当成标准化外部接入的一种方式，而不是默认所有工具都走 MCP。像 ticket system 或 CRM 这种需要标准协议接入、未来可能跨 host 复用的能力，可以封成 MCP server；但像内部高频日志查询、数据库只读接口这类场景，我会优先 native connector，因为更轻、更容易控制延迟和上下文开销。所以我在这个项目里强调的是 MCP 与 native connector 的边界，而不是把所有东西都 MCP 化。
```

### Q3：你怎么保证模型生成的处理建议是有依据的？

**回答模板**

```text
我设计了 Retrieval + Evidence Bundle 机制。Investigator 先从知识库、历史工单和业务系统里拿证据，证据必须带 source 和 confidence，然后 Resolver 只能基于 evidence bundle 生成 diagnosis 和 response。最后 Verifier 会检查 grounding，如果证据不足或者结论和证据不一致，就不会放行自动处理。
```

### Q4：这个项目里最像后端系统设计的部分是什么？

**回答模板**

```text
最像后端系统设计的部分是 workflow state、tool gateway、approval/audit 和 eval 这几层。因为真正难的不是 prompt，而是怎么让一次工单 run 有状态、有边界、可恢复、可审计，还能在版本切换时做回归比较。这些东西本质上是后端系统设计问题，而不是单纯的 LLM 调用问题。
```

## 7. 简历写法建议

如果你的简历只留 3 条 bullet，建议保留：

```text
• 设计并实现企业级 AI 工单解决编排系统，覆盖分类、证据收集、解决建议生成、审批升级、结果回写与审计全链路
• 基于 LangGraph 构建 Triage / Investigator / Resolver / Verifier 多 Agent Workflow，整合 RAG、MCP/原生工具接入与 Skill Registry
• 搭建 Tool Gateway、Approval Service、Trace/Audit 与 Eval Harness，对 groundedness、升级正确率、延迟和成本做可回放、可评测的版本优化
```
