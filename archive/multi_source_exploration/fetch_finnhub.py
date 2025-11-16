"""
Finnhub数据获取模块

官方金融数据API，稳定可靠
- 免费tier: 60 calls/minute
- 支持: 股票价格、基本面数据、财务数据
- 覆盖: 全球主要市场
"""

import logging
import os
from typing import Optional
from datetime import datetime
import finnhub

from core.models import StockData
from core.schemas.validation_rules import ValidationRules

logger = logging.getLogger(__name__)

# Finnhub客户端
FINNHUB_TOKEN = os.getenv("FINNHUB_TOKEN")
if not FINNHUB_TOKEN:
    logger.warning("未找到FINNHUB_TOKEN环境变量，finnhub功能将不可用")
    finnhub_client = None
else:
    finnhub_client = finnhub.Client(api_key=FINNHUB_TOKEN)


def normalize_ticker_for_finnhub(ticker: str) -> str:
    """
    将ticker转换为finnhub格式
    
    Examples:
        AAPL -> AAPL
        00700.HK -> 0700.HK (finnhub使用4位港股代码)
    """
    if ticker.endswith('.HK'):
        code = ticker.replace('.HK', '')
        # finnhub使用4位代码，去掉前导0
        code = code.lstrip('0')
        if len(code) < 4:
            code = code.zfill(4)
        return f"{code}.HK"
    return ticker


def fetch_stock_data(ticker: str) -> Optional[StockData]:
    """
    从Finnhub获取股票数据
    
    Args:
        ticker: 股票代码（如 AAPL, 00700.HK）
    
    Returns:
        StockData对象，失败返回None
    """
    if not finnhub_client:
        logger.error(f"{ticker}: finnhub客户端未初始化（缺少FINNHUB_TOKEN）")
        return None
    
    logger.info(f"[Finnhub] 正在获取 {ticker} 的数据...")
    
    try:
        # 转换ticker格式
        fh_ticker = normalize_ticker_for_finnhub(ticker)
        
        # 1. 获取实时报价
        try:
            quote = finnhub_client.quote(fh_ticker)
            
            if not quote or quote.get('c', 0) == 0:
                logger.warning(f"{ticker}: finnhub无报价数据")
                return None
            
            price = float(quote['c'])  # current price
            
        except Exception as e:
            logger.warning(f"{ticker}: finnhub获取报价失败 - {e}")
            return None
        
        # 2. 获取基本面数据（PE等）
        try:
            metrics = finnhub_client.company_basic_financials(fh_ticker, 'all')
            
            if not metrics or 'metric' not in metrics:
                logger.warning(f"{ticker}: finnhub无基本面数据")
                return None
            
            metric = metrics['metric']
            
            # 提取PE
            pe = metric.get('peBasicExclExtraTTM') or metric.get('peTTM')
            if pe is None or pe == 0:
                logger.warning(f"{ticker}: finnhub无PE数据")
                return None
            
            pe = float(pe)
            
            # 提取市值
            market_cap = metric.get('marketCapitalization')
            if market_cap:
                market_cap = float(market_cap) * 1e6  # finnhub以百万为单位
            
        except Exception as e:
            logger.warning(f"{ticker}: finnhub获取基本面数据失败 - {e}")
            return None
        
        # 3. 获取财务数据（利润、增长率）
        try:
            financials = finnhub_client.company_earnings(fh_ticker, limit=5)
            
            if not financials or len(financials) < 2:
                logger.warning(f"{ticker}: finnhub财务数据不足")
                # 使用默认增长率
                growth_rate = 0.15
            else:
                # 计算EPS增长率
                latest_eps = financials[0].get('epsActual', 0)
                previous_eps = financials[1].get('epsActual', 0)
                
                if previous_eps and previous_eps != 0:
                    growth_rate = (latest_eps - previous_eps) / abs(previous_eps)
                else:
                    growth_rate = 0.15
            
        except Exception as e:
            logger.warning(f"{ticker}: finnhub获取财务数据失败 - {e}")
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
            ttm_profit=0.0,  # finnhub不直接提供
            growth_rate=growth_rate,
            market_cap=market_cap,
            data_source="finnhub",
            confidence="HIGH"  # 官方API，高置信度
        )
        
        logger.info(f"{ticker}: 数据获取成功 - PE={pe:.2f}, PEG={peg:.2f}, 置信度=HIGH")
        return stock_data
        
    except Exception as e:
        logger.error(f"{ticker}: finnhub数据获取失败 - {str(e)}")
        return None


def test_connection() -> bool:
    """测试finnhub连接"""
    if not finnhub_client:
        return False
    
    try:
        quote = finnhub_client.quote('AAPL')
        return quote and quote.get('c', 0) > 0
    except:
        return False

