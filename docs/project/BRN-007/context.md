# BRN-007 技术现状与背景

## 基线
- 目标：五套环境（dev/ci/test/staging/prod）通过 Docker Compose 分层 + Vault 管理密钥/环境变量，实现一键启动/部署。
- 决策来源：`docs/origin/BRN-007.app_env_design.md`；技术/基础设施方案见 `TRD-007`、`IRD-007`。
- 现有资产：历史 BRN-004 环境文件、`tools/dev.sh`、GitHub Actions、docker-compose*.yml（待确认分层）。

## 当前状态（待补充）
- 分层 Compose 是否已落地 base + overrides：未核实。
- Vault 集成范围与默认值：未记录。
- PR 预览、staging dump、回滚策略：未记录。

## 待补充动作
- [ ] 盘点现有 compose/脚本与 IRD-007 差距。
- [ ] 补充环境变量清单（与 `.env.ci` 对齐）。
- [ ] 记录已知风险/阻塞与验证方法。
