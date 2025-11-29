# BRN-002: 任务清单

## Phase 0: 文档准备 ✅
- [x] 创建 context.md（技术现状）
- [x] 创建 prompt.md（指令记录）
- [x] 创建 todowrite.md（本文件）
- [x] 创建 phrase_0.planning/（规划文档）

## Phase 1: 环境准备与依赖调整
- [ ] 更新 `apps/backend/requirements.txt`（移除 Flask/Ariadne，添加 FastAPI/Strawberry）
- [ ] 更新 `apps/backend/project.json`（serve target 改为 uvicorn）
- [ ] 更新 `apps/backend/README.md`（技术栈说明）
- [ ] 验证：`pip install -r requirements.txt` 无冲突

## Phase 2: Schema 多域拆分
- [ ] 创建 `libs/schema/common/types.graphql`（PingResponse）
- [ ] 创建 `libs/schema/market/market.graphql`（PegStock, SingleStockPage）
- [ ] 创建 `libs/schema/news/news.graphql`（占位）
- [ ] 创建 `libs/schema/merge_schema.py`（聚合脚本）
- [ ] 更新 `libs/schema/README.md`（多域规则）
- [ ] 验证：`python merge_schema.py` 生成 `schema.graphql`

## Phase 3: 创建 libs/neo4j-repo/
- [ ] 创建 `libs/neo4j-repo/project.json`（Nx lib 配置）
- [ ] 创建 `libs/neo4j-repo/connection.py`（Neo4j 连接配置）
- [ ] 创建 `libs/neo4j-repo/repositories/stock_repository.py`（从 graph_store 迁移）
- [ ] 创建 `libs/neo4j-repo/models/stock.py`（neomodel 节点定义）
- [ ] 创建 `libs/neo4j-repo/README.md`（使用说明）
- [ ] 验证：单元测试 `libs/neo4j-repo` 可独立运行

## Phase 4: 创建 backend 新目录结构
- [ ] 创建 `apps/backend/main.py`（FastAPI entry）
- [ ] 创建 `apps/backend/graphql/ping.py`（ping resolver）
- [ ] 创建 `apps/backend/graphql/stock.py`（pegStocks/singleStock resolvers）
- [ ] 创建 `apps/backend/graphql/__init__.py`（合并 Query）
- [ ] 创建 `apps/backend/services/stock_service.py`（业务逻辑）
- [ ] 创建 `apps/backend/config.py`（保留并简化）

## Phase 5: 迁移 Resolver 逻辑
- [ ] 实现 `graphql/ping.py`（调用 tracking service）
- [ ] 实现 `graphql/stock.py`（调用 stock_service）
- [ ] 实现 `services/stock_service.py`（从 graphql_api 提取逻辑）
- [ ] 配置 FastAPI lifespan（Neo4j 连接管理）
- [ ] 验证：`uvicorn apps.backend.main:app` 启动成功

## Phase 6: 测试迁移
- [ ] 更新 `apps/backend/tests/conftest.py`（FastAPI TestClient）
- [ ] 更新 `apps/backend/tests/test_graphql.py`（所有测试用例）
- [ ] 验证：`nx run backend:test` 全绿
- [ ] 验证：`nx run regression:ping` 通过

## Phase 7: 清理与文档
- [ ] 重命名 `pegserver/` → `pegserver_legacy/`（保留备份）
- [ ] 删除旧代码（确认回归测试全绿后）
- [ ] 更新 `apps/backend/Dockerfile`（CMD 改为 uvicorn）
- [ ] 更新 `tools/dev.sh`（启动命令）
- [ ] 更新 `docs/project/BRN-002/completion_report.md`（完成报告）
- [ ] 验证：`nx run-many --target=test --all` 全绿

## 验收标准（全部完成后）
- [ ] `uvicorn apps.backend.main:app` 启动成功
- [ ] `/graphql` Playground 可访问（dev 环境）
- [ ] `nx run backend:test` 全绿
- [ ] `nx run regression:ping` 通过
- [ ] `nx run regression:web-e2e` 通过
- [ ] 代码符合三层分离（GraphQL → Service → Repository）
- [ ] `libs/neo4j-repo/` 可被其他 app 复用
- [ ] 文档更新完整（TRD-002, README, arch.md）

