#!/bin/bash

# 运行三源数据采集
# 确保环境变量正确传递

export FINNHUB_TOKEN="${FINNHUB_TOKEN}"
export TWELVE_DATA_API_KEY="${TWELVE_DATA_API_KEY}"

echo "环境变量检查:"
echo "  FINNHUB_TOKEN: ${FINNHUB_TOKEN:0:10}..."
echo "  TWELVE_DATA_API_KEY: ${TWELVE_DATA_API_KEY:0:10}..."
echo ""

uv run python data_collection/fetch_final_three_sources.py
