"""
investpy数据获取模块

从investing.com获取股票数据
- 无需API key
- 覆盖全球市场（美股+港股）
- 独立于Yahoo Finance
"""

import logging
import time
import random
from typing import Optional
from datetime import datetime
from functools import wraps
import investpy

from core.models import StockData
from core.schemas.validation_rules import ValidationRules

logger = logging.getLogger(__name__)

# 限速装饰器
def rate_limit(min_interval=3.0):
    """限速装饰器，避免触发403错误"""
    last_call = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 等待
            elapsed = time.time() - last_call[0]
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed + random.uniform(0, 1)
                logger.debug(f"限速等待 {sleep_time:.1f}秒...")
                time.sleep(sleep_time)
            
            # 执行
            try:
                result = func(*args, **kwargs)
                last_call[0] = time.time()
                return result
            except Exception as e:
                if '403' in str(e):
                    # 403错误，等待更久
                    wait_time = random.uniform(10, 20)
                    logger.warning(f"遇到403错误，等待{wait_time:.1f}秒后重试...")
                    time.sleep(wait_time)
                    # 重试一次
                    try:
                        result = func(*args, **kwargs)
                        last_call[0] = time.time()
                        return result
                    except:
                        raise
                else:
                    raise
        return wrapper
    return decorator


def normalize_ticker_for_investpy(ticker: str) -> tuple[str, str]:
    """
    将ticker转换为investpy格式
    
    Returns:
        (stock_code, country)
        
    Examples:
        AAPL -> ('AAPL', 'united states')
        00700.HK -> ('0700', 'hong kong')
    """
    if ticker.endswith('.HK'):
        code = ticker.replace('.HK', '')
        # investpy港股使用4位代码
        if len(code) > 4:
            code = code.lstrip('0')  # 去掉前导0
        if len(code) < 4:
            code = code.zfill(4)  # 补齐到4位
        return (code, 'hong kong')
    else:
        return (ticker, 'united states')


@rate_limit(min_interval=3.0)
def fetch_stock_data(ticker: str) -> Optional[StockData]:
    """
    从investpy获取股票数据（带限速保护）
    
    Args:
        ticker: 股票代码（如 AAPL, 00700.HK）
    
    Returns:
        StockData对象，失败返回None
    """
    logger.info(f"[investpy-备用] 正在获取 {ticker} 的数据...")
    
    try:
        # 转换ticker格式
        stock_code, country = normalize_ticker_for_investpy(ticker)
        
        # 1. 获取最近价格数据
        recent_data = investpy.get_stock_recent_data(
            stock=stock_code,
            country=country,
            as_json=False
        )
        
        if recent_data.empty:
            logger.warning(f"{ticker}: 无法从investpy获取价格数据")
            return None
        
        price = float(recent_data['Close'].iloc[-1])
        
        # 2. 获取股票信息
        try:
            info = investpy.get_stock_information(
                stock=stock_code,
                country=country,
                as_json=True
            )
            
            # 从info中提取PE、市值等
            pe = None
            market_cap = None
            
            for item in info:
                if item['key'] == 'P/E Ratio':
                    try:
                        pe_str = item['value'].replace(',', '')
                        pe = float(pe_str)
                    except:
                        pass
                elif item['key'] == 'Market Cap':
                    try:
                        cap_str = item['value'].replace(',', '').replace('B', 'e9').replace('M', 'e6')
                        market_cap = float(cap_str)
                    except:
                        pass
            
            if pe is None:
                logger.warning(f"{ticker}: investpy未提供PE数据")
                return None
            
        except Exception as e:
            logger.warning(f"{ticker}: 无法从investpy获取股票信息 - {e}")
            return None
        
        # 3. 获取财务数据（估算增长率）
        # investpy不直接提供利润数据，使用历史价格估算增长
        try:
            historical = investpy.get_stock_historical_data(
                stock=stock_code,
                country=country,
                from_date='01/01/2023',
                to_date=datetime.now().strftime('%d/%m/%Y'),
                as_json=False
            )
            
            # 使用股价年增长率作为估算
            if len(historical) >= 252:  # 至少一年数据
                price_1y_ago = historical['Close'].iloc[-252]
                growth_rate = (price - price_1y_ago) / price_1y_ago
            else:
                # 数据不足一年，使用可用数据
                price_start = historical['Close'].iloc[0]
                days = len(historical)
                growth_rate = ((price / price_start) ** (252 / days)) - 1
                
        except Exception as e:
            logger.warning(f"{ticker}: 无法计算增长率 - {e}")
            # 使用行业平均15%作为默认值
            growth_rate = 0.15
        
        # 4. 计算PEG
        if growth_rate == 0:
            peg = 0.0
        else:
            peg = pe / (growth_rate * 100)
        
        # 5. 数据验证
        validation_errors = []
        
        if not ValidationRules.validate_pe(pe, ticker):
            validation_errors.append("PE无效")
        
        if not ValidationRules.validate_peg(peg, ticker):
            validation_errors.append("PEG无效")
        
        if not ValidationRules.validate_growth_rate(growth_rate, ticker):
            validation_errors.append("增长率无效")
        
        if validation_errors:
            logger.error(f"{ticker}: 数据被拒绝 - {'; '.join(validation_errors)}")
            return None
        
        # 6. 构建StockData
        stock_data = StockData(
            ticker=ticker,
            date=datetime.now().strftime('%Y-%m-%d'),
            price=price,
            pe=pe,
            peg=peg,
            ttm_profit=0.0,  # investpy不提供
            growth_rate=growth_rate,
            market_cap=market_cap,
            data_source="investpy",
            confidence="MEDIUM"  # 因为增长率是估算的
        )
        
        logger.info(f"{ticker}: 数据获取成功 - PE={pe:.2f}, PEG={peg:.2f}, 置信度=MEDIUM")
        return stock_data
        
    except Exception as e:
        logger.error(f"{ticker}: 数据获取失败 - {str(e)}")
        return None

