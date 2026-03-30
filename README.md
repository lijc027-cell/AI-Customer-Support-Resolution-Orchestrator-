# AI Customer Support Resolution Orchestrator

> Backend MVP for evidence-based customer support workflows.

这是一个面向企业客服与技术支持场景的后端项目。它不是 FAQ 聊天机器人，而是把工单接入、风险判断、证据收集、解决建议、审批边界和审计追踪串成一个可运行的工作流闭环。

## 为什么值得看

- 不是单轮对话 demo，而是 `ticket intake -> triage -> investigate -> resolve -> verify` 的完整后端链路。
- 用 `LangGraph` 表达长任务工作流形态，并把分类、调查、生成、验证拆成独立阶段。
- 同时展示了 native connector 和 MCP server 两种外部能力接入方式。
- 提供 `FastAPI` API、CRM 证据补充、run 持久化、audit/trace 记录和 MCP JSON-RPC 测试覆盖。

## 当前实现

- `POST /tickets/intake`：接收工单并返回结构化 `RunSummary`。
- `GET /runs/{run_id}`：读取已持久化的 workflow run。
- 工单会基于关键词做 `category / priority / risk_level` 判断。
- 高风险 billing/refund/invoice 请求会进入 `approval_pending` 状态。
- `RetrievalService` 与 `crm_lookup` 会共同生成 evidence bundle。
- `AuditService`、`TraceService`、`RunStore` 会保留审计、trace 和运行记录。
- `MinimalMCPServer` 通过 JSON-RPC 暴露 `crm_lookup` 工具。
- 当前测试覆盖 `27` 个 `pytest` 用例。

## 仓库结构

| 路径 | 作用 |
| --- | --- |
| `src/customer_support_resolution/api` | FastAPI 路由与 API 响应模型 |
| `src/customer_support_resolution/domain` | 工单、证据、resolution、run summary 等核心模型 |
| `src/customer_support_resolution/services` | workflow、retrieval、policy、approval、audit、trace、run store |
| `src/customer_support_resolution/connectors` | 业务系统 connector |
| `src/customer_support_resolution/mcp` | 最小 MCP server 实现 |
| `tests` | API、workflow、connector、MCP 集成测试 |
| `docs` | 架构、设计、路线图、面试材料 |

## 关键流程

1. 工单通过 `POST /tickets/intake` 进入系统。
2. `CustomerSupportWorkflow` 先做 triage，判断类别、优先级和风险。
3. `RetrievalService` 收集知识证据，`ToolGateway` 补充 CRM 账户快照。
4. `Resolver` 生成 diagnosis、recommended action 和 user reply。
5. `PolicyEngine` 判断是否需要审批，并将状态置为 `completed` 或 `approval_pending`。
6. `AuditService`、`TraceService`、`RunStore` 持久化运行结果，支持后续读取与回放扩展。

## API 快照

| Endpoint | 说明 |
| --- | --- |
| `GET /health` | 健康检查 |
| `POST /tickets/intake` | 创建工单 run 并返回执行摘要 |
| `GET /runs/{run_id}` | 查询指定 run 的持久化结果 |

示例请求：

```json
{
  "tenant_id": "tenant_acme",
  "source": "zendesk",
  "external_ticket_id": "zd_1001",
  "requester": {
    "id": "u_1",
    "email": "alice@acme.com",
    "name": "Alice"
  },
  "account_context": {
    "account_id": "acc_1",
    "org_id": "org_1",
    "plan_type": "enterprise",
    "product": "iam-cloud",
    "product_version": "v5.2.1"
  },
  "ticket": {
    "title": "Urgent refund issue",
    "body": "Need urgent billing refund investigation",
    "attachments": []
  },
  "metadata": {
    "channel": "email"
  }
}
```

## 快速运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn customer_support_resolution.main:app --reload
```

启动后可访问：

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/health`

运行测试：

```bash
pytest
```

## 项目状态

这个仓库当前是一个 runnable backend MVP：

- 已有真实可跑的 API、workflow 和测试。
- 设计文档覆盖了生产化扩展方向，如更完整的 connector、审批服务、评测与数据层。
- 适合在面试中展示你对 agent workflow、后端边界和治理能力的理解，而不是把它包装成“已经上线的大而全平台”。

## 文档导航

- [架构设计](docs/architecture/customer-support-resolution-orchestrator-architecture.md)
- [技术方案](docs/design/customer-support-resolution-orchestrator-tech-spec.md)
- [数据与 API 设计](docs/design/customer-support-resolution-data-api-design.md)
- [实施计划](docs/implementation/customer-support-resolution-implementation-plan.md)
- [路线图](docs/roadmap/customer-support-resolution-roadmap.md)
- [简历与 STAR 话术](docs/interview/customer-support-resolution-resume-star.md)

