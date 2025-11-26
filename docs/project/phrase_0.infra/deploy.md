# Phase 0 Deploy TODOwrite

Cloudflare 代理 + 独立 VPS 部署路径（以当前 Nx monorepo：Python BE + RN/Vite 前端为基线）。按步骤执行，逐步勾掉，每一步都附带可执行的验证标准。

## 0. 预备条件
- 拥有 Cloudflare 域名管理权限，已知 VPS 公网 IP。
- VPS 上已有普通用户（非 root）和 sudo 权限；能够通过 SSH 登录。
- 已阅读 `AGENTS.md` / `docs/AI_EVALUATION.md`，并在当前迭代的 `iteration_flow.md` 记录时间戳。

## 1. Cloudflare DNS 与模式
- 操作：在 Cloudflare DNS 为根域和 `www` 添加 `A` 记录指向 VPS，开启橙色云（代理）。
- 测试标准：本地执行 `dig +short yourdomain.com` 返回 Cloudflare 节点 IP；`curl -I https://yourdomain.com` 响应 `Server: cloudflare`.

## 2. TLS（Full Strict）
- 操作：在 Cloudflare 生成 Origin Certificate（证书+私钥），拷贝到 VPS `/etc/ssl/cloudflare/{origin.crt,origin.key}`，Web 服务器引用。
- 测试标准：`openssl s_client -connect yourdomain.com:443 -servername yourdomain.com | grep -i \"Verify return code: 0\"`.

## 3. VPS 基线
- 操作：更新系统包；安装 `ufw` 开 22/80/443；安装 Docker + Docker Compose；同步时区。
- 测试标准：`docker --version`、`docker compose version` 正常；`ufw status` 显示规则仅放行需要的端口。

## 4. 代码与环境变量
- 操作：将仓库拉到 VPS（或拉取 CI 产物）。在仓库根放 `.env.prod`（不入仓库），包含 API keys/DB/`ENV` 路径；`tools/dev.sh` 可读取 `$ENV` 指定文件。
- 测试标准：`test -f .env.prod` 通过；`ENV=.env.prod ./tools/dev.sh status`（如有）输出无报错，或 `source .env.prod && printenv | head` 可见关键变量。

## 5. 构建产物
- 操作（示例）：使用 Docker 化部署。
  - 后端：基于 `python:3.11-slim` 构建镜像，启动 `gunicorn`/`uvicorn` 暴露 8000。
  - 前端：`nx build` 产出 Vite 静态资源，挂载到 Caddy/Nginx。
  - 反代：Caddy/Nginx 终止 TLS，`/api` 反向代理到后端容器。
- 测试标准：`docker compose config` 成功渲染；`docker compose build` 退出码 0。

## 6. 运行与健康检查
- 操作：`docker compose up -d`。确保反代、后端、静态资源容器都在运行。
- 测试标准：
  - `docker compose ps` 所有服务 `running`。
  - 内网：`curl -f http://localhost:8000/api/ping/` 返回 200（或等价健康路由）。
  - 外网：`curl -I https://yourdomain.com` 返回 200/301；`curl -f https://yourdomain.com/api/ping/` 通过。

## 7. Cloudflare 侧安全/缓存
- 操作：WAF 常用规则开启；为 `/api/*` 配置 Rate Limiting；静态文件按需 Cache Everything，API 路径设 Bypass。
- 测试标准：Cloudflare 仪表盘看到规则启用；`curl -I https://yourdomain.com/main.js` 返回 `CF-Cache-Status: HIT`（静态）；`curl -I https://yourdomain.com/api/ping/` 无缓存标头。

## 8. 可观测性与回滚
- 操作：为服务添加健康探针 `/health`；日志挂载到持久卷；准备 `docker compose pull && docker compose up -d` 回滚流程。
- 测试标准：`curl -f https://yourdomain.com/health` 成功；`docker compose logs --tail=20` 可看到最新日志；在拉取旧镜像后服务能恢复。

## 9. 自动化（后续项）
- 操作：CI 推镜像到私有/公有仓库；使用 GitHub Actions SSH 到 VPS 执行 `docker compose pull && docker compose up -d --remove-orphans`。
- 测试标准：CI 任务产出镜像 tag；部署后第 6 步的健康检查通过。

> 完成每步后，在 `checklist.md` 勾选对应条目并记录命令输出（如需）到 `x-log/`。如有新提示词，先追加到 `../prompt_log.md` 再同步到本阶段 `append_promot.md`。
