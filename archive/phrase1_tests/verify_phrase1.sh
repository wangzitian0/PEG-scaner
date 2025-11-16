#!/bin/bash
# phrase1_acceptance_test.sh - Phrase 1 验收测试脚本

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
    if [ $ROWS -ge 6 ]; then
        echo "✅ Aggregated数据: $ROWS 条（需要>=6）"
    else
        echo "❌ Aggregated数据: $ROWS 条（需要>=6）"
        exit 1
    fi
else
    echo "❌ Aggregated文件不存在"
    exit 1
fi

# 4. 运行测试
echo ""
echo "[4/6] 运行测试..."
uv run pytest tests/ -v -x --tb=short
if [ $? -eq 0 ]; then
    echo "✅ 所有测试通过"
else
    echo "❌ 测试失败"
    exit 1
fi

# 5. 检查覆盖率
echo ""
echo "[5/6] 检查覆盖率..."
uv run pytest tests/ --cov=core --cov=data_collection --cov-report=term --cov-report=html --cov-report=term-missing:skip-covered -q

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
