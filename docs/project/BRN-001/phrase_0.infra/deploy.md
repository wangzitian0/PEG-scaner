# 部署指南

**成功标准**：访问 `https://yourdomain.com`，看到页面左上角的小绿点

---

## 方式 A: Dokploy 部署（推荐）

### Step 1: 推送代码

```bash
git add docker-compose.yml apps/backend/Dockerfile apps/mobile/Dockerfile apps/mobile/nginx.conf
git commit -m "Add Docker deployment files"
git push
```

### Step 2: 在 Dokploy 创建项目

1. 登录 Dokploy Dashboard
2. Create Project → Compose
3. 填写 Git 仓库地址
4. Deploy

### Step 3: 配置域名

Dokploy 项目设置 → Domains → 添加你的域名

### Step 4: 验证

访问 `https://yourdomain.com`，看到小绿点 ✅

---

## 方式 B: 手动 Docker Compose

```bash
# SSH 到 VPS
ssh user@your-vps-ip

# 拉代码
git clone <你的仓库> /opt/peg-scanner
cd /opt/peg-scanner

# 构建并启动
docker compose up -d --build

# 验证
curl -X POST http://localhost/graphql -H "Content-Type: application/json" -d '{"query":"{ ping { message } }"}'
```

---

## 文件说明

| 文件 | 用途 |
|------|------|
| `docker-compose.yml` | 定义 neo4j + backend + frontend |
| `apps/backend/Dockerfile` | Flask 后端 |
| `apps/mobile/Dockerfile` | Vite 构建 + Nginx |
| `apps/mobile/nginx.conf` | Nginx 配置，/graphql 代理到 backend |

---

## 排查

```bash
docker compose logs -f          # 查看日志
docker compose restart backend  # 重启某个服务
docker compose up --build -d    # 重新构建
```
