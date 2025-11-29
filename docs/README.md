# PEG Scanner - Documentation

**AI 阅读入口**：从 [AGENTS.md](../AGENTS.md) 进入 → 本目录 → [index.md](./index.md) 找到对的位置

## 目录结构

```
docs/
├── index.md           # 索引总表 + 当前状态总览
├── arch.md            # 架构决策记录（5W1H）
├── origin/            # BRN-NNN.md（用户决策录，AI 只读）
├── specs/             # 各类规范文档（PRD/TRD/DRD/IRD）
│   ├── product/       # PRD - 产品需求
│   ├── tech/          # TRD - 技术规范
│   ├── BI/            # DRD - 数据运营与 BI
│   └── infra/         # IRD - 基础设施
└── project/           # 迭代执行记录（BRN-NNN/）
```

## 快速导航

| 我想... | 去哪里 |
|--------|--------|
| 了解当前做什么 | [index.md](./index.md) - 当前状态 |
| 查看技术架构 | [arch.md](./arch.md) |
| 了解产品需求 | [specs/product/](./specs/product/) |
| 查看技术实现 | [specs/tech/](./specs/tech/) |
| 了解数据运营 | [specs/BI/](./specs/BI/) |
| 查看迭代进度 | [project/](./project/) |

## 编号规则
- **BRN 编号统领**：如 BRN-002 → TRD-002/PRD-002（视需要）
- **XRD 继承编号**：PRD/TRD/DRD/IRD 继承对应 BRN 编号
- **文档独立性**：不是每个 BRN 都需要全部 XRD

## 文档原则
详见 [AGENTS.md § 文档组织原则](../AGENTS.md#docs-目录组织原则)
