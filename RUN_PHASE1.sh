#!/bin/bash
#
# Phase 1 执行脚本 - yfinance 单源数据采集
#

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          Phase 1: 数据采集 (yfinance)                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "1️⃣  清理旧数据..."
rm -f x-data/stock_fundamental/stock_fundamental-mag7-*.csv
echo "✅ 旧数据已清理"
echo ""

echo "2️⃣  运行数据采集 (yfinance)..."
uv run python data_collection/fetch_current_peg_new.py
echo ""

echo "3️⃣  检查结果..."
if [ -f x-data/stock_fundamental/stock_fundamental-mag7-yfinance-*.csv ]; then
    FILE=$(ls -1 x-data/stock_fundamental/stock_fundamental-mag7-yfinance-*.csv | head -1)
    ROW_COUNT=$(tail -n +2 "$FILE" | wc -l | tr -d ' ')
    echo "✅ 数据文件: $FILE"
    echo "✅ 数据行数: $ROW_COUNT"
    
    if [ "$ROW_COUNT" -ge 11 ]; then
        echo ""
        echo "╔════════════════════════════════════════════════════════════╗"
        echo "║          ✅ Phase 1 完成！                                 ║"
        echo "╚════════════════════════════════════════════════════════════╝"
        echo ""
        echo "查看结果: cat $FILE"
    else
        echo "⚠️  数据行数少于预期 (11+)"
    fi
else
    echo "❌ 数据文件未生成"
    exit 1
fi

