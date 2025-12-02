# Workflows (Change Types)

> 入口：根据变更类型选择对应流程文件；流程彼此正交，避免混用

## 目录

| 文件 | 适用范围 | 备注 |
|------|----------|------|
| [docs-change.md](./docs-change.md) | 仅文档/目录治理，无代码改动 | 侧重索引和一致性 |
| [app-logic-change.md](./app-logic-change.md) | 应用层代码变更（前后端、GraphQL resolver/service） | 强制跑相关测试 |
| [data-schema-change.md](./data-schema-change.md) | 数据/Schema 变更（GraphQL SDL、Neo4j、因子口径） | 关注多源校验 |
| [infra-automation-change.md](./infra-automation-change.md) | 基建、CI/CD、开发脚本、环境配置 | 注重回滚与成本 |

## 使用案例

| 场景 | 选择的 workflow | 说明 |
|------|----------------|------|
| 更新 `docs/index.md` 导航、整理 README 链接 | docs-change | 仅文档结构和索引调整，不改代码 |
| 修改 GraphQL resolver 逻辑、补充单测 | app-logic-change | 接口契约不变，专注业务行为和测试 |
| 为股票节点新增字段并更新 SDL 与校验规则 | data-schema-change | 涉及数据口径/Schema，需要多源校验 |
| 调整 `docker-compose.yml` 端口或 CI 缓存策略 | infra-automation-change | 环境/管道/脚本变更需考虑回滚与成本 |
| 需求同时涉及 Schema 与应用逻辑 | 拆分为 data-schema-change + app-logic-change | 先更新 Schema，再按逻辑流程落地调用方 |

### 正交性原则
- 先判断目标输出是什么：文档、业务逻辑、数据定义、基建管道。
- 只选一个流程执行；若涉及多个领域，将需求拆分后分别走流程。
- 遵循 `AGENTS.md` 和 `docs/specs/infra/IRD-001.ai_evaluation.md` 的评分/约束。
