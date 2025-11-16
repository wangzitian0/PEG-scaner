# 第三数据源计划

**要求来源**: agent.md Line 27
**状态**: 📝 计划中
**优先级**: P2（Phase 1.5）

---

## 📋 背景

agent.md Line 27要求：
> 拉数据为了保证置信度，应当使用至少三个免费的财经数据源

**当前状态**:
- ✅ yfinance (已实现)
- ✅ Alpha Vantage (已实现)
- ❌ 第三数据源 (待实现)

---

## 🎯 候选数据源

### 1. Yahoo Finance API (推荐)
**优点**:
- 免费、无需API key
- 数据全面（价格+财务）
- 与yfinance数据可交叉验证

**缺点**:
- 非官方API，可能不稳定

### 2. Financial Modeling Prep
**优点**:
- 官方API
- 数据质量高
- 免费额度充足

**缺点**:
- 需要注册API key
- 速率限制

### 3. IEX Cloud
**优点**:
- 官方API
- 数据实时性好

**缺点**:
- 免费额度有限
- 财务数据不完整

### 4. Polygon.io
**优点**:
- 数据全面
- API稳定

**缺点**:
- 免费额度较小

---

## 🚀 实现计划

### Phase 1.5: 第三数据源集成

#### 1. 选择数据源
- [ ] 评估各候选源
- [ ] 注册API key（如需要）
- [ ] 测试数据质量

#### 2. 实现Fetcher
- [ ] 创建 `data_collection/fetch_xxx.py`
- [ ] 实现与现有fetcher相同的接口
- [ ] 添加错误处理和重试

#### 3. 集成到Aggregator
- [ ] 更新 `data_aggregator.py`
- [ ] 支持3源交叉验证
- [ ] 提高置信度算法

#### 4. 测试
- [ ] 单元测试
- [ ] 集成测试
- [ ] 数据质量测试

---

## 📊 三源验证策略

### 当前（2源）
```python
if source1 == source2:
    confidence = "HIGH"
else:
    confidence = "MEDIUM"  # 或拒绝
```

### 升级（3源）
```python
if all_three_agree:
    confidence = "HIGH"
elif two_agree:
    confidence = "MEDIUM"
    use_majority_value()
else:
    confidence = "LOW"
    reject_or_manual_review()
```

---

## ⏱️ 时间估算

- 数据源评估和选择: 2小时
- Fetcher实现: 4小时
- Aggregator升级: 2小时
- 测试和文档: 2小时

**总计**: 约10小时

---

## 📝 注意事项

1. **API Key管理**
   - 使用环境变量
   - 不要提交到Git

2. **速率限制**
   - 实现请求缓存
   - 添加延迟控制

3. **数据一致性**
   - 统一时区处理
   - 统一币种转换

4. **向后兼容**
   - 保持现有2源代码可用
   - 渐进式迁移到3源

---

**状态**: 当前2源验证已满足基本需求，第三源可在Phase 1.5或Phase 2前实现

**上级文档**: [返回phrase_1](./README.md)
