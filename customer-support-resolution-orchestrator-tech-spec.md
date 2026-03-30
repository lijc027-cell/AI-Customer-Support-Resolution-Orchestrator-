# AI Customer Support Resolution Orchestrator 技术方案

## 1. 项目定位

### 1.1 项目目标

构建一个面向企业客服、售后和技术支持团队的 AI 工单解决编排系统。系统不是单纯生成回复，而是围绕工单处理全流程完成：

- 工单分类与优先级判断
- 知识检索与历史案例召回
- 业务工具调用与证据收集
- 解决建议生成
- 高风险场景升级与人工审批
- 结果回写与全链路审计
- 效果评估与持续优化

### 1.2 目标用户

- 客服运营团队
- 技术支持团队
- B2B 客户成功团队
- 内部质量与风控团队

### 1.3 目标价值

- 降低低风险标准工单的人力占用
- 缩短复杂工单的调查与响应时间
- 提高回复一致性和证据充分性
- 建立可回放、可审计、可评测的 AI 工单处理体系

## 2. 背景问题

企业支持团队常见问题：

- 工单来源分散，信息结构不统一
- 处理过程依赖人工查文档、查订单、查日志、查历史工单
- 低风险工单适合自动化，高风险工单必须人工介入
- 现有 FAQ 机器人无法胜任调查、判断、升级、回写等动作
- 业务方需要的不只是回答能力，而是有证据、有边界的执行能力

因此，本项目的核心不是做一个更会聊天的机器人，而是做一个有业务流程意识、权限边界和质量闭环的 AI 应用后端。

## 3. 业务范围

### 3.1 覆盖场景

- 账单与退款咨询
- 权限与账号问题
- 集成配置与接入故障
- 产品 bug 排查与升级
- 常见企业支持问题的标准化处理

### 3.2 不覆盖场景

- 完全开放式通用对话
- 无权限控制的数据库写操作
- 直接执行高风险业务动作
- 无审计、无审批的自动关闭高优先级工单

## 4. 总体架构

### 4.1 高层架构

系统分为 7 层：

1. 接入层
2. 工单编排层
3. Agent Runtime 层
4. Knowledge & Retrieval 层
5. Tools / MCP / Connector 层
6. Governance & Eval 层
7. 数据与观测层

### 4.2 系统组件

- Ticket Ingestion Service
- Workflow Orchestrator
- Agent Runtime
- Skill Registry
- Retrieval Service
- Tool Gateway
- MCP Registry
- Policy Engine
- Approval Service
- Trace & Audit Service
- Eval Harness
- Operator Console API

### 4.3 推荐技术栈

- Backend: Python + FastAPI
- Workflow: LangGraph
- Queue: Celery 或 Temporal
- Database: PostgreSQL
- Cache / Session: Redis
- Vector Store: pgvector 或 Qdrant
- Object Storage: S3 compatible storage
- Observability: OpenTelemetry + Grafana + Langfuse/LangSmith
- LLM Provider: OpenAI Agents SDK 或 Anthropic Agent SDK
- MCP: Python/TypeScript MCP SDK

## 5. 核心业务流程

### 5.1 工单处理主流程

1. 接收工单
2. 标准化工单结构
3. Triage Agent 分类、判优先级、判风险
4. Retriever / Investigator 收集知识与业务证据
5. Resolver Agent 生成解决方案
6. Verifier Agent 审查证据充分性、合规性和风险
7. 根据结果走三种路径：
   - 自动回复并回写
   - 待人工审批
   - 升级到人工专家
8. 写入执行日志、审计日志和评测数据

### 5.2 关键控制点

- 高风险关键词命中时必须升级
- 高价值账户必须人工审批
- 缺乏充分证据时禁止自动关闭工单
- 工具调用失败时必须记录原因并触发降级策略

## 6. Multi-Agent 设计

### 6.1 角色划分

#### Triage Agent

职责：

- 识别问题类型
- 识别优先级
- 识别是否为高风险场景
- 决定后续所需工具与技能

输入：

- 原始工单文本
- 用户与账户基础信息

输出：

- category
- priority
- risk_level
- required_skills
- suggested_tools

#### Investigator Agent

职责：

- 检索知识库与历史案例
- 调用业务系统工具收集证据
- 汇总工单诊断上下文

输入：

- triage 结果
- 可调用工具集合

输出：

- evidence_bundle
- candidate_causes
- missing_information

#### Resolver Agent

职责：

- 基于证据生成解决建议
- 输出用户回复和内部备注
- 给出置信度与下一步建议

输出：

- diagnosis
- confidence
- recommended_action
- user_response
- internal_notes

#### Verifier Agent

职责：

- 检查回答是否有依据
- 检查是否越权
- 检查是否满足自动执行条件
- 判断 accept / approve / escalate / ask-human

### 6.2 为什么需要多 Agent

本项目采用多 Agent，不是为了展示“会做 multi-agent”，而是因为职责边界明确：

- 分类与调查是不同问题
- 调查与生成是不同问题
- 生成与验证是不同问题
- 风险控制需要独立判断层

## 7. Skills 设计

### 7.1 Skill 的作用

Skill 用来固化领域处理策略，而不是每次依赖 prompt 临时发挥。

### 7.2 推荐 Skills

- billing-dispute-handling
- refund-escalation-policy
- enterprise-sso-troubleshooting
- integration-diagnostic-playbook
- critical-incident-routing

### 7.3 Skill 内容结构

每个 skill 包含：

- 触发条件
- 所需输入
- 处理流程
- 输出结构
- 风险边界
- 何时升级人工
- 禁止动作

### 7.4 Skill 触发机制

- 由 Triage Agent 选择候选 skill
- 由 Policy Engine 做最终允许列表过滤
- 运行时保留 skill version，便于审计和回归测试

## 8. MCP 与 Connector 设计

### 8.1 设计原则

不是所有工具都应该 MCP 化。

选型原则：

- 跨客户端复用、标准化接入需求强：优先 MCP
- 高频内部工具、已有稳定 SDK/CLI：优先 native connector

### 8.2 推荐 MCP 场景

- 工单系统读取
- CRM 信息读取
- 外部文档系统只读检索

### 8.3 推荐 Native Connector 场景

- 内部数据库只读查询
- 日志摘要服务
- 内部审批 API
- 高性能缓存访问

### 8.4 Tool Gateway 设计

Tool Gateway 统一负责：

- 工具注册
- schema 校验
- tool-level RBAC
- timeout / retry / circuit breaker
- 审计记录
- 结果标准化

## 9. Retrieval 与知识系统设计

### 9.1 数据来源

- 产品文档
- FAQ
- 历史工单
- 事故复盘
- 内部 SOP
- 账户与订单辅助信息

### 9.2 检索策略

- 文档离线切分与 embedding
- metadata 标记场景、产品线、版本、租户
- hybrid retrieval
- reranking
- top-k 证据合并

### 9.3 结果要求

- 每条证据必须带 source
- 对用户回复和内部备注都要保留来源链路
- 无证据时不得输出“确定性”判断

## 10. 状态管理与数据模型

### 10.1 Workflow State

建议状态字段：

- ticket_id
- tenant_id
- requester_profile
- category
- priority
- risk_level
- selected_skills
- evidence_bundle
- recommended_action
- verification_result
- approval_status
- final_resolution
- trace_id
- audit_events

### 10.2 核心数据表

#### tickets

- id
- tenant_id
- source
- external_ticket_id
- title
- description
- status
- priority
- created_at

#### agent_runs

- id
- ticket_id
- workflow_version
- model_version
- skill_version_set
- start_time
- end_time
- outcome
- latency_ms
- token_usage

#### tool_calls

- id
- run_id
- tool_name
- input_payload
- output_summary
- status
- latency_ms
- error_message

#### approvals

- id
- run_id
- approval_type
- requested_by
- reviewed_by
- status
- reason
- created_at

#### eval_records

- id
- run_id
- dataset_name
- metric_name
- metric_value
- label_source

## 11. Policy、权限与审计

### 11.1 权限模型

- tenant isolation
- operator RBAC
- tool-level permission scope
- approval scope
- data classification tagging

### 11.2 风险控制

高风险条件示例：

- 涉及退款或账务调整
- 涉及企业管理员权限变更
- 涉及安全配置修改
- 涉及生产事故或大客户升级

### 11.3 审计要求

必须记录：

- 输入工单快照
- 所有 skill 版本
- 所有 tool 调用
- 关键中间判断
- 最终决策与人工审批信息

## 12. Eval Harness 设计

### 12.1 评测目标

建立离线评测与回归机制，不依赖主观“感觉变好了”。

### 12.2 数据集来源

- 匿名历史工单
- 合成复杂工单
- 人工标注标准答案与升级标签

### 12.3 核心指标

- classification accuracy
- correct escalation rate
- grounded resolution rate
- unsafe auto-action rate
- average latency
- operator acceptance rate
- deflection rate

### 12.4 评测维度

- 模型版本
- prompt / skill 版本
- retrieval 配置
- tool policy 配置

## 13. 可观测性设计

### 13.1 Trace

每个 ticket run 需要 trace_id，贯穿：

- ticket intake
- agent nodes
- retrieval
- tool calls
- approval
- final writeback

### 13.2 Metrics

- p50 / p95 latency
- cost per ticket
- tool failure rate
- escalation rate
- approval wait time
- groundedness score

### 13.3 Logging

- structured logs
- error taxonomy
- replayable workflow events

## 14. API 设计

建议提供：

- `POST /tickets/intake`
- `GET /tickets/{id}/status`
- `GET /tickets/{id}/trace`
- `POST /tickets/{id}/approve`
- `POST /tickets/{id}/resume`
- `GET /admin/evals`
- `GET /admin/tool-calls`

## 15. 部署与运行

### 15.1 部署拓扑

- API 服务
- Worker 集群
- PostgreSQL
- Redis
- Vector Store
- Object Storage
- Observability stack

### 15.2 运行模式

- 同步模式：低复杂度工单
- 异步模式：复杂调查与审批工单

## 16. 分阶段交付建议

### Phase 1

- 单租户
- 单一 ticket source
- triage + retrieval + resolver + verifier
- 基础人工审批

### Phase 2

- 多 connector
- MCP registry
- skill registry
- trace dashboard

### Phase 3

- 完整 eval harness
- AB test
- 自动回归
- 多租户与策略中心

## 17. 招聘展示重点

这个项目最适合突出以下能力：

- AI 应用后端架构
- 多 Agent 编排
- RAG 与 grounded generation
- MCP 与 connector 选型能力
- skills 机制设计
- approval / audit / policy control
- evals 与可观测性

## 18. 目标结果指标

建议最终项目以这些指标收尾：

- 自动处理 40% 以上低风险工单
- grounded resolution rate 达到 80% 以上
- 高风险工单 0 次越权自动关闭
- 平均处理时延相较人工流程显著下降
- 全链路可追踪、可审计、可回放
