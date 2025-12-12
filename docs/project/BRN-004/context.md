# BRN-004 技术现状与背景

## 基线
- 目标：提供 dev/ci/test/staging/prod 五套环境的一键部署与运行方案。
- 现有资产：`docker-compose.yml`（生产）、`docker-compose.dev.yml`（开发），CI 已有 GitHub Actions。
- 方案参考：`TRD-004.env_eaas_implementation.md`、`IRD-004.env_eaas_infra.md`、infra 仓库 <https://github.com/wangzitian0/infra/blob/main/docs/BRN-004.env_eaas_design.md>。

## 当前状态
- 运行时改为 k3s + Kubero + Kubero UI；Traefik/Vault 集成仍在规划中。
- 一键启动入口：`npm run dev` / `tools/dev.sh`（需验证环境注入与依赖启动）。

## 待补充
- [ ] 回填具体指令与依赖清单（端口、环境变量、密钥来源）。
- [ ] 记录当前阻塞项与已知问题（对齐 `todowrite.md`）。
- [ ] 补充监控/回滚策略与验证方法。
