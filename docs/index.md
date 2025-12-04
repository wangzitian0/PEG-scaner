# 文档索引

> **AI 阅读入口**：从 `AGENTS.md` 进入，到本文件找到"对的位置"

---

## 文件职责定义

| 文件 | 职责 | 更新时机 | 谁写 |
|------|------|----------|------|
| **本文件 (index.md)** | 索引 + 当前状态总览 | 每次迭代结束 | Agent |
| **[workflows/\*.md](./workflows/README.md)** | 变更流程定义（按类型正交） | 新增/调整流程时 | Agent |
| **[PRD-000.stock_app_overview.md](./specs/product/PRD-000.stock_app_overview.md)** | 产品总览（整体目标/界面列表） | 用户修改需求时 | 用户 |
| **[TRD-000.roadmap_phases.md](./specs/tech/TRD-000.roadmap_phases.md)** | 开发路线图（Phase 1-5 高层规划） | 规划调整时 | Agent |
| **[TRD-001.infra_ping.md](./specs/tech/TRD-001.infra_ping.md)** | 核心基建技术实现（对应 BRN-001） | 基建变更时 | Agent |
| **[TRD-002.strawberry_fastapi.md](./specs/tech/TRD-002.strawberry_fastapi.md)** | GraphQL 协议实现（对应 BRN-002） | 协议/Schema 变更时 | Agent |
| **[TRD-003.single_stock_tech.md](./specs/tech/TRD-003.single_stock_tech.md)** | 个股页面技术设计（对应 BRN-003） | 个股页技术变更时 | Agent |
| **[TRD-004.env_eaas_implementation.md](./specs/tech/TRD-004.env_eaas_implementation.md)** | 开发/测试/生产环境（对应 BRN-004） | 环境变更时 | Agent |
| **[TRD-005.cms_graph_admin.md](./specs/tech/TRD-005.cms_graph_admin.md)** | Django CMS + Neo4j Admin（对应 BRN-005） | CMS/Admin 变更时 | Agent |
|| **[DRD-005.data_pipeline_ops.md](./specs/BI/DRD-005.data_pipeline_ops.md)** | 数据流水线运营规范（对应 BRN-005） | 数据运营规则变更时 | Agent |
| **[PRD-003.single_stock_page.md](./specs/product/PRD-003.single_stock_page.md)** | 个股页面产品需求（对应 BRN-003） | 产品需求变更时 | Agent |
| **[todowrite.md](./project/BRN-001/todowrite.md)** | 需求完成状态跟踪（打勾用） | 每次完成任务后 | Agent |
| **[IRD-001.md](./specs/infra/IRD-001.md)** | AI 评分机制详细说明 | 机制变更时 | Agent |
| **[IRD-004.md](./specs/infra/IRD-004.env_eaas_infra.md)** | 开发/测试/生产环境基础设施 | 环境变更时 | Agent |
| **[project/BRN-001/README.md](./project/BRN-001/README.md)** | 迭代管理规范 + 当前 Phase 状态 | Phase 状态变更时 | Agent |
| **[project/BRN-001/prompt.md](./project/BRN-001/prompt.md)** | 用户指令日志（SSOT） | 每次收到指令后 | Agent |
| **project/BRN-001/phrase_N.xxx/** | 单个迭代的详细记录 | 迭代进行中 | Agent |

---

## 当前状态

| 迭代 | 名称 | 状态 | 详情 |
|------|------|------|------|
| BRN-001 | 核心基建 & 个股页面 | 🚧 进行中 | [project/BRN-001/](./project/BRN-001/README.md) |
| BRN-002 | 架构迁移（Strawberry + FastAPI） | ✅ 已完成 | [project/BRN-002/](./project/BRN-002/README.md) |
| BRN-003 | 个股页面完整实现 | 📋 未开始 | [project/BRN-003/](./project/BRN-003/README.md) |
| BRN-004 | 开发/测试/生产环境 | 🚧 进行中 | [project/BRN-004/](./project/BRN-004/README.md) |
| BRN-005 | 股票知识图谱 Schema + CMS | 📋 待确认 | [TRD-005](./specs/tech/TRD-005.cms_graph_admin.md) |

### BRN-001 Phase 进度
| Phase | 名称 | 状态 |
|-------|------|------|
| 0 | GraphQL & Nx 基础设施 | ✅ 已完成 |
| 1 | 个股页面骨架 | 🚧 进行中 |

---

## 导航指南

### 我想知道...

| 问题 | 去哪里 |
|------|--------|
| 项目要做什么功能？ | [PRD-000.stock_app_overview.md](./specs/product/PRD-000.stock_app_overview.md) |
| 按类型执行变更流程？ | [workflows/](./workflows/README.md) |
| 整体开发计划是什么？ | [TRD-000.roadmap_phases.md](./specs/tech/TRD-000.roadmap_phases.md) |
| 个股页面怎么做？ | [PRD-003](./specs/product/PRD-003.single_stock_page.md) + [TRD-003](./specs/tech/TRD-003.single_stock_tech.md) |
| 数据源与质量规则？ | [DRD-005](./specs/BI/DRD-005.data_pipeline_ops.md) |
|| 流水线如何设计？ | [TRD-005](./specs/tech/TRD-005.cms_graph_admin.md) |
| 哪些需求已完成/待做？ | [todowrite.md](./project/BRN-001/todowrite.md) |
| 当前在做哪个 Phase？ | 本文件的"当前状态"表格 |
| 某个 Phase 的详细进展？ | [project/BRN-001/phrase_N/](./project/BRN-001/) |
| 用户说过什么指令？ | [project/BRN-001/prompt.md](./project/BRN-001/prompt.md) |
| AI 评分标准是什么？ | [IRD-001.ai_evaluation.md](./specs/infra/IRD-001.ai_evaluation.md) |

### AI 工作流程

1. 读 `AGENTS.md` → 了解强制规则
2. 读本文件 → 找到当前 Phase
3. 读 `project/phrase_N/README.md` → 了解当前目标
4. 读 `project/phrase_N/checklist.md` → 找到待做任务
5. 完成后更新 `project/BRN-001/todowrite.md` + `phrase_N/checklist.md`

---

## 已完成的里程碑

- ✅ Nx monorepo 初始化
- ✅ GraphQL schema 定义 (`libs/schema/schema.graphql`)
- ✅ Backend `/graphql` ping + Frontend 状态指示器
- ✅ `apps/regression/` E2E 测试框架
- ✅ `npm run dev` 一键启动
- ✅ Neo4j + Crawler 集成
- ✅ 单股页面 GraphQL 端点 + UI 骨架
- ✅ 文档体系治理（BRN/PRD/TRD 编号统一，specs/BI 目录调整）
- ✅ **BRN-002**: FastAPI + Strawberry GraphQL 架构迁移
  - 三层分离（Resolver → Service → Repository）
  - Schema 多域管理（common/market/news）
  - 共享数据访问层 `libs/neo4j_repo/`

---

## 项目目标

构建 AI-native 的量化选股工具，主要面向美股：
- 个股信息展示（K线、财务、新闻）
- 因子计算（PEG、PE、PS、PB）
- AI 对话创建策略
- 策略回测与推送
