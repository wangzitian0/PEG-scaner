"""
Twelve Data数据源 - 全球市场官方API

特点:
- 官方API，稳定可靠
- 支持全球市场（包括港股）
- 免费tier: 800次/天, 8次/分钟
- 有完整的Python SDK
"""

import os
import time
import logging
from typing import Optional
from datetime import datetime
from twelvedata import TDClient

from core.models import StockData
from core.schemas.validation_rules import ValidationRules

logger = logging.getLogger(__name__)


def get_twelvedata_client() -> Optional[TDClient]:
    """
    获取Twelve Data客户端
    
    Returns:
        TDClient对象，未设置API key则返回None
    """
    api_key = os.getenv('TWELVE_DATA_API_KEY')
    if not api_key:
        logger.warning("TWELVE_DATA_API_KEY未设置，跳过twelvedata")
        return None
    
    return TDClient(apikey=api_key)


def normalize_ticker_for_twelvedata(ticker: str) -> str:
    """
    转换ticker格式为twelvedata格式
    
    Examples:
        00700.HK -> 0700:HKEX or 0700.HK
        MSFT.US -> MSFT
        
    注意: twelvedata港股格式需要验证
    """
    if ticker.upper().endswith('.HK'):
        # 港股：去掉前导零，保留.HK
        code = ticker.split('.')[0].lstrip('0')
        return f"{code}.HK"
    elif ticker.upper().endswith('.US'):
        # 美股：去掉.US后缀
        return ticker.split('.')[0]
    else:
        return ticker


def fetch_stock_price(client: TDClient, symbol: str) -> Optional[dict]:
    """
    获取股票价格和基本信息
    
    Args:
        client: TDClient对象
        symbol: twelvedata格式的ticker
        
    Returns:
        包含价格数据的字典
    """
    try:
        # 获取最新价格
        ts = client.time_series(
            symbol=symbol,
            interval="1day",
            outputsize=1
        )
        
        price_data = ts.as_json()
        
        if not price_data or 'values' not in price_data:
            logger.warning(f"{symbol}: 未找到价格数据")
            return None
        
        latest = price_data['values'][0]
        
        return {
            'price': float(latest['close']),
            'volume': float(latest.get('volume', 0)),
            'datetime': latest['datetime']
        }
        
    except Exception as e:
        logger.error(f"{symbol}: 获取价格失败: {e}")
        return None


def fetch_stock_fundamentals(client: TDClient, symbol: str) -> Optional[dict]:
    """
    获取股票基本面数据
    
    Args:
        client: TDClient对象
        symbol: twelvedata格式的ticker
        
    Returns:
        包含基本面数据的字典
    """
    try:
        # 获取统计数据
        stats = client.get_statistics(symbol=symbol)
        
        if not stats or stats.status_code != 200:
            logger.warning(f"{symbol}: 未找到基本面数据")
            return None
        
        data = stats.as_json()
        
        # 提取关键指标
        statistics = data.get('statistics', {})
        valuations = statistics.get('valuations', {})
        
        return {
            'pe_ratio': valuations.get('TrailingPE'),
            'market_cap': valuations.get('MarketCapitalization'),
            'peg_ratio': valuations.get('PegRatio'),
        }
        
    except Exception as e:
        logger.error(f"{symbol}: 获取基本面失败: {e}")
        return None


def fetch_stock_data(ticker: str) -> Optional[StockData]:
    """
    从Twelve Data获取股票数据
    
    Args:
        ticker: 标准格式ticker (如 "00700.HK", "MSFT.US")
        
    Returns:
        StockData对象，失败返回None
    """
    # 1. 获取客户端
    client = get_twelvedata_client()
    if client is None:
        return None
    
    # 2. 转换ticker格式
    td_symbol = normalize_ticker_for_twelvedata(ticker)
    logger.info(f"{ticker}: 转换为twelvedata格式: {td_symbol}")
    
    # 3. 获取价格数据
    price_data = fetch_stock_price(client, td_symbol)
    if price_data is None:
        return None
    
    # 4. 获取基本面数据（限速保护）
    time.sleep(0.5)  # 8次/分钟 = 7.5秒间隔，保守使用0.5秒
    fundamentals = fetch_stock_fundamentals(client, td_symbol)
    
    # 5. 构造StockData
    try:
        stock_data = StockData(
            ticker=ticker,
            date=datetime.now().strftime('%Y-%m-%d'),
            price=price_data['price'],
            pe_ratio=float(fundamentals['pe_ratio']) if fundamentals and fundamentals.get('pe_ratio') else None,
            peg_ratio=float(fundamentals['peg_ratio']) if fundamentals and fundamentals.get('peg_ratio') else None,
            ttm_net_income=None,  # twelvedata可能不提供详细财务数据
            growth_rate=None,
            market_cap=float(fundamentals['market_cap']) if fundamentals and fundamentals.get('market_cap') else None,
            data_source='twelvedata',
            confidence='HIGH'  # 官方API
        )
        
        # 6. 验证数据
        is_valid, warnings = ValidationRules.validate_stock_data(
            stock_data.ticker,
            stock_data.price,
            stock_data.pe_ratio,
            stock_data.peg_ratio,
            stock_data.growth_rate
        )
        
        if not is_valid:
            logger.warning(f"{ticker}: 数据验证失败: {warnings}")
            return None
        
        if warnings:
            logger.info(f"{ticker}: 数据验证警告: {warnings}")
            stock_data.confidence = 'MEDIUM'
        
        logger.info(f"{ticker}: ✅ 数据获取成功 (price={stock_data.price:.2f}, PE={stock_data.pe_ratio})")
        return stock_data
        
    except Exception as e:
        logger.error(f"{ticker}: 构造StockData失败: {e}")
        return None


def test_fetch():
    """测试函数"""
    logging.basicConfig(level=logging.INFO)
    
    # 检查API key
    api_key = os.getenv('TWELVE_DATA_API_KEY')
    if not api_key:
        print("❌ TWELVE_DATA_API_KEY未设置")
        print("请运行: export TWELVE_DATA_API_KEY='your_api_key'")
        return
    
    test_tickers = [
        "00700.HK",  # 腾讯
        "MSFT.US",   # 微软
    ]
    
    for ticker in test_tickers:
        print(f"\n{'='*50}")
        print(f"测试: {ticker}")
        print(f"{'='*50}")
        
        data = fetch_stock_data(ticker)
        if data:
            print(f"✅ 成功: {data}")
        else:
            print(f"❌ 失败")
        
        time.sleep(1)  # 限速保护


if __name__ == "__main__":
    test_fetch()

