# Project - 迭代执行记录

记录每个 BRN 迭代的实时进度、决策日志、问题追踪。

## 目录结构

```
project/
├── BRN-001/           # 核心基建迭代
│   ├── prompt.md      # 用户指令（SSOT）
│   ├── context.md     # 技术现状
│   ├── todowrite.md   # 任务清单
│   └── README.md      # 迭代总览
├── BRN-002/           # 架构迁移迭代
│   ├── prompt.md
│   ├── context.md
│   ├── todowrite.md
│   └── README.md
└── BACKLOG.md         # 未来需求池
```

## 文件规范（严格限定）
每个 BRN-NNN/ 目录**仅允许 4 个文件**：
1. **prompt.md** - 用户指令记录（SSOT）
2. **context.md** - 技术现状与背景
3. **todowrite.md** - 任务清单（动态更新）
4. **README.md** - 迭代总览（Phase 列表、验收标准）

**不允许**：phrase_N/ 子目录（详细技术文档放 specs/）

## 迭代列表

| BRN | 名称 | 状态 | 详情 |
|-----|------|------|------|
| BRN-001 | 核心基建与个股页面 | 🚧 进行中 | [BRN-001/](./BRN-001/) |
| BRN-002 | 架构迁移（Strawberry + FastAPI） | 📋 规划中 | [BRN-002/](./BRN-002/) |
| BRN-003 | （占位） | 📋 未开始 | [BRN-003/](./BRN-003/) |

## 使用规范
- **prompt.md**：记录用户原始指令，每次收到新指令追加
- **context.md**：记录技术栈现状、已有代码、当前问题
- **todowrite.md**：动态任务清单，完成后打勾
- **phrase_N.xxxx/**：每个 Phase 独立目录，包含 plan/checklist/iteration_flow 等

## 参考
- [index.md](../index.md) - 文档索引
- [AGENTS.md](../../AGENTS.md) - 流程规范
