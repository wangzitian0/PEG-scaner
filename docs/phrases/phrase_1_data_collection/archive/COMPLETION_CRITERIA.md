# Phrase 1 完成标准（验收标准）

**版本**: v1.0  
**日期**: 2025-11-15  
**状态**: 🎯 标准已定义，待验收

---

## 📋 核心验收标准

### 1. 多源数据采集 ✅/❌

**标准**:
```
必须至少有2个独立的数据源成功获取数据
每个数据源都应生成独立的CSV文件
```

**验收方法**:
```bash
# 检查是否存在至少2个不同source的CSV文件
ls x-data/stock_fundamental/stock_fundamental-mag7-*.csv | wc -l
# 结果应 >= 2

# 检查source列的唯一值
cat x-data/stock_fundamental/*.csv | grep -v "^ticker" | cut -d',' -f9 | sort -u
# 应输出至少2个不同的source（如yfinance, fmp）
```

**通过条件**: ✅ 至少2个source的CSV文件，每个至少5条有效数据

---

### 2. 多源验证数据 ✅/❌

**标准**:
```
必须生成aggregated数据文件
aggregated数据应包含通过多源验证的股票数据
至少50%的目标股票通过验证
```

**验收方法**:
```bash
# 检查aggregated文件是否存在
ls x-data/stock_fundamental/stock_fundamental-mag7-aggregated-*.csv

# 检查aggregated数据条数
wc -l x-data/stock_fundamental/stock_fundamental-mag7-aggregated-*.csv
# 应至少有7条数据（14只股票的50%）
```

**通过条件**: ✅ aggregated文件存在，至少6条数据（考虑数据质量，宁缺毋滥）

---

### 3. 数据质量验证 ✅/❌

**标准**:
```
所有数据必须通过ValidationRules验证
PEG值在合理范围内（-5 到 10）
PE值在合理范围内（-50 到 500）
growth_rate不为空
confidence为HIGH或MEDIUM
```

**验收方法**:
```bash
# 运行数据质量测试
uv run pytest tests/test_data_quality.py -v

# 手动检查CSV数据范围
python << EOF
import pandas as pd
df = pd.read_csv('x-data/stock_fundamental/stock_fundamental-mag7-aggregated-*.csv')
print(f"PEG范围: {df['peg'].min():.2f} ~ {df['peg'].max():.2f}")
print(f"PE范围: {df['pe'].min():.2f} ~ {df['pe'].max():.2f}")
print(f"空值检查: growth_rate空值 {df['growth_rate'].isna().sum()}个")
print(f"置信度: {df['confidence'].value_counts()}")
EOF
```

**通过条件**: ✅ 所有数据质量测试通过

---

### 4. agent.md要求满足 ✅/❌

**标准**:
```
agent.md (28): "至少两个数据源且相同，才进行下一步" ✅
agent.md (30): 数据文件遵循schema-name-source-date.csv命名 ✅
agent.md (31): 数据文件放在对应schema目录 ✅
agent.md (34): 数据持久化，中间过程可追溯 ✅
agent.md (49): 每次改代码都跑测试 ✅
```

**验收方法**:
```bash
# 检查文件命名
ls x-data/stock_fundamental/*.csv
# 应符合: stock_fundamental-mag7-{source}-{date}.csv

# 检查数据源数量
cat x-data/stock_fundamental/*.csv | grep -v "^ticker" | cut -d',' -f9 | sort -u | wc -l
# 应 >= 2

# 运行所有测试
uv run pytest tests/ -v --cov=./ --cov-report=html
# 应全部通过，覆盖率 >= 80%
```

**通过条件**: ✅ 所有agent.md相关要求满足

---

### 5. 代码质量 ✅/❌

**标准**:
```
所有单元测试通过
代码覆盖率 >= 80%
无linter错误
所有功能有对应测试
```

**验收方法**:
```bash
# 运行测试
uv run pytest tests/ -v --cov=./ --cov-report=term-missing

# 检查覆盖率
# core/: >= 80%
# data_collection/: >= 80%

# 运行linter（如果配置）
# uv run ruff check .
```

**通过条件**: ✅ 测试通过率100%，覆盖率>=80%

---

### 6. 文档完整性 ✅/❌

**标准**:
```
README.md更新，说明实际使用的数据源
数据Schema文档完整
API使用说明清晰
示例代码可运行
```

**验收方法**:
```bash
# 检查必要文档
ls docs/phrases/phrase_1_data_collection/
# 应包含: PLAN.md, CHECKLIST.md, SUMMARY.md, COMPLETION_CRITERIA.md

# 检查README更新
grep -i "数据源" README.md
grep -i "Financial Modeling Prep\|FMP" README.md
```

**通过条件**: ✅ 所有关键文档存在且内容完整

---

## 🎯 最终验收检查清单

### 必须满足（P0）

- [ ] **数据文件**: 至少2个source的CSV文件 + 1个aggregated文件
- [ ] **数据条数**: aggregated文件至少7条有效数据
- [ ] **数据质量**: 所有数据通过ValidationRules验证
- [ ] **agent.md (28)**: 至少两个数据源且相同
- [ ] **测试通过**: 所有单元测试100%通过

### 应该满足（P1）

- [ ] **覆盖率**: 代码覆盖率 >= 80%
- [ ] **文档**: README说明实际使用的数据源
- [ ] **命名规范**: 所有CSV文件符合schema-name-source-date.csv
- [ ] **数据持久化**: 中间数据可追溯

### 最好满足（P2）

- [ ] **错误处理**: 数据源失败时有fallback
- [ ] **性能**: 单次完整采集 < 2分钟
- [ ] **日志**: 清晰的日志输出，便于debug

---

## 📊 自动验收脚本

```bash
#!/bin/bash
# phrase1_acceptance_test.sh

echo "========================================"
echo "Phrase 1 验收测试"
echo "========================================"

# 1. 检查数据文件
echo ""
echo "[1/6] 检查数据文件..."
FILES=$(ls x-data/stock_fundamental/stock_fundamental-mag7-*.csv 2>/dev/null | wc -l)
if [ $FILES -ge 3 ]; then
    echo "✅ 数据文件: $FILES 个（需要>=3）"
else
    echo "❌ 数据文件: $FILES 个（需要>=3）"
    exit 1
fi

# 2. 检查数据源
echo ""
echo "[2/6] 检查数据源..."
SOURCES=$(cat x-data/stock_fundamental/*.csv | grep -v "^ticker" | cut -d',' -f9 | sort -u | wc -l)
if [ $SOURCES -ge 2 ]; then
    echo "✅ 数据源: $SOURCES 个（需要>=2）"
    cat x-data/stock_fundamental/*.csv | grep -v "^ticker" | cut -d',' -f9 | sort -u
else
    echo "❌ 数据源: $SOURCES 个（需要>=2）"
    exit 1
fi

# 3. 检查aggregated数据
echo ""
echo "[3/6] 检查aggregated数据..."
if ls x-data/stock_fundamental/stock_fundamental-mag7-aggregated-*.csv 1> /dev/null 2>&1; then
    ROWS=$(cat x-data/stock_fundamental/stock_fundamental-mag7-aggregated-*.csv | grep -v "^ticker" | wc -l)
    if [ $ROWS -ge 7 ]; then
        echo "✅ Aggregated数据: $ROWS 条（需要>=7）"
    else
        echo "❌ Aggregated数据: $ROWS 条（需要>=7）"
        exit 1
    fi
else
    echo "❌ Aggregated文件不存在"
    exit 1
fi

# 4. 运行测试
echo ""
echo "[4/6] 运行测试..."
uv run pytest tests/ -v -x
if [ $? -eq 0 ]; then
    echo "✅ 所有测试通过"
else
    echo "❌ 测试失败"
    exit 1
fi

# 5. 检查覆盖率
echo ""
echo "[5/6] 检查覆盖率..."
uv run pytest tests/ --cov=core --cov=data_collection --cov-report=term | tail -5

# 6. 检查文档
echo ""
echo "[6/6] 检查文档..."
DOCS=("PLAN.md" "CHECKLIST.md" "SUMMARY.md" "COMPLETION_CRITERIA.md")
for doc in "${DOCS[@]}"; do
    if [ -f "docs/phrases/phrase_1_data_collection/$doc" ]; then
        echo "✅ $doc"
    else
        echo "⚠️  $doc 缺失"
    fi
done

echo ""
echo "========================================"
echo "✅ Phrase 1 验收测试完成！"
echo "========================================"
```

---

## 📝 验收签字

**验收人**: _________  
**验收日期**: _________  
**验收结果**: ☐ 通过 ☐ 不通过  
**备注**: _________

---

## 🔄 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2025-11-15 | 初始版本，定义6大验收标准 |

