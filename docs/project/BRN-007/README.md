# BRN-007: 应用开发/测试/生产环境机制

## 概述
构建 dev/ci/test/staging/prod 五套环境的一键启动与部署机制，使用 Docker Compose 分层结构 + Vault 管理环境变量/密钥，保持配置单一真理源且无敏感信息入仓。

## 对应文档
- **决策**：[BRN-007.app_env_design.md](../../origin/BRN-007.app_env_design.md)
- **技术规范**：[TRD-007.app_env_implementation.md](../../specs/tech/TRD-007.app_env_implementation.md)
- **基础设施**：[IRD-007.app_env_infra.md](../../specs/infra/IRD-007.app_env_infra.md)

## 当前状态
🚧 进行中 — 已有 Compose 方向，但具体执行记录缺失，需要补全指令与任务分解。

## 验收标准（待细化）
- dev/ci/test/staging/prod 可通过统一脚本/命令一键启动。
- 所有敏感配置通过 Vault 注入/读取，仓库不含真实密钥。
- Compose 分层（base + overrides）清晰，`docker compose config` 可验证最终配置。
- 回滚与预览环境（PR）流程可复现，文档同步。

## 依赖与参考
- BRN-004 历史资产（环境/Compose 文件）。
- 现有工具：`tools/dev.sh`、GitHub Actions。

## 进度记录
- 指令与执行轨迹：见本目录 `prompt.md`、`todowrite.md`、`context.md`。
