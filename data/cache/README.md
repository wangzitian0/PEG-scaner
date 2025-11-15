# cache - 临时缓存

**用途**: 临时缓存API响应数据，减少API调用

**注意**: 
- 缓存是临时性质的，**不遵循** schema-name-source-date命名规范
- schema规范仅用于持久化数据
- 缓存文件格式: `{ticker}.json`
- 默认过期时间: 24小时

**管理**:
- 缓存由 `data_collection/cache_manager.py` 自动管理
- 过期数据自动失效
- 可手动清理: `rm data/cache/*`

---

**上级文档**: [返回data目录](../README.md)
