# Tools

自动化脚本和部署工具。

---

## Dokploy 部署

### 首次部署

#### 1. 创建服务

在 Dokploy 控制台创建：

| 服务 | 类型 | 说明 |
|------|------|------|
| `postgres` | Database → PostgreSQL | 内置服务 |
| `neo4j` | Docker Compose | 或外部托管 |
| `cms` | Application → Docker | Django CMS |
| `backend` | Application → Docker | FastAPI |

#### 2. 配置环境变量

在每个 Application 的 **Environment** 面板设置：

**cms 服务:**
```
PEG_ENV=prod
DEBUG=False
DATABASE_URL=postgres://user:pass@postgres:5432/pegscanner
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=xxx
JWT_SECRET_KEY=xxx
DJANGO_SECRET_KEY=xxx
DJANGO_ALLOWED_HOSTS=your-domain.com,cms
```

**backend 服务:**
```
PEG_ENV=prod
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=xxx
```

#### 3. 首次部署后初始化

```bash
# SSH 进入服务器，或使用 Dokploy Terminal

# 进入 cms 容器
docker exec -it <cms-container> bash

# 运行 migrations
python manage.py migrate

# 创建管理员
python manage.py createsuperuser

# Neo4j constraints (在 backend 容器或本地)
# 参考 tools/init_db.sh 中的 Cypher 语句
```

---

### 日常部署

| 操作 | 方式 |
|------|------|
| **代码更新** | Git push → Dokploy 自动构建部署 |
| **数据库迁移** | Dokploy Terminal → `python manage.py migrate` |
| **环境变量** | Dokploy 控制台修改 → Redeploy |
| **回滚** | Dokploy 控制台选择历史版本 |

---

### Dockerfile 配置

确保 `apps/cms/Dockerfile` 和 `apps/backend/Dockerfile` 存在。

Dokploy 会根据 Git 仓库自动检测和构建。

---

## 本地开发

```bash
# 复制环境变量
cp tools/envs/env.ci .env
vim .env  # 填入本地配置

# 启动服务
./tools/dev.sh start

# 或使用 docker-compose
docker-compose up -d
```

---

## 目录结构

```
tools/
├── envs/
│   ├── README.md       # 环境变量说明
│   └── env.ci          # 变量契约 (SSOT)
├── init_db.sh          # 本地初始化脚本
├── dev.sh              # 本地开发启停
├── manage.py           # 环境管理 CLI
├── install_system.py   # 系统依赖检查
└── lint_structure.sh   # 目录结构检查
```

---

## 环境变量契约

**文件**: `tools/envs/env.ci`

| 变量 | 必填 | 说明 |
|------|------|------|
| `PEG_ENV` | ✓ | `dev` / `test_xxx` / `prod` |
| `DATABASE_URL` | ✓ | PostgreSQL 连接串 |
| `NEO4J_URI` | ✓ | Neo4j Bolt URI |
| `NEO4J_USER` | ✓ | Neo4j 用户名 |
| `NEO4J_PASSWORD` | ✓ | Neo4j 密码 |
| `JWT_SECRET_KEY` | ✓ | JWT 签名密钥 |
| `DJANGO_SECRET_KEY` | ✓ | Django 密钥 |
| `DJANGO_ALLOWED_HOSTS` | ✓ | 允许的域名 |

---

## 常见问题

### Q: Dokploy 部署失败？
检查 Build Logs，常见原因：
- Dockerfile 路径不对
- 依赖安装失败
- 环境变量缺失

### Q: Migration 冲突？
```bash
# 在 Dokploy Terminal
python manage.py showmigrations
python manage.py migrate --fake <app> <migration>
```

### Q: 连不上数据库？
- 检查 Dokploy 内部网络名称（通常是服务名如 `postgres`）
- 确认 `DATABASE_URL` 格式正确
