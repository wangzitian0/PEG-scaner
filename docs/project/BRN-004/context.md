# BRN-004 技术现状与背景

## 基线
- 目标：提供 dev/ci/test/staging/prod 五套环境的一键部署与运行方案。
- 现有资产：`docker-compose.yml`（生产）、`docker-compose.dev.yml`（开发），CI 已有 GitHub Actions。
- 方案参考：`TRD-004.dev_test_prod_implementation.md`、`IRD-004.dev_test_prod_infra.md`。

## 当前状态
- Dokploy/Traefik/Infisical 集成仍在进行中。
- 一键启动入口：`npm run dev` / `tools/dev.sh`（需验证环境注入与依赖启动）。

## 待补充
- [ ] 回填具体指令与依赖清单（端口、环境变量、密钥来源）。
- [ ] 记录当前阻塞项与已知问题（对齐 `todowrite.md`）。
- [ ] 补充监控/回滚策略与验证方法。
