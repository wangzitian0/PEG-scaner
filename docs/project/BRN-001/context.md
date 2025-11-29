# BRN-001: 技术现状与执行历史

## 当前状态
**迭代目标**：核心基建（GraphQL + Nx + Ping）+ 个股页面骨架  
**状态**：Phase 0 ✅ 完成，Phase 1 🚧 进行中

## 技术栈（当前）
- **前端**：React Native (Expo) + Vite Web
- **后端**：Flask + Ariadne GraphQL（**待迁移到 FastAPI + Strawberry，见 BRN-002**）
- **数据库**：Neo4j + SQLite
- **Monorepo**：Nx
- **容器**：Podman/Docker Compose

## Phase 0: GraphQL & Nx 基础设施 ✅

### 目标
建立 GraphQL SDL 作为 SSOT，配置 Nx monorepo，实现 ping-pong 通路。

### 已完成工作
1. **Schema 管理**：`libs/schema/schema.graphql` 作为唯一源
2. **Backend Ping**：Flask `/graphql` 端点，返回 `{ ping { message, agent, timestampMs } }`
3. **Frontend 状态指示器**：Mobile app 显示 backend 连接状态
4. **Nx Targets**：
   - `backend:test` - 运行 GraphQL 测试
   - `mobile:typecheck` - TypeScript 检查
   - `regression:ping` - E2E ping 测试
   - `regression:infra-flow` - 基建流程测试
5. **回归测试**：Playwright 覆盖 ping 指示器
6. **Neo4j 集成**：neomodel + Crawler admin 后台

### 关键里程碑
- ✅ Backend `/graphql` ping 端点
- ✅ Mobile app 状态指示器
- ✅ Nx targets 配置完成
- ✅ 回归测试框架搭建
- ✅ Neo4j + Crawler 集成

### 风险与缓解
- **风险**：Schema drift（SDL 与实现不一致）
- **缓解**：SDL 变更后运行 regression ping

## Phase 1: 个股页面 🚧

### 目标
实现个股信息展示（K 线、新闻、F10），建立数据源验证流程。

### 当前进度
1. ✅ 创建 `project/BRN-001/todowrite.md`
2. ✅ 更新迭代管理文件
3. ✅ 创建 GraphQL 端点 `singleStock(symbol: String!)`
4. ✅ UI 骨架（watchlist + detail view）
5. ✅ Crawler + Neo4j 数据管道
6. 🚧 数据源蓝图（K 线/新闻/F10 供应商选择）
7. 🚧 3 源校验流程

### 待完成工作
- [ ] 数据源配置（yfinance/SEC/Alpha Vantage）
- [ ] 多源校验实现（≥3 来源）
- [ ] K 线图渲染
- [ ] 新闻列表展示
- [ ] F10 模块实现

### 关键决策
- 协议：GraphQL（对应 BRN-002/TRD-002）
- 产品需求：对应 BRN-003/PRD-003
- 数据质量：宁缺勿滥，≥3 来源校验

## 依赖关系
- **上游**：无（BRN-001 是起点）
- **下游**：
  - BRN-002（架构迁移，Flask → FastAPI）
  - BRN-003（个股页面完整实现）

## 参考文档
- [BRN-001: 核心基建决策](../../origin/BRN-001.core_infra_ping.md)
- [TRD-001: 技术规范](../../specs/tech/TRD-001.infra_ping.md)
- [BRN-002: GraphQL 协议](../../origin/BRN-002.graphql_protocol_decision.md)
- [BRN-003: 个股页面](../../origin/BRN-003.single_stock_page.md)
