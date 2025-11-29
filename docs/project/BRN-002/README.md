# BRN-002: 架构迁移（Strawberry + FastAPI）

## 迭代目标
将现有 Flask + Ariadne 架构迁移到 Strawberry + FastAPI，实现三层分离与 Schema 多域管理。

## 对应文档
- **决策文档**：[BRN-002](../../origin/BRN-002.graphql_protocol_decision.md)
- **技术规范**：[TRD-002](../../specs/tech/TRD-002.strawberry_fastapi.md)

## 当前状态
📋 **规划中** - 等待 BRN-001 Phase 1 完成后启动

## 验收标准
- ✅ `uvicorn apps.backend.src.main:app` 启动成功
- ✅ `/graphql` Playground 可访问（开发环境）
- ✅ `pytest apps/backend/tests/` 全绿
- ✅ `nx run regression:ping` 通过
- ✅ 代码符合三层分离（GraphQL → Service → Repository）

## 迁移计划（草案）
1. Phase 0: 环境准备（requirements.txt, Nx targets）
2. Phase 1: Schema 多域拆分（libs/schema/）
3. Phase 2: 三层目录创建（api/core/infra）
4. Phase 3: Resolver 迁移（ping → pegStocks → singleStock）
5. Phase 4: 测试更新与回归验证
6. Phase 5: 删除 Flask 遗留代码

## 参考
- [迁移流程详细规划](../../specs/tech/TRD-002.strawberry_fastapi.md#9-迁移路径flask--fastapi)
