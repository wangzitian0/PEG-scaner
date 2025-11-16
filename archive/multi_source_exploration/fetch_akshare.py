"""
AkShare数据源 - 专注中文市场（A股、港股）

特点:
- 开源爬虫，完全免费
- 专注中文市场
- 实时数据
- 可能遇到反爬虫（已实现重试机制）
"""

import time
import logging
from typing import Optional
from datetime import datetime
import akshare as ak
import pandas as pd

from core.models import StockData
from core.schemas.validation_rules import ValidationRules

logger = logging.getLogger(__name__)


def normalize_ticker_for_akshare(ticker: str) -> str:
    """
    转换ticker格式为akshare格式
    
    Examples:
        00700.HK -> 00700
        MSFT.US -> MSFT (akshare不支持美股)
    """
    if ticker.upper().endswith('.HK'):
        # 港股：保留前导零
        return ticker.split('.')[0]
    else:
        # 美股：akshare不支持
        return None


def fetch_hk_stock_data(symbol: str, max_retries: int = 3) -> Optional[dict]:
    """
    获取港股数据（带重试机制）
    
    Args:
        symbol: 港股代码（如 "00700"）
        max_retries: 最大重试次数
        
    Returns:
        包含价格和基本面数据的字典，失败返回None
    """
    for attempt in range(max_retries):
        try:
            # 获取实时行情
            df_spot = ak.stock_hk_spot_em()
            
            # 筛选目标股票
            stock_data = df_spot[df_spot['代码'] == symbol]
            
            if stock_data.empty:
                logger.warning(f"{symbol}: 未找到股票数据")
                return None
            
            stock_row = stock_data.iloc[0]
            
            # 获取历史数据（用于计算TTM）
            try:
                df_hist = ak.stock_hk_daily(symbol=symbol, adjust="qfq")
                if not df_hist.empty:
                    current_price = float(df_hist.iloc[-1]['close'])
                else:
                    current_price = float(stock_row['最新价'])
            except Exception as e:
                logger.warning(f"{symbol}: 获取历史数据失败: {e}，使用实时价格")
                current_price = float(stock_row['最新价'])
            
            # 构造返回数据
            result = {
                'symbol': symbol,
                'price': current_price,
                'market_cap': float(stock_row.get('总市值', 0)) if '总市值' in stock_row else None,
                'pe_ratio': float(stock_row.get('市盈率', 0)) if '市盈率' in stock_row else None,
                'volume': float(stock_row.get('成交量', 0)) if '成交量' in stock_row else None,
            }
            
            logger.info(f"{symbol}: 成功获取数据 (价格={result['price']:.2f}, PE={result['pe_ratio']})")
            return result
            
        except Exception as e:
            logger.warning(f"{symbol}: 尝试 {attempt+1}/{max_retries} 失败: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
            else:
                logger.error(f"{symbol}: 所有重试失败")
                return None


def calculate_peg_from_akshare(data: dict, symbol: str) -> Optional[float]:
    """
    基于akshare数据计算PEG
    
    注意: akshare的财务数据有限，PEG计算可能不准确
    """
    try:
        pe = data.get('pe_ratio')
        if pe is None or pe <= 0:
            logger.warning(f"{symbol}: PE无效 ({pe})")
            return None
        
        # akshare港股财务数据支持有限，暂时无法准确获取增长率
        # 这里返回None，表示PEG需要从其他源获取
        logger.info(f"{symbol}: akshare暂不支持增长率计算，PEG需从其他源获取")
        return None
        
    except Exception as e:
        logger.error(f"{symbol}: PEG计算失败: {e}")
        return None


def fetch_stock_data(ticker: str) -> Optional[StockData]:
    """
    从akshare获取股票数据
    
    Args:
        ticker: 标准格式ticker (如 "00700.HK", "MSFT.US")
        
    Returns:
        StockData对象，失败返回None
    """
    # 1. 检查是否支持
    if ticker.upper().endswith('.US'):
        logger.info(f"{ticker}: akshare不支持美股")
        return None
    
    ak_symbol = normalize_ticker_for_akshare(ticker)
    if ak_symbol is None:
        logger.warning(f"{ticker}: 无法转换为akshare格式")
        return None
    
    # 2. 获取数据
    data = fetch_hk_stock_data(ak_symbol)
    if data is None:
        return None
    
    # 3. 计算PEG
    peg = calculate_peg_from_akshare(data, ak_symbol)
    
    # 4. 构造StockData
    try:
        stock_data = StockData(
            ticker=ticker,
            date=datetime.now().strftime('%Y-%m-%d'),
            price=data['price'],
            pe_ratio=data.get('pe_ratio'),
            peg_ratio=peg,
            ttm_net_income=None,  # akshare暂不提供
            growth_rate=None,  # akshare暂不提供
            market_cap=data.get('market_cap'),
            data_source='akshare',
            confidence='MEDIUM'  # 因为缺少财务数据
        )
        
        # 5. 验证数据
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
            stock_data.confidence = 'LOW'
        
        logger.info(f"{ticker}: ✅ 数据获取成功 (price={stock_data.price:.2f}, PE={stock_data.pe_ratio})")
        return stock_data
        
    except Exception as e:
        logger.error(f"{ticker}: 构造StockData失败: {e}")
        return None


def test_fetch():
    """测试函数"""
    logging.basicConfig(level=logging.INFO)
    
    test_tickers = [
        "00700.HK",  # 腾讯
        "09988.HK",  # 阿里巴巴
        "MSFT.US",   # 微软（应该失败）
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


if __name__ == "__main__":
    test_fetch()

