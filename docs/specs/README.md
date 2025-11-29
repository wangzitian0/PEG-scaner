# Specs (Definitive Guides)

Finalized specifications for product/tech/BI/infra. Each domain follows `XRD-NNN` naming, inheriting BRN编号.

## 目录结构
```
specs/
├── product/    # PRD-NNN.md（产品需求：界面、交互、用户体验）
├── tech/       # TRD-NNN.md（技术规范：架构图、调用关系、Schema）
├── BI/         # DRD-NNN.md（数据运营：数据源、质量监控、BI Dashboard）
└── infra/      # IRD-NNN.md（基础设施：部署、CI/CD、监控）
```

## 编号规则
- BRN 编号统领，XRD 继承同编号
- 例：BRN-002 → TRD-002（技术）、无需 PRD-002/DRD-002（视业务需要）

## 参考
- [AGENTS.md](../../AGENTS.md) - 文档组织原则
- [index.md](../index.md) - 文档索引总表
