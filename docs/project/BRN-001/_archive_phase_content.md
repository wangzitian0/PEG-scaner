# BRN-001: Phase 历史内容归档

> 本文件记录从 phrase_0.infra/ 和 phrase_1.single_stock_page/ 删除的内容，确保无遗漏。

---

## Phase 0: GraphQL & Nx 基础设施

### 核心目标（来自 phrase_0.infra/README.md）
- 维护 GraphQL schema 作为 SSOT
- 保持 Nx 配置就绪
- 提供 onboarding 指南
- 托管共享回归测试

### 关键任务（来自 phrase_0.infra/checklist.md）
- [x] GraphQL schema 覆盖 ping/pegStocks/singleStock 需求
- [x] 移除 protobuf codegen flow，改为 GraphQL SDL
- [x] 文档化 GraphQL 使用
- [x] 审计 nx.json + project configs，添加 targets
- [x] 添加新增 Nx 项目的说明
- [x] 实现并验证 ping-pong flow（GraphQL）
- [x] 添加 regression:infra-flow（backend + Vite 联通）
- [x] 添加 Playwright regression（web-e2e）

### 工作流程（来自 phrase_0.infra/iteration_flow.md）
1. **Pre-work**：读 AGENTS.md + IRD-001 + prompt.md
2. **执行循环**：
   - Schema 变更：更新 SDL → 对齐 resolver/hooks → 跑测试
   - Neo4j 连接：确保 NEO4J_URI 等环境变量
   - Nx 任务：编辑配置 → `nx graph` / `nx run` 验证
   - 记录日志到 x-log/
3. **文档扫描**：更新 README（本阶段 → 上层）
4. **交接**：记录风险/TODO 到 checklist

### 部署指南（来自 phrase_0.infra/deploy.md）
**已整合到 TRD-001 § 6.2**

### 用户 Prompt（来自 phrase_0.infra/append_promot.md）
**已整合到 project/BRN-001/prompt.md** (Prompt 7-11, 13)

### 工作计划（来自 phrase_0.infra/plan.md）
| 工作包 | 描述 | 状态 |
|--------|------|------|
| Schema Governance | 维护 schema.graphql SSOT | Pending |
| Nx Workspace Health | 保持 nx.json 和 project configs 更新 | Pending |
| Resolver & Client Alignment | 保持 resolver/client 与 SDL 对齐 | Pending |
| Infra Documentation | 文档化其他 phase 如何使用 GraphQL/Nx | Completed |
| Nx Targets | 添加 backend:test, mobile:typecheck, regression:ping | Completed |
| Tooling Verification | 定期运行 nx graph, lint, smoke tests | Completed |
| Ping-Pong Flow | Backend ping + mobile 指示器 + regression 脚本 | Completed |

**里程碑**：
- M0: 建立文档占位
- M1: GraphQL schema 被前后端/回归共用
- M2: Nx targets 正式化

**风险与缓解**：
- 风险：Schema drift（SDL 与实现不一致）
- 缓解：SDL 变更后运行 regression ping

---

## Phase 1: 个股页面

### 核心目标（来自 phrase_1.single_stock_page/README.md）
- 捕获所有用户 prompt，保持可审计
- 定义个股页面的 scope、backlog、质量门
- 明确日常工作流程

### 关键任务（来自 phrase_1.single_stock_page/checklist.md）
- [x] 创建 phrase_1 迭代文件夹
- [x] 追加 prompt 到 ../prompt.md
- [x] 捕获基线目录树
- [x] 运行 backend:test（当前 0 tests）
- [ ] 草拟个股数据源蓝图（K 线、新闻、F10、因子，验证流程）
- [ ] 映射 schema.graphql 类型到 backend/mobile 组件
- [x] 明确 agent 奖励机制（IRD-001 + AGENTS.md 强制要求）
- [x] 确保每个 agent 必须先读 IRD-001
- [ ] 产生实施 tickets：
  - [ ] Backend single-stock GraphQL API（K 线 + F10）
  - [ ] 因子计算服务（PEG）
  - [ ] Mobile single-stock UI 骨架
- [ ] 更新 ../todowrite.md
- [x] 实现 backend singleStock GraphQL resolver
- [x] 实现 mobile single-stock UI 骨架
- [x] 支持 URL ?symbol= 参数查询
- [x] 添加 crawler app + Flask-Admin 管理爬虫任务

### 工作流程（来自 phrase_1.single_stock_page/iteration_flow.md）
1. **Morning Sync**：
   - 重读 AGENTS.md + IRD-001 + todowrite + checklist
   - 追加新 prompt 到 prompt.md
   - 重新排序 plan.md backlog
2. **工作块执行**：
   - 选择最高优先级任务
   - 编辑前检查现有 docs/code（SSOT 规则）
   - 实现 → 测试 → 记录
3. **文档扫描**：
   - 更新触及目录的 README → 冒泡到根 README
   - 更新 checklist + 记录阻塞
4. **交接**：
   - 确保 todowrite 反映未满足需求
   - 总结会话（完成/待完成）

### 用户 Prompt（来自 phrase_1.single_stock_page/append_promot.md）
**已整合到 project/BRN-001/prompt.md** (Prompt 2-7, 13)

### 工作计划（来自 phrase_1.single_stock_page/plan.md）
| 工作包 | 描述 | 状态 |
|--------|------|------|
| Prompt Logging | 保持 prompt.md 更新 | Completed |
| Iteration Docs | 维护 plan/checklist/flow | Completed |
| Data Source Blueprint | 列举 K 线/新闻/F10/因子候选供应商，描述验证流程 | Todo |
| Schema Alignment | 映射 schema.graphql 到 backend/mobile | Todo |
| Agent Reward Design | 草拟奖励信号 | Completed |
| Single Stock Data Flow | 定义数据源和 API 合约 | Completed (GraphQL endpoint) |
| UI Skeleton | 设计并搭建 UI（图表/新闻占位） | Completed |
| Crawler + Neo4j | Bootstrap crawler app, admin, Neo4j 数据管道 | Completed |
| Evaluation Adoption | 强制 IRD-001 via AGENTS.md | In Progress |
| Execution Tracking | 更新 README/index.md/todowrite | In Progress |
| BRN Alignment | 维护 BRN-003 作为 scope guardrail | New |
| Baseline Snapshot | 捕获 repo 树和 smoke tests | Completed |

**里程碑**：
- M1: Prompt log 和迭代脚手架就绪
- M2: 数据源蓝图 + schema gap 分析批准
- M3: 初始实施 tickets（backend/mobile K 线 fetcher、PEG 计算器、UI stubs）

**依赖**：
- 访问 backend/mobile 代码库
- 数据供应商/API 协议（可能需要凭证）
- 验证工具（浏览器自动化/手工检查）

**风险与缓解**：
- 风险：数据供应商不可用或限流 → 缓解：准备多候选和缓存规则
- 风险：文档漂移 → 缓解：通过 checklist 锁定流程，强制 README 更新
- 风险：奖励机制不清晰 → 缓解：草拟具体指标（测试覆盖率、需求完成度、数据验证计数）

---

## 内容完整性检查

### ✅ 已妥善整合的内容
| 原文件 | 核心内容 | 新位置 |
|--------|---------|--------|
| `phrase_0.infra/README.md` | Phase 0 目标、可交付成果 | **project/BRN-001/context.md § Phase 0** |
| `phrase_0.infra/plan.md` | 工作包、里程碑、风险 | **TRD-001**（技术规范） + **context.md** |
| `phrase_0.infra/checklist.md` | 具体任务清单 | **project/BRN-001/todowrite.md**（合并） + **context.md** |
| `phrase_0.infra/deploy.md` | 部署步骤、文件说明 | **TRD-001 § 6.2**（部署流程） |
| `phrase_0.infra/iteration_flow.md` | 工作流程细节 | **本文件归档**（供参考） |
| `phrase_0.infra/append_promot.md` | Prompt 片段 | **project/BRN-001/prompt.md**（完整版） |
| `phrase_1.single_stock_page/README.md` | Phase 1 目标 | **project/BRN-001/context.md § Phase 1** |
| `phrase_1.single_stock_page/plan.md` | 工作包、里程碑 | **PRD-003** + **TRD-003** + **context.md** |
| `phrase_1.single_stock_page/checklist.md` | 任务清单 | **project/BRN-001/todowrite.md** + **context.md** |
| `phrase_1.single_stock_page/iteration_flow.md` | 工作流程 | **本文件归档** |
| `phrase_1.single_stock_page/append_promot.md` | Prompt 片段 | **project/BRN-001/prompt.md** |

### ⚠️ 仅归档（非核心内容，作参考）
- **iteration_flow.md**（两个 phase）：具体工作流程细节，已提炼要点到 context.md，完整版保存在本归档文件
- **append_promot.md**（两个 phase）：Prompt 片段索引，完整版在 prompt.md

---

## 结论
✅ **所有核心内容都已保留**，分布在：
1. **TRD-001**（技术规范 + 部署指南）
2. **PRD-003/TRD-003**（产品/技术设计）
3. **project/BRN-001/context.md**（历史执行记录）
4. **project/BRN-001/todowrite.md**（任务清单）
5. **project/BRN-001/prompt.md**（完整指令）
6. **本归档文件**（工作流程细节，供参考）

