# 文档索引

> **AI 阅读入口**：从 `AGENTS.md` 进入，到本文件找到"对的位置"

---

## 文件职责定义

| 文件 | 职责 | 更新时机 | 谁写 |
|------|------|----------|------|
| **本文件 (index.md)** | 索引 + 当前状态总览 | 每次迭代结束 | Agent |
| **[PRD-001.md](./specs/product/PRD-001.md)** | 产品需求原文（界面/功能定义） | 用户修改需求时 | 用户 |
| **[TRD-001.md](./specs/tech/TRD-001.md)** | 开发路线图（Phase 1-5 高层规划） | 规划调整时 | Agent |
| **[todowrite.md](./project/BRN-001/todowrite.md)** | 需求完成状态跟踪（打勾用） | 每次完成任务后 | Agent |
| **[IRD-001.md](./specs/infra/IRD-001.md)** | AI 评分机制详细说明 | 机制变更时 | Agent |
| **[project/BRN-001/README.md](./project/BRN-001/README.md)** | 迭代管理规范 + 当前 Phase 状态 | Phase 状态变更时 | Agent |
| **[project/BRN-001/prompt.md](./project/BRN-001/prompt.md)** | 用户指令日志（SSOT） | 每次收到指令后 | Agent |
| **project/BRN-001/phrase_N.xxx/** | 单个迭代的详细记录 | 迭代进行中 | Agent |

---

## 当前状态

| Phase | 名称 | 状态 | 详情 |
|-------|------|------|------|
| 0 | Proto & Nx 基础设施 | ✅ Active | [phrase_0.infra/](./project/BRN-001/phrase_0.infra/README.md) |
| 1 | 个股页面 | 🚧 In Progress | [phrase_1.single_stock_page/](./project/BRN-001/phrase_1.single_stock_page/README.md) |
| 2 | 因子计算 | 📋 Planned | 见 [TRD-001.md](./specs/tech/TRD-001.md) |
| 3 | AI 对话 | 📋 Planned | 见 [TRD-001.md](./specs/tech/TRD-001.md) |
| 4 | 策略回测 | 📋 Planned | 见 [TRD-001.md](./specs/tech/TRD-001.md) |
| 5 | 策略推送 | 📋 Planned | 见 [TRD-001.md](./specs/tech/TRD-001.md) |

---

## 导航指南

### 我想知道...

| 问题 | 去哪里 |
|------|--------|
| 项目要做什么功能？ | [PRD-001.md](./specs/product/PRD-001.md) |
| 整体开发计划是什么？ | [TRD-001.md](./specs/tech/TRD-001.md) |
| 哪些需求已完成/待做？ | [todowrite.md](./project/BRN-001/todowrite.md) |
| 当前在做哪个 Phase？ | 本文件的"当前状态"表格 |
| 某个 Phase 的详细进展？ | [project/BRN-001/phrase_N/](./project/BRN-001/) |
| 用户说过什么指令？ | [project/BRN-001/prompt.md](./project/BRN-001/prompt.md) |
| AI 评分标准是什么？ | [IRD-001.md](./specs/infra/IRD-001.md) |

### AI 工作流程

1. 读 `AGENTS.md` → 了解强制规则
2. 读本文件 → 找到当前 Phase
3. 读 `project/phrase_N/README.md` → 了解当前目标
4. 读 `project/phrase_N/checklist.md` → 找到待做任务
5. 完成后更新 `project/BRN-001/todowrite.md` + `phrase_N/checklist.md`

---

## 已完成的里程碑

- ✅ Nx monorepo 初始化
- ✅ Protobuf schema 定义 (`libs/schema/`)
- ✅ Backend `/api/ping/` + Frontend 状态指示器
- ✅ `apps/regression/` E2E 测试框架
- ✅ `npm run dev` 一键启动
- ✅ Neo4j + Crawler 集成
- ✅ 单股页面 protobuf 端点 + UI 骨架

---

## 项目目标

构建 AI-native 的量化选股工具，主要面向美股：
- 个股信息展示（K线、财务、新闻）
- 因子计算（PEG、PE、PS、PB）
- AI 对话创建策略
- 策略回测与推送
