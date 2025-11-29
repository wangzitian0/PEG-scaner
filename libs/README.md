# Libraries

Shared libraries and Single Source of Truth assets live under `libs/`. 

## Directory Index

| Library | Description |
|---------|-------------|
| [`schema/`](./schema/README.md) | GraphQL SDL - cross-application contracts (SSOT) |
| [`neo4j_repo/`](./neo4j_repo/README.md) | Neo4j data access layer - repositories & models |
| [`neo4j_db/`](./neo4j_db/README.md) | Legacy Neo4j client (deprecated, use neo4j_repo) |

## Architecture

```
libs/
├── schema/           # GraphQL SDL (SSOT for data contracts)
│   ├── common/       # 通用类型 (Ping, Pagination)
│   ├── market/       # 市场域 (Stock, KLine)
│   ├── news/         # 新闻域 (NewsItem)
│   └── schema.graphql  # 聚合产物
│
└── neo4j_repo/       # 共享数据访问层
    ├── connection.py # 连接管理
    ├── repositories/ # Repository 类
    └── models/       # neomodel 节点定义
```

## Usage

### Schema

```bash
# Modify domain files, then regenerate
python libs/schema/merge_schema.py
```

### Neo4j Repository

```python
from neo4j_repo import StockRepository

repo = StockRepository()
payload = repo.fetch_stock_payload("AAPL")
```

## Adding New Libraries

Add new shared libs here (e.g., reusable TypeScript/Python packages) so every app consumes the same artifacts.
