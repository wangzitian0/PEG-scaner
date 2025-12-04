# BRN-004: 开发/测试/生产环境

## 概述

实现 5 套环境（dev/ci/test/staging/prod）的一键部署机制。

## 相关文档

| 类型 | 文档 | 状态 |
|------|------|------|
| BRN | [BRN-004.dev_test_prod_design.md](../../origin/BRN-004.dev_test_prod_design.md)<br>Infra 实现口径：<https://github.com/wangzitian0/infra/blob/main/docs/BRN-004.env_eaas_design.md> | ✅ |
| TRD | [TRD-004.env_eaas_implementation.md](../../specs/tech/TRD-004.env_eaas_implementation.md) | ✅ |
| IRD | [IRD-004.env_eaas_infra.md](../../specs/infra/IRD-004.env_eaas_infra.md) | ✅ |

## 当前状态

🚧 **进行中**

## 进度

| 任务 | 状态 | 备注 |
|------|------|------|
| docker-compose.yml 基础配置 | ✅ | 生产环境 |
| docker-compose.dev.yml 开发配置 | ✅ | 含本地数据库 |
| Infisical 集成 | 📋 | 待配置 |
| Dokploy 部署 | 🚧 | 调试中 |
| Traefik 路由 | 📋 | 待配置 |
| CI/CD 流程 | ✅ | GitHub Actions |

## 已知问题

- [ ] docker-compose.yml 语法需验证（cms.expose 格式）
- [ ] Infisical 环境变量待导入
