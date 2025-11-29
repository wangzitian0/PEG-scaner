# GraphQL Schema (SSOT)

Single Source of Truth for all data contracts across backend, frontend, and regression tests.

## Directory Structure

```
libs/schema/
├── common/           # 通用类型（Ping, Pagination）
│   └── types.graphql
├── market/           # 市场域（Stock, KLine, PegStock）
│   └── market.graphql
├── news/             # 新闻域（NewsItem）
│   └── news.graphql
├── query.graphql     # Root Query 定义
├── merge_schema.py   # 聚合脚本
├── schema.graphql    # 🔴 自动生成，勿手动编辑
└── README.md
```

## Usage

### 1. 修改 Schema

编辑对应域的 `.graphql` 文件：

- **通用类型** → `common/types.graphql`
- **股票/市场** → `market/market.graphql`
- **新闻** → `news/news.graphql`
- **新增 Query** → `query.graphql`

### 2. 重新生成聚合文件

```bash
python libs/schema/merge_schema.py
```

### 3. Codegen（如有前端类型生成）

```bash
npm run codegen  # 如配置了 graphql-codegen
```

## 命名约定

| 域 | 前缀规则 | 示例 |
|----|---------|------|
| common | 无前缀 | `Ping`, `PaginationInput` |
| market | 无特殊前缀（历史兼容） | `Stock`, `PegStock`, `KLinePoint` |
| news | `News*` | `NewsItem` |

## 依赖顺序

```
common → news → market → query
```

- `common/` 不引用其他域
- `news/` 不引用 market
- `market/` 可引用 news（如 `SingleStockPage.news`）
- `query.graphql` 聚合所有域的查询入口

## Strawberry 类型同步

Backend Resolvers 位于 `apps/backend/graphql/`，使用 Strawberry dataclass 风格定义，应与本 Schema 保持一致。
