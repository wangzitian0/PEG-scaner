# Tech Specs

Technical Requirement Documents (TRD) for architecture, API design, and implementation patterns.

## 文档列表

| 文档 | 对应 BRN | 描述 | 状态 |
|------|---------|------|------|
| [TRD-000](./TRD-000.roadmap_phases.md) | - | 开发路线图（Phase 1-5） | ✅ 已完成 |
| [TRD-001](./TRD-001.infra_ping.md) | BRN-001 | 核心基建与 Ping 实现 | ✅ 已完成 |
| [TRD-002](./TRD-002.strawberry_fastapi.md) | BRN-002 | Strawberry + FastAPI 实现 | ✅ 已完成 |
| [TRD-003](./TRD-003.single_stock_tech.md) | BRN-003 | 个股页面技术设计 | ✅ 已完成 |

## 文档规范
- **内容重点**：架构图、调用关系、技术选型对比、接口伪代码（5-10行）
- **包含数据层**：数据库 Schema、ER 图、Neo4j 模型属于 TRD
- **不写内容**：完整实现代码（>50行放代码仓库）

## 参考
- [AGENTS.md](../../../AGENTS.md) - 文档组织原则
- [arch.md](../../arch.md) - 架构决策记录
