"""
Financial Modeling Prep (FMP) 数据获取模块

免费API限制：
- 250 requests/day
- 支持美股+港股
- 数据质量好

API文档: https://site.financialmodelingprep.com/developer/docs/
"""

import logging
import os
from typing import Optional
import requests
from datetime import datetime

from core.models import StockData
from core.schemas.validation_rules import ValidationRules

logger = logging.getLogger(__name__)

# FMP API配置
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
FMP_API_KEY = os.getenv("FMP_API_KEY", "demo")  # 默认使用demo key


def normalize_ticker_for_fmp(ticker: str) -> str:
    """
    将ticker转换为FMP格式
    
    Examples:
        00700.HK -> 0700.HK (FMP格式)
        AAPL -> AAPL
    """
    # FMP对香港股票使用4位代码（去掉前导0但保留4位）
    if ticker.endswith('.HK'):
        code = ticker.replace('.HK', '')
        # 去掉前导0
        code = code.lstrip('0')
        # 如果是港股，FMP使用4位格式
        if len(code) < 4:
            code = code.zfill(4)
        return f"{code}.HK"
    return ticker


def fetch_stock_data(ticker: str) -> Optional[StockData]:
    """
    从Financial Modeling Prep获取股票数据
    
    Args:
        ticker: 股票代码（如 AAPL, 00700.HK）
    
    Returns:
        StockData对象，失败返回None
    """
    logger.info(f"[FMP] 正在获取 {ticker} 的数据...")
    
    # 转换ticker格式
    fmp_ticker = normalize_ticker_for_fmp(ticker)
    
    # 检查API key
    if FMP_API_KEY == "demo":
        logger.warning(f"{ticker}: 未配置FMP API Key，使用demo密钥（功能受限）")
    
    try:
        # 1. 获取股票报价（价格、PE等）
        quote_data = _fetch_quote(fmp_ticker)
        if not quote_data:
            logger.warning(f"{ticker}: 无法从FMP获取报价数据")
            return None
        
        # 2. 获取财务数据（利润、增长率）
        financials = _fetch_financials(fmp_ticker)
        if not financials:
            logger.warning(f"{ticker}: 无法从FMP获取财务数据")
            return None
        
        # 3. 构建StockData
        stock_data = _build_stock_data(
            ticker=ticker,
            quote=quote_data,
            financials=financials
        )
        
        if not stock_data:
            return None
        
        # 4. 数据验证
        validation_errors = []
        validation_warnings = []
        
        # PE验证
        if not ValidationRules.validate_pe(stock_data.pe, ticker):
            validation_errors.append(f"PE无效: {ValidationRules.validate_pe(stock_data.pe, ticker, return_message=True)}")
        
        # PEG验证
        if not ValidationRules.validate_peg(stock_data.peg, ticker):
            validation_errors.append(f"PEG无效: {ValidationRules.validate_peg(stock_data.peg, ticker, return_message=True)}")
        
        # 增长率验证
        if stock_data.growth_rate is None:
            validation_errors.append("增长率为空")
        elif not ValidationRules.validate_growth_rate(stock_data.growth_rate, ticker):
            validation_warnings.append(f"增长率异常: {ValidationRules.validate_growth_rate(stock_data.growth_rate, ticker, return_message=True)}")
        
        # 如果有严重错误，拒绝数据
        if validation_errors:
            logger.error(f"{ticker}: 数据被拒绝 - {'; '.join(validation_errors)}")
            return None
        
        # 根据警告设置置信度
        if validation_warnings:
            logger.warning(f"{ticker}: 数据有警告 - {'; '.join(validation_warnings)}")
            stock_data.confidence = "MEDIUM"
        else:
            stock_data.confidence = "HIGH"
        
        logger.info(f"{ticker}: 数据获取成功 - PE={stock_data.pe:.2f}, PEG={stock_data.peg:.2f}, 置信度={stock_data.confidence}")
        return stock_data
        
    except Exception as e:
        logger.error(f"{ticker}: 数据获取失败 - {str(e)}")
        return None


def _fetch_quote(ticker: str) -> Optional[dict]:
    """获取股票报价"""
    url = f"{FMP_BASE_URL}/quote/{ticker}"
    params = {"apikey": FMP_API_KEY}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data or len(data) == 0:
            return None
        
        return data[0]  # FMP返回列表
    except Exception as e:
        logger.debug(f"获取报价失败: {e}")
        return None


def _fetch_financials(ticker: str) -> Optional[dict]:
    """获取财务数据（TTM）"""
    # 使用income statement TTM
    url = f"{FMP_BASE_URL}/income-statement/{ticker}"
    params = {
        "apikey": FMP_API_KEY,
        "period": "annual",  # 年度数据
        "limit": 5  # 获取最近5年
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data or len(data) < 2:
            return None
        
        # 计算增长率（使用最近2年）
        latest = data[0]
        previous = data[1]
        
        return {
            'net_income': latest.get('netIncome'),
            'revenue': latest.get('revenue'),
            'eps': latest.get('eps'),
            'growth_rate': _calculate_growth_rate(
                latest.get('netIncome'),
                previous.get('netIncome')
            )
        }
    except Exception as e:
        logger.debug(f"获取财务数据失败: {e}")
        return None


def _calculate_growth_rate(current: Optional[float], previous: Optional[float]) -> Optional[float]:
    """计算增长率"""
    if current is None or previous is None or previous == 0:
        return None
    
    growth = (current - previous) / abs(previous)
    return growth


def _build_stock_data(
    ticker: str,
    quote: dict,
    financials: dict
) -> Optional[StockData]:
    """构建StockData对象"""
    try:
        price = quote.get('price')
        pe = quote.get('pe')
        eps = quote.get('eps')
        market_cap = quote.get('marketCap')
        
        net_income = financials.get('net_income')
        growth_rate = financials.get('growth_rate')
        
        # 检查必要字段
        if price is None or pe is None or growth_rate is None:
            logger.warning(f"{ticker}: 缺少必要数据 - price={price}, pe={pe}, growth_rate={growth_rate}")
            return None
        
        # 计算PEG
        if growth_rate == 0:
            peg = 0.0  # 增长为0，PEG定义为0
        else:
            peg = pe / (growth_rate * 100)  # growth_rate转为百分比
        
        return StockData(
            ticker=ticker,
            date=datetime.now().strftime('%Y-%m-%d'),
            price=float(price),
            pe=float(pe),
            peg=float(peg),
            ttm_profit=float(net_income) if net_income else None,
            growth_rate=float(growth_rate),
            market_cap=float(market_cap) if market_cap else None,
            source="fmp",
            confidence="HIGH"  # 初始为HIGH，后续根据验证调整
        )
        
    except Exception as e:
        logger.error(f"{ticker}: 构建数据失败 - {str(e)}")
        return None


# 便捷函数：批量获取
def fetch_batch(tickers: list[str]) -> dict[str, Optional[StockData]]:
    """
    批量获取股票数据
    
    Args:
        tickers: 股票代码列表
    
    Returns:
        {ticker: StockData} 字典
    """
    results = {}
    for ticker in tickers:
        results[ticker] = fetch_stock_data(ticker)
    return results

