# BRN-002: 架构迁移（Strawberry + FastAPI）

## 迭代目标
将现有 Flask + Ariadne 架构迁移到 Strawberry + FastAPI，实现：
1. 独立 app 架构（backend/crawler/etl）
2. 共享 libs（neo4j-repo）
3. 三层分离（GraphQL → Service → Repository）
4. Schema 多域管理（common/market/news）

## 对应文档
- **决策文档**：[BRN-002](../../origin/BRN-002.graphql_protocol_decision.md)
- **技术规范**：[TRD-002](../../specs/tech/TRD-002.strawberry_fastapi.md)
- **技术现状**：[context.md](./context.md)
- **指令记录**：[prompt.md](./prompt.md)
- **任务清单**：[todowrite.md](./todowrite.md)

## 当前状态
📋 **Phase 0 规划** - 等待用户 review

## Phase 列表（详见 TRD-002 § 9）
| Phase | 任务 | 状态 | 验收标准 |
|-------|------|------|---------|
| 1 | 环境准备 | 📋 待开始 | requirements.txt 更新成功 |
| 2 | Schema 拆分 | 📋 待开始 | merge_schema.py 生成 schema.graphql |
| 3 | 创建 libs/neo4j-repo | 📋 待开始 | 单元测试通过 |
| 4 | backend 新目录 | 📋 待开始 | 目录创建完成 |
| 5 | 迁移逻辑 | 📋 待开始 | uvicorn 启动，ping 成功 |
| 6 | 测试更新 | 📋 待开始 | backend:test + regression:ping 全绿 |
| 7 | 清理文档 | 📋 待开始 | 旧代码删除，文档更新 |

## 验收标准
- ✅ `uvicorn apps.backend.main:app` 启动成功
- ✅ `/graphql` Playground 可访问（dev 环境）
- ✅ `nx run backend:test` 全绿
- ✅ `nx run regression:ping` 通过
- ✅ `nx run regression:web-e2e` 通过
- ✅ 代码符合三层分离
- ✅ `libs/neo4j-repo` 可被未来 crawler/etl 复用

## 关键决策
1. **去掉 `src/` 层级**：`apps/backend/main.py`（不是 `src/main.py`）
2. **独立 app**：backend/crawler/etl 各自独立部署
3. **共享 libs**：`libs/neo4j-repo/` 供所有 app 使用
4. **分 7 个 Phase**：环境 → Schema → libs → 目录 → 逻辑 → 测试 → 清理

## 下一步
用户 review [TRD-002 § 9 实施计划](../../specs/tech/TRD-002.strawberry_fastapi.md#9-实施计划)，确认后开始 Phase 1 执行。
