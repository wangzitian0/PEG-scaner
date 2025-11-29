# BRN-001: 核心基建与个股页面

## 迭代目标
1. 建立 GraphQL + Nx 基础设施
2. 实现 ping-pong 通路验证
3. 搭建个股页面骨架（UI + GraphQL 端点）

## 对应文档
- **决策文档**：[BRN-001](../../origin/BRN-001.core_infra_ping.md)
- **技术规范**：[TRD-001](../../specs/tech/TRD-001.infra_ping.md)
- **技术现状**：[context.md](./context.md)
- **指令记录**：[prompt.md](./prompt.md)
- **任务清单**：[todowrite.md](./todowrite.md)

## 当前状态
Phase 0 ✅ 完成，Phase 1 🚧 进行中

## Phase 列表
| Phase | 名称 | 状态 | 关键成果 |
|-------|------|------|---------|
| 0 | GraphQL & Nx 基础设施 | ✅ 完成 | Schema SSOT、Nx targets、ping-pong、回归测试 |
| 1 | 个股页面骨架 | 🚧 进行中 | GraphQL 端点、UI 骨架、Crawler 集成 |

## 验收标准
- ✅ `nx run backend:serve` 启动成功
- ✅ `nx run regression:ping` 通过
- ✅ `nx run regression:infra-flow` 通过
- ✅ `nx run regression:web-e2e` 通过
- ✅ Frontend 状态指示器显示绿色
- 🚧 个股页面加载成功（待数据源配置）

## 已完成里程碑
- ✅ Nx monorepo 初始化
- ✅ GraphQL schema 定义（`libs/schema/schema.graphql`）
- ✅ Backend `/graphql` ping 端点
- ✅ Frontend 状态指示器
- ✅ 回归测试框架（`apps/regression/`）
- ✅ Neo4j + Crawler 集成
- ✅ 个股页面 GraphQL 端点 + UI 骨架

## 下一步
1. 完成 Phase 1（数据源配置、多源校验）
2. 启动 BRN-002（架构迁移 Flask → FastAPI）

## 文件清单
- `prompt.md` - 用户指令（SSOT）
- `context.md` - 技术现状与执行历史
- `todowrite.md` - 任务清单
- `README.md` - 本文件
- `_archive_phase_content.md` - Phase 0/1 详细历史归档（工作流程、checklist 完整版）

## 参考
- [docs/index.md § 当前状态](../../index.md)
- [TRD-001 § 验收标准](../../specs/tech/TRD-001.infra_ping.md#8-验收标准)
- [_archive_phase_content.md](./_archive_phase_content.md) - 历史执行细节
