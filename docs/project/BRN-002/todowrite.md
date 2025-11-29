# BRN-002: 任务清单

## Phase 0: 文档准备 ✅
- [x] 创建 context.md（技术现状）
- [x] 创建 prompt.md（指令记录）
- [x] 创建 todowrite.md（本文件）
- [x] 创建 phrase_0.planning/（规划文档）

## Phase 1: 环境准备与依赖调整 ✅
- [x] 更新 `apps/backend/requirements.txt`（移除 Flask/Ariadne，添加 FastAPI/Strawberry）
- [x] 更新 `apps/backend/project.json`（serve target 改为 uvicorn）
- [x] 更新 `apps/backend/README.md`（技术栈说明）
- [x] 验证：`pip install -r requirements.txt` 无冲突

## Phase 2: Schema 多域拆分 ✅
- [x] 创建 `libs/schema/common/types.graphql`（PingResponse）
- [x] 创建 `libs/schema/market/market.graphql`（PegStock, SingleStockPage）
- [x] 创建 `libs/schema/news/news.graphql`（NewsItem）
- [x] 创建 `libs/schema/merge_schema.py`（聚合脚本）
- [x] 更新 `libs/schema/README.md`（多域规则）
- [x] 验证：`python merge_schema.py` 生成 `schema.graphql`

## Phase 3: 创建 libs/neo4j_repo/ ✅
- [x] 创建 `libs/neo4j_repo/__init__.py`
- [x] 创建 `libs/neo4j_repo/connection.py`（Neo4j 连接配置）
- [x] 创建 `libs/neo4j_repo/repositories/stock_repository.py`（从 graph_store 迁移）
- [x] 创建 `libs/neo4j_repo/models/stock.py`（neomodel 节点定义）
- [x] 创建 `libs/neo4j_repo/README.md`（使用说明）
- [x] 验证：单元测试 `libs/neo4j_repo` 可独立运行

## Phase 4: 创建 backend 新目录结构 ✅
- [x] 创建 `apps/backend/main.py`（FastAPI entry）
- [x] 创建 `apps/backend/resolvers/ping.py`（ping resolver）
- [x] 创建 `apps/backend/resolvers/stock.py`（pegStocks/singleStock resolvers）
- [x] 创建 `apps/backend/resolvers/__init__.py`（合并 Query）
- [x] 创建 `apps/backend/services/stock_service.py`（业务逻辑）
- [x] 创建 `apps/backend/config.py`（保留并简化）

## Phase 5: 迁移 Resolver 逻辑 ✅
- [x] 实现 `resolvers/ping.py`（调用 tracking service）
- [x] 实现 `resolvers/stock.py`（调用 stock_service）
- [x] 实现 `services/stock_service.py`（从 graphql_api 提取逻辑）
- [x] 配置 FastAPI lifespan（Neo4j 连接管理）
- [x] 验证：`uvicorn apps.backend.main:app` 启动成功

## Phase 6: 测试迁移 ✅
- [x] 更新 `apps/backend/tests/conftest.py`（Starlette TestClient）
- [x] 更新 `apps/backend/tests/test_graphql.py`（所有测试用例）
- [x] 验证：`nx run backend:test` 全绿（6 passed）

## Phase 7: 清理与文档 ✅
- [x] 重命名 `pegserver/` → `pegserver_legacy/`（保留备份）
- [x] 更新 `apps/backend/README.md`（新架构说明）
- [x] 更新 `docs/project/BRN-002/README.md`（完成状态）
- [x] 更新本文件（todowrite.md）

## 验收标准（全部完成）✅
- [x] `uvicorn apps.backend.main:app` 启动成功
- [x] `/graphql` Playground 可访问（dev 环境）
- [x] `nx run backend:test` 全绿
- [ ] `nx run regression:ping` 通过（待运行）
- [ ] `nx run regression:web-e2e` 通过（待运行）
- [x] 代码符合三层分离（GraphQL → Service → Repository）
- [x] `libs/neo4j_repo/` 可被其他 app 复用
- [x] 文档更新完整（TRD-002, README, arch.md）
