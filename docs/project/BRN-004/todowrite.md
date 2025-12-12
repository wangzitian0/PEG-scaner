# BRN-004 任务清单

## 核心目标
> dev/ci 要一键跑起来

## Docker Compose 结构

- [x] docker-compose.yml 生产配置
- [x] docker-compose.dev.yml 开发配置（含本地 DB）
- [ ] 验证 compose 语法通过 Dokploy
- [ ] 考虑是否改为 `compose.base.yml` + `compose.{env}.yml` 结构

## 一键启动（关键）

- [ ] `npm run dev` 或 `./tools/dev.sh` 一键启动本地全栈
- [ ] CI 一键跑测试（当前 `.github/workflows/ci.yml` 已有）
- [ ] 本地无需配置 Vault 也能跑（用默认值）

## Vault 集成

- [ ] 设计 Vault KV 路径与命名（dev/ci/test/staging/prod）
- [ ] `tools/dev.sh` 支持从 Vault 拉取/注入（可选）
- [ ] GitHub Actions/CI 与 Vault 的认证方式（如需要）

## 部署

- [ ] Dokploy 应用配置
- [ ] Traefik 路由规则
- [ ] 域名解析 (truealpha.club, api.*, cms.*)
- [ ] SSL 证书 (Cloudflare)

## PR 预览环境

- [ ] GitHub Actions workflow: `deploy-preview.yml`
- [ ] 动态域名 `pr-{number}.truealpha.club`
- [ ] PR 关闭后自动清理环境

## Staging 数据同步

- [ ] prod → staging 数据 dump 脚本
- [ ] 定期同步机制（cron 或手动）
- [ ] 敏感数据脱敏

## 监控

- [ ] 健康检查端点 `/health`
- [ ] 日志收集配置
- [ ] 告警规则

## 文档

- [x] IRD-004 基础设施规范
- [x] TRD-004 技术实现（含 tools/ 规范）
- [ ] 执行 tools/ 目录迁移（scripts/、ci/ 子目录）
- [ ] README 更新一键启动命令
