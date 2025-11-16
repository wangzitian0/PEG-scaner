"""
yfinance多端点交叉验证

虽然都是yfinance，但使用不同的数据端点进行交叉验证：
- info端点: stock.info (摘要数据)
- financials端点: stock.financials (财务报表)
- quarterly_financials端点: stock.quarterly_financials (季度财务)

通过比较不同端点的数据一致性，提高数据可靠性
"""

import logging
from typing import Optional, Dict
from datetime import datetime
import yfinance as yf

from core.models import StockData
from core.schemas.validation_rules import ValidationRules
from core.format_utils import normalize_ticker

logger = logging.getLogger(__name__)


def fetch_stock_data_multiendpoint(ticker: str) -> Optional[StockData]:
    """
    使用yfinance多端点交叉验证获取股票数据
    
    Args:
        ticker: 股票代码
    
    Returns:
        StockData对象，失败返回None
    """
    logger.info(f"[yfinance-multi] 正在获取 {ticker} 的数据（多端点验证）...")
    
    ticker = normalize_ticker(ticker)
    stock = yf.Ticker(ticker)
    
    try:
        # 1. 从info端点获取数据
        info_data = _fetch_from_info(stock, ticker)
        
        # 2. 从financials端点获取数据
        financials_data = _fetch_from_financials(stock, ticker)
        
        # 3. 从quarterly_financials端点获取数据（可选）
        quarterly_data = _fetch_from_quarterly(stock, ticker)
        
        # 4. 交叉验证
        validated_data = _cross_validate_endpoints(
            ticker=ticker,
            info=info_data,
            financials=financials_data,
            quarterly=quarterly_data
        )
        
        if not validated_data:
            logger.warning(f"{ticker}: 多端点验证失败")
            return None
        
        # 5. 构建StockData
        stock_data = _build_stock_data(ticker, validated_data)
        
        if stock_data:
            logger.info(f"{ticker}: 多端点验证成功 - PE={stock_data.pe:.2f}, PEG={stock_data.peg:.2f}, confidence={stock_data.confidence}")
        
        return stock_data
        
    except Exception as e:
        logger.error(f"{ticker}: 多端点验证失败 - {str(e)}")
        return None


def _fetch_from_info(stock: yf.Ticker, ticker: str) -> Optional[Dict]:
    """从info端点获取数据"""
    try:
        info = stock.info
        
        return {
            'price': info.get('currentPrice') or info.get('regularMarketPrice'),
            'pe': info.get('trailingPE') or info.get('forwardPE'),
            'peg': info.get('pegRatio'),
            'market_cap': info.get('marketCap'),
            'eps': info.get('trailingEps'),
        }
    except Exception as e:
        logger.debug(f"{ticker}: info端点失败 - {e}")
        return None


def _fetch_from_financials(stock: yf.Ticker, ticker: str) -> Optional[Dict]:
    """从financials端点获取数据（计算增长率）"""
    try:
        financials = stock.financials
        
        if financials.empty or 'Net Income' not in financials.index:
            return None
        
        # 获取最近2年的净利润
        net_incomes = financials.loc['Net Income']
        if len(net_incomes) < 2:
            return None
        
        latest = net_incomes.iloc[0]
        previous = net_incomes.iloc[1]
        
        # 计算增长率
        growth_rate = None
        if previous != 0:
            growth_rate = float((latest - previous) / abs(previous))
        
        return {
            'net_income': float(latest),
            'growth_rate': growth_rate,
        }
    except Exception as e:
        logger.debug(f"{ticker}: financials端点失败 - {e}")
        return None


def _fetch_from_quarterly(stock: yf.Ticker, ticker: str) -> Optional[Dict]:
    """从quarterly_financials端点获取数据"""
    try:
        quarterly = stock.quarterly_financials
        
        if quarterly.empty or 'Net Income' not in quarterly.index:
            return None
        
        # 获取最近4个季度的TTM净利润
        net_incomes = quarterly.loc['Net Income']
        if len(net_incomes) < 4:
            return None
        
        ttm_income = sum(net_incomes.iloc[:4])
        
        return {
            'ttm_income': float(ttm_income),
        }
    except Exception as e:
        logger.debug(f"{ticker}: quarterly端点失败 - {e}")
        return None


def _cross_validate_endpoints(
    ticker: str,
    info: Optional[Dict],
    financials: Optional[Dict],
    quarterly: Optional[Dict]
) -> Optional[Dict]:
    """
    交叉验证不同端点的数据
    
    Returns:
        验证后的数据字典，包含confidence字段
    """
    if not info:
        logger.warning(f"{ticker}: info端点无数据")
        return None
    
    if not financials:
        logger.warning(f"{ticker}: financials端点无数据")
        return None
    
    # 合并数据
    validated = {
        'price': info.get('price'),
        'pe': info.get('pe'),
        'peg': info.get('peg'),
        'market_cap': info.get('market_cap'),
        'eps': info.get('eps'),
        'net_income': financials.get('net_income'),
        'growth_rate': financials.get('growth_rate'),
        'ttm_income': quarterly.get('ttm_income') if quarterly else None,
    }
    
    # 验证必要字段
    if validated['price'] is None:
        logger.warning(f"{ticker}: 缺少价格数据")
        return None
    
    if validated['pe'] is None:
        logger.warning(f"{ticker}: 缺少PE数据")
        return None
    
    if validated['growth_rate'] is None:
        logger.warning(f"{ticker}: 缺少增长率数据")
        return None
    
    # 交叉验证净利润（如果有quarterly数据）
    if validated['ttm_income'] and validated['net_income']:
        deviation = abs(validated['ttm_income'] - validated['net_income']) / abs(validated['net_income'])
        
        if deviation > 0.3:  # 偏差>30%
            logger.warning(f"{ticker}: 年度与TTM净利润偏差较大 ({deviation*100:.1f}%)")
            validated['confidence'] = "MEDIUM"
        else:
            logger.info(f"{ticker}: 净利润数据一致 (偏差{deviation*100:.1f}%)")
            validated['confidence'] = "HIGH"
    else:
        # 只有单一来源
        validated['confidence'] = "MEDIUM"
    
    # 计算或验证PEG
    if validated['pe'] and validated['growth_rate']:
        calculated_peg = validated['pe'] / (validated['growth_rate'] * 100)
        
        if validated['peg']:
            # 比较info端点的PEG和计算的PEG
            deviation = abs(calculated_peg - validated['peg']) / max(abs(validated['peg']), 0.01)
            
            if deviation > 0.5:  # 偏差>50%
                logger.warning(f"{ticker}: info的PEG与计算的PEG偏差较大 ({deviation*100:.1f}%)")
                validated['peg'] = calculated_peg  # 使用计算值
                validated['confidence'] = "MEDIUM"
        else:
            validated['peg'] = calculated_peg
    
    return validated


def _build_stock_data(ticker: str, data: Dict) -> Optional[StockData]:
    """构建StockData对象"""
    try:
        # 数据验证
        validation_errors = []
        
        # PE验证
        if not ValidationRules.validate_pe(data['pe'], ticker):
            validation_errors.append("PE无效")
        
        # PEG验证
        if not ValidationRules.validate_peg(data['peg'], ticker):
            validation_errors.append("PEG无效")
        
        # 增长率验证
        if not ValidationRules.validate_growth_rate(data['growth_rate'], ticker):
            validation_errors.append("增长率无效")
        
        if validation_errors:
            logger.error(f"{ticker}: 数据被拒绝 - {'; '.join(validation_errors)}")
            return None
        
        return StockData(
            ticker=ticker,
            date=datetime.now().strftime('%Y-%m-%d'),
            price=float(data['price']),
            pe=float(data['pe']),
            peg=float(data['peg']),
            ttm_profit=float(data['net_income']) if data.get('net_income') else 0.0,
            growth_rate=float(data['growth_rate']),
            market_cap=float(data['market_cap']) if data.get('market_cap') else None,
            data_source="yfinance_multiendpoint",
            confidence=data.get('confidence', 'MEDIUM')
        )
        
    except Exception as e:
        logger.error(f"{ticker}: 构建数据失败 - {str(e)}")
        return None

