# BRN-002: 技术现状与背景

## 当前技术栈（迁移前）

### 后端架构
- **框架**：Flask 2.x（同步阻塞模型）
- **GraphQL**：Ariadne（SDL-first，手动绑定 resolver）
- **ORM**：neomodel（Neo4j OGM）
- **Web Server**：Flask dev server（生产未配置）

### 目录结构（现状）
```
apps/backend/
├── src/
│   └── pegserver/
│       ├── __init__.py          # Flask app 创建
│       ├── graphql_api.py       # Ariadne resolvers（160行）
│       ├── graph_store.py       # Neo4j 数据访问（混杂业务逻辑）
│       ├── crawler.py           # 爬虫逻辑（耦合在 backend）
│       ├── config.py            # Settings
│       └── admin.py             # Flask-Admin
├── tests/
│   └── test_graphql.py          # Flask test_client
├── requirements.txt             # Flask + Ariadne + neomodel
└── project.json                 # Nx: serve/test targets
```

### 现存问题
1. **同步模型**：Flask 同步，难扩展异步任务（爬虫/ETL）
2. **职责混乱**：API/爬虫/管理后台耦合在 `pegserver/`
3. **无分层**：`graphql_api.py` 混杂 Resolver + 业务逻辑 + 数据访问
4. **依赖膨胀**：`requirements.txt` 包含 API + 爬虫 + Admin 所有依赖
5. **部署困难**：单一进程，爬虫挂了影响 API
6. **测试困难**：依赖 Flask app context，Mock 复杂

## 迁移目标

### 技术栈升级
- **Flask → FastAPI**：ASGI 异步、依赖注入、OpenAPI 自动生成
- **Ariadne → Strawberry**：dataclass 风格、Pydantic 集成、类型安全
- **单进程 → 多 App**：backend/crawler/etl 独立部署

### 架构改进
- **三层分离**：GraphQL Resolver（薄）→ Service（业务）→ Repository（数据）
- **共享 libs**：`libs/neo4j-repo/` 供所有 app 复用
- **Schema 多域**：`libs/schema/{common,market,news}/` 模块化管理

### 预期收益
- ✅ **性能提升**：ASGI 异步处理，支持 WebSocket
- ✅ **可维护性**：分层清晰，单一职责
- ✅ **可扩展性**：独立 app 可独立扩容
- ✅ **开发体验**：Strawberry dataclass + FastAPI 依赖注入

## 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| Ariadne → Strawberry API 不兼容 | 中 | 保留旧代码（`_legacy.py`），分阶段迁移 |
| 测试用例需要重写 | 中 | Flask test_client → FastAPI TestClient |
| 前端 GraphQL 客户端可能需要调整 | 低 | Schema 保持不变，仅后端实现变化 |
| Neo4j 连接生命周期管理 | 低 | FastAPI lifespan hook 统一管理 |
| 爬虫/ETL 暂未迁移 | 低 | 本次仅迁移 backend，爬虫/ETL 后续独立 BRN |

## 依赖关系

### 上游依赖
- BRN-001 已完成（GraphQL Schema 定义、Neo4j 集成、回归测试框架）

### 下游影响
- BRN-003 个股页面实现（依赖本次架构迁移完成）
- 未来爬虫/ETL 独立（复用 `libs/neo4j-repo/`）

## 回滚方案
- 保留 `pegserver/` 目录（重命名 `pegserver_legacy/`）
- 保留旧 `requirements.txt`（重命名 `requirements.legacy.txt`）
- Git tag 标记迁移前版本
- 回滚只需修改 `project.json` 启动命令

## 参考资源
- [Strawberry 官方文档](https://strawberry.rocks/)
- [FastAPI 最佳实践](https://fastapi.tiangolo.com/tutorial/)
- [Flask to FastAPI 迁移指南](https://fastapi.tiangolo.com/alternatives/#flask)

