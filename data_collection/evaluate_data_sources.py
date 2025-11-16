#!/usr/bin/env python3
"""
Phase 1 核心：数据源质量评估

目标：
数据类型 × 数据来源 × 公司股票 → 置信程度

输出：
完整的数据质量矩阵表格
"""

import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import yfinance as yf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 目标股票
STOCKS = {
    '美股': [
        ('AAPL', '苹果'),
        ('MSFT', '微软'),
        ('GOOGL', '谷歌'),
        ('AMZN', '亚马逊'),
        ('NVDA', '英伟达'),
        ('META', 'Meta'),
        ('TSLA', '特斯拉'),
    ],
    '港股': [
        ('00700.HK', '腾讯'),
        ('09988.HK', '阿里巴巴'),
        ('03690.HK', '美团'),
        ('01810.HK', '小米'),
        ('09618.HK', '京东'),
        ('01211.HK', '比亚迪'),
        ('09999.HK', '网易'),
    ]
}

# 数据类型
DATA_TYPES = {
    'price': '实时价格',
    'volume': '成交量',
    'market_cap': '市值',
    'pe': 'PE比率',
    'financials': '财务报表',
    'net_income': '净利润',
    'growth': '增长率',
}


def normalize_hk_ticker(ticker: str) -> str:
    """港股ticker格式标准化"""
    if '.HK' in ticker:
        base = ticker.replace('.HK', '')
        base = base.lstrip('0') or '0'
        if len(base) < 4:
            base = base.zfill(4)
        return f"{base}.HK"
    return ticker


def evaluate_yfinance(ticker: str, name: str) -> Dict[str, str]:
    """评估 yfinance 数据源"""
    logger.info(f"  [yfinance] 测试 {name} ({ticker})")
    
    result = {
        'ticker': ticker,
        'name': name,
        'source': 'yfinance',
    }
    
    try:
        # 标准化ticker
        normalized = normalize_hk_ticker(ticker)
        stock = yf.Ticker(normalized)
        
        # 1. 测试价格数据
        info = stock.info
        if info and 'currentPrice' in info:
            result['price'] = '✅'
            result['price_value'] = f"{info['currentPrice']:.2f}"
        else:
            result['price'] = '❌'
            result['price_value'] = 'N/A'
        
        # 2. 测试成交量
        if info and 'volume' in info:
            result['volume'] = '✅'
        else:
            result['volume'] = '❌'
        
        # 3. 测试市值
        if info and 'marketCap' in info:
            result['market_cap'] = '✅'
            result['market_cap_value'] = f"{info['marketCap']/1e9:.1f}B"
        else:
            result['market_cap'] = '❌'
            result['market_cap_value'] = 'N/A'
        
        # 4. 测试PE
        if info and 'trailingPE' in info:
            result['pe'] = '✅'
            result['pe_value'] = f"{info['trailingPE']:.2f}"
        else:
            result['pe'] = '❌'
            result['pe_value'] = 'N/A'
        
        # 5. 测试财务数据
        financials = stock.financials
        if not financials.empty:
            result['financials'] = '✅'
            
            # 6. 测试净利润
            if 'Net Income' in financials.index:
                result['net_income'] = '✅'
                latest_income = financials.loc['Net Income'].iloc[0]
                result['net_income_value'] = f"{latest_income/1e9:.1f}B"
            else:
                result['net_income'] = '❌'
                result['net_income_value'] = 'N/A'
            
            # 7. 测试增长率（需要多期数据）
            if 'Net Income' in financials.index and len(financials.columns) >= 2:
                try:
                    income_curr = financials.loc['Net Income'].iloc[0]
                    income_prev = financials.loc['Net Income'].iloc[1]
                    growth = (income_curr - income_prev) / abs(income_prev)
                    result['growth'] = '✅'
                    result['growth_value'] = f"{growth*100:.1f}%"
                except:
                    result['growth'] = '⚠️'
                    result['growth_value'] = 'calc_error'
            else:
                result['growth'] = '❌'
                result['growth_value'] = 'N/A'
        else:
            result['financials'] = '❌'
            result['net_income'] = '❌'
            result['net_income_value'] = 'N/A'
            result['growth'] = '❌'
            result['growth_value'] = 'N/A'
        
        # 计算置信度
        checks = [
            result.get('price') == '✅',
            result.get('pe') == '✅',
            result.get('financials') == '✅',
            result.get('net_income') == '✅',
            result.get('growth') == '✅',
        ]
        score = sum(checks)
        
        if score >= 4:
            result['confidence'] = 'HIGH'
        elif score >= 2:
            result['confidence'] = 'MEDIUM'
        else:
            result['confidence'] = 'LOW'
        
    except Exception as e:
        logger.error(f"    错误: {e}")
        for dtype in DATA_TYPES.keys():
            result[dtype] = '❌'
        result['confidence'] = 'FAILED'
    
    return result


def evaluate_finnhub(ticker: str, name: str) -> Dict[str, str]:
    """评估 finnhub 数据源"""
    logger.info(f"  [finnhub] 测试 {name} ({ticker})")
    
    result = {
        'ticker': ticker,
        'name': name,
        'source': 'finnhub',
    }
    
    api_key = os.getenv('FINNHUB_TOKEN')
    if not api_key:
        logger.warning("    FINNHUB_TOKEN 未设置")
        for dtype in DATA_TYPES.keys():
            result[dtype] = '⚠️'
        result['confidence'] = 'NO_API_KEY'
        return result
    
    try:
        import requests
        
        # 转换ticker格式
        symbol = ticker.replace('.US', '')
        
        # 1. 测试报价
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"
        resp = requests.get(url, timeout=5)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('c', 0) > 0:
                result['price'] = '✅'
                result['price_value'] = f"{data['c']:.2f}"
            else:
                result['price'] = '❌'
        elif resp.status_code == 403:
            result['price'] = '🔒'  # 权限不足
        else:
            result['price'] = '❌'
        
        time.sleep(0.2)  # 限速
        
        # 2. 测试基本面数据
        url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={api_key}"
        resp = requests.get(url, timeout=5)
        
        if resp.status_code == 200:
            data = resp.json()
            metric = data.get('metric', {})
            
            if metric.get('peBasicExclExtraTTM'):
                result['pe'] = '✅'
                result['pe_value'] = f"{metric['peBasicExclExtraTTM']:.2f}"
            else:
                result['pe'] = '❌'
            
            if metric.get('marketCapitalization'):
                result['market_cap'] = '✅'
                result['market_cap_value'] = f"{metric['marketCapitalization']:.1f}B"
            else:
                result['market_cap'] = '❌'
        else:
            result['pe'] = '❌'
            result['market_cap'] = '❌'
        
        # finnhub 免费tier 不提供详细财务数据
        result['financials'] = '🔒'
        result['net_income'] = '🔒'
        result['growth'] = '🔒'
        result['volume'] = '⚠️'
        
        # 计算置信度
        if result.get('price') == '✅' and result.get('pe') == '✅':
            result['confidence'] = 'MEDIUM'
        elif result.get('price') == '🔒':
            result['confidence'] = 'BLOCKED'
        else:
            result['confidence'] = 'LOW'
        
    except Exception as e:
        logger.error(f"    错误: {e}")
        for dtype in DATA_TYPES.keys():
            result[dtype] = '❌'
        result['confidence'] = 'FAILED'
    
    return result


def evaluate_twelvedata(ticker: str, name: str) -> Dict[str, str]:
    """评估 twelvedata 数据源"""
    logger.info(f"  [twelvedata] 测试 {name} ({ticker})")
    
    result = {
        'ticker': ticker,
        'name': name,
        'source': 'twelvedata',
    }
    
    api_key = os.getenv('TWELVE_DATA_API_KEY')
    if not api_key:
        logger.warning("    TWELVE_DATA_API_KEY 未设置")
        for dtype in DATA_TYPES.keys():
            result[dtype] = '⚠️'
        result['confidence'] = 'NO_API_KEY'
        return result
    
    try:
        from twelvedata import TDClient
        td = TDClient(apikey=api_key)
        
        # 转换ticker
        symbol = ticker.replace('.US', '')
        
        # 1. 测试价格
        try:
            ts = td.time_series(symbol=symbol, interval="1day", outputsize=1)
            data = ts.as_json()
            if isinstance(data, tuple) and len(data) > 0:
                result['price'] = '✅'
                result['price_value'] = f"{float(data[0]['close']):.2f}"
            else:
                result['price'] = '❌'
        except Exception as e:
            if 'pro' in str(e).lower():
                result['price'] = '🔒'
            else:
                result['price'] = '❌'
        
        time.sleep(0.5)  # 限速
        
        # twelvedata 免费tier：统计数据需要付费
        result['pe'] = '🔒'
        result['market_cap'] = '🔒'
        result['financials'] = '🔒'
        result['net_income'] = '🔒'
        result['growth'] = '🔒'
        result['volume'] = '⚠️'
        
        if result.get('price') == '✅':
            result['confidence'] = 'LOW'  # 只有价格
        else:
            result['confidence'] = 'BLOCKED'
        
    except Exception as e:
        logger.error(f"    错误: {e}")
        for dtype in DATA_TYPES.keys():
            result[dtype] = '❌'
        result['confidence'] = 'FAILED'
    
    return result


def main():
    """运行完整评估"""
    print("="*80)
    print("Phase 1 核心：数据源质量评估")
    print("="*80)
    print()
    
    all_results = []
    
    for market, stocks in STOCKS.items():
        print(f"\n{'='*80}")
        print(f"{market} 市场")
        print("="*80)
        
        for ticker, name in stocks:
            print(f"\n{name} ({ticker}):")
            
            # 评估 yfinance
            result_yf = evaluate_yfinance(ticker, name)
            all_results.append(result_yf)
            
            time.sleep(0.5)
            
            # 评估 finnhub (仅美股)
            if market == '美股':
                result_fh = evaluate_finnhub(ticker, name)
                all_results.append(result_fh)
                time.sleep(0.5)
            
            # 评估 twelvedata (仅美股)
            if market == '美股':
                result_td = evaluate_twelvedata(ticker, name)
                all_results.append(result_td)
                time.sleep(0.5)
    
    # 保存结果
    df = pd.DataFrame(all_results)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'x-data/data_source_evaluation_{timestamp}.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n{'='*80}")
    print(f"✅ 评估完成！")
    print(f"📄 结果已保存: {output_file}")
    print("="*80)
    
    # 生成汇总报告
    print("\n" + "="*80)
    print("汇总统计")
    print("="*80)
    
    for source in df['source'].unique():
        source_data = df[df['source'] == source]
        print(f"\n{source}:")
        print(f"  总测试数: {len(source_data)}")
        print(f"  置信度分布:")
        for conf, count in source_data['confidence'].value_counts().items():
            print(f"    {conf}: {count}")
    
    return df


if __name__ == "__main__":
    df = main()

