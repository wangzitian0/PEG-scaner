# BRN-002: 架构迁移（Strawberry + FastAPI）

## 状态
✅ **已完成** - 2024-11-30

## 迭代目标
将现有 Flask + Ariadne 架构迁移到 Strawberry + FastAPI，实现：
1. ✅ 独立 app 架构（backend/crawler/etl）
2. ✅ 共享 libs（neo4j_repo）
3. ✅ 三层分离（GraphQL → Service → Repository）
4. ✅ Schema 多域管理（common/market/news）

## 对应文档
- **决策文档**：[BRN-002](../../origin/BRN-002.graphql_protocol_decision.md)
- **技术规范**：[TRD-002](../../specs/tech/TRD-002.strawberry_fastapi.md)
- **技术现状**：[context.md](./context.md)
- **指令记录**：[prompt.md](./prompt.md)
- **任务清单**：[todowrite.md](./todowrite.md)

## 完成的 Phase 列表
| Phase | 任务 | 状态 | 验收标准 |
|-------|------|------|---------|
| 1 | 环境准备 | ✅ 完成 | requirements.txt 更新成功 |
| 2 | Schema 拆分 | ✅ 完成 | merge_schema.py 生成 schema.graphql |
| 3 | 创建 libs/neo4j_repo | ✅ 完成 | 单元测试通过 |
| 4 | backend 新目录 | ✅ 完成 | 目录创建完成 |
| 5 | 迁移逻辑 | ✅ 完成 | uvicorn 启动，ping 成功 |
| 6 | 测试更新 | ✅ 完成 | backend:test 全绿 |
| 7 | 清理文档 | ✅ 完成 | 旧代码重命名，文档更新 |

## 验收标准（已满足）
- ✅ `uvicorn apps.backend.main:app` 启动成功
- ✅ `/graphql` Playground 可访问（dev 环境）
- ✅ `nx run backend:test` 全绿（6 passed）
- ✅ 代码符合三层分离（Resolver → Service → Repository）
- ✅ `libs/neo4j_repo/` 可被未来 crawler/etl 复用
- ✅ 文档更新完整

## 关键产物

### 新增文件
- `apps/backend/main.py` - FastAPI 入口
- `apps/backend/resolvers/` - Strawberry 解析器
- `apps/backend/services/` - 业务逻辑层
- `libs/neo4j_repo/` - 共享数据访问层
- `libs/schema/{common,market,news}/` - Schema 子域

### 修改文件
- `apps/backend/requirements.txt` - 新增 FastAPI/Strawberry
- `apps/backend/project.json` - uvicorn 启动命令
- `libs/schema/schema.graphql` - 自动生成

### Legacy 备份
- `apps/backend/src/pegserver_legacy/` - 原 Flask 代码

## 下一步
- 运行 `regression:ping` 和 `regression:web-e2e` 完成端到端验证
- 开始 BRN-003 个股页面完整实现
