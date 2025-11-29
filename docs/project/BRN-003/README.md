# BRN-003: 个股页面完整实现

## 迭代目标
基于 BRN-001 已有的个股页面骨架，完善数据接入、UI 交互、测试覆盖。

## 对应文档
- **决策文档**：[BRN-003](../../origin/BRN-003.single_stock_page.md)
- **产品需求**：[PRD-003](../../specs/product/PRD-003.single_stock_page.md)
- **技术规范**：[TRD-003](../../specs/tech/TRD-003.single_stock_tech.md)

## 当前状态
📋 **未开始** - 等待 BRN-002 架构迁移完成

## 验收标准
- ✅ K 线图渲染（≥30 个数据点）
- ✅ 新闻列表显示（≥1 条或占位）
- ✅ F10 模块可展开/折叠
- ✅ 移动端适配（iPhone SE + iPad）
- ✅ 回归测试 `nx run regression:web-e2e` 通过

## 依赖
- BRN-002 完成（Strawberry + FastAPI 架构）
- 数据源配置完成（DRD-001，待创建）

## 参考
- [PRD-003 § 核心场景](../../specs/product/PRD-003.single_stock_page.md#3-核心场景)
- [TRD-003 § 整体架构](../../specs/tech/TRD-003.single_stock_tech.md#2-整体架构)
