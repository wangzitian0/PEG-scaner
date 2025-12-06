# Tech Specs

Technical Requirement Documents (TRD) for architecture, API design, and implementation patterns.

## 文档列表

| 文档 | 对应 BRN | 描述 | 状态 |
|------|---------|------|------|
| [TRD-000](./TRD-000.roadmap_phases.md) | - | 开发路线图（Phase 1-5） | ✅ 已完成 |
| [TRD-001](./TRD-001.infra_ping.md) | BRN-001 | 核心基建与 Ping 实现 | ✅ 已完成 |
| [TRD-002](./TRD-002.strawberry_fastapi.md) | BRN-002 | Strawberry + FastAPI 实现 | ✅ 已完成 |
| [TRD-003](./TRD-003.single_stock_tech.md) | BRN-003 | 个股页面技术设计 | ✅ 已完成 |
| [TRD-005](./TRD-005.cms_graph_admin.md) | BRN-005 | CMS 知识图谱管理 | 🚧 进行中 |
| [TRD-004](./TRD-004.env_eaas_implementation.md) | BRN-004 | 开发/测试/生产环境 + tools/ 规范 | 🚧 进行中 |
| [TRD-007](./TRD-007.app_env_implementation.md) | BRN-007 | 应用环境实施细节（Compose + Infisical 规范） | 🚧 进行中 |

## 文档规范
- **内容重点**：架构图、调用关系、技术选型对比、接口伪代码（5-10行）、实施计划（Phase 列表、工时估算）
- **包含数据层**：数据库 Schema、ER 图、Neo4j 模型属于 TRD
- **包含实施**：详细的 Phase 规划、文件变更清单、风险评估
- **避免超大段的代码**：重点是给我审阅设计和架构，而不是代码

## 参考
- [AGENTS.md](../../../AGENTS.md) - 文档组织原则
- [arch.md](../../arch.md) - 架构决策记录
