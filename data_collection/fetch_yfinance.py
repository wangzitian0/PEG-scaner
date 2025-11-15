"""
yfinance数据源实现
"""

import yfinance as yf
import logging
from datetime import datetime
from typing import Optional
from core.models import StockData
from core.format_utils import normalize_ticker, get_currency_from_ticker
from core.schemas.validation_rules import ValidationRules

logger = logging.getLogger(__name__)


def fetch_stock_data(ticker: str, date: Optional[str] = None) -> Optional[StockData]:
    """
    从yfinance获取股票数据并计算PEG
    
    Args:
        ticker: 股票代码（如'MSFT', '00700.HK'）
        date: 数据日期（默认为最新）
    
    Returns:
        StockData对象，失败返回None
    """
    try:
        # 标准化股票代码
        ticker = normalize_ticker(ticker)
        logger.info(f"正在获取 {ticker} 的数据...")
        
        # 创建yfinance对象
        stock = yf.Ticker(ticker)
        
        # 获取基础信息
        info = stock.info
        
        # 获取当前价格
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        if not price:
            logger.warning(f"{ticker}: 无法获取价格数据")
            return None
        
        # 获取市值
        market_cap = info.get('marketCap')
        
        # 获取流通股本
        shares_outstanding = info.get('sharesOutstanding')
        
        # 获取财务数据
        try:
            # 获取季度财报
            quarterly_income = stock.quarterly_income_stmt
            
            if quarterly_income is None or quarterly_income.empty:
                logger.warning(f"{ticker}: 无季度财报数据")
                return None
            
            # 计算TTM净利润（最近4季度）
            if 'Net Income' in quarterly_income.index:
                net_income_row = quarterly_income.loc['Net Income']
            elif 'NetIncome' in quarterly_income.index:
                net_income_row = quarterly_income.loc['NetIncome']
            else:
                logger.warning(f"{ticker}: 找不到净利润数据")
                return None
            
            # 获取最近4个季度的数据
            if len(net_income_row) < 4:
                logger.warning(f"{ticker}: 季度数据不足4个")
                return None
            
            ttm_profit = float(net_income_row.iloc[:4].sum())
            
            # 计算去年同期TTM（第5-8季度）
            if len(net_income_row) >= 8:
                ttm_profit_last_year = float(net_income_row.iloc[4:8].sum())
                
                # 计算增长率
                if ttm_profit_last_year != 0:
                    growth_rate = (ttm_profit - ttm_profit_last_year) / abs(ttm_profit_last_year)
                else:
                    growth_rate = 0.0
            else:
                # 尝试使用年度数据
                try:
                    annual_income = stock.income_stmt
                    if annual_income is not None and not annual_income.empty:
                        if 'Net Income' in annual_income.index:
                            annual_ni = annual_income.loc['Net Income']
                        elif 'NetIncome' in annual_income.index:
                            annual_ni = annual_income.loc['NetIncome']
                        else:
                            annual_ni = None
                        
                        if annual_ni is not None and len(annual_ni) >= 2:
                            current_year = float(annual_ni.iloc[0])
                            last_year = float(annual_ni.iloc[1])
                            if last_year != 0:
                                growth_rate = (current_year - last_year) / abs(last_year)
                            else:
                                growth_rate = 0.0
                            logger.info(f"{ticker}: 使用年度数据计算增长率")
                        else:
                            growth_rate = 0.0
                    else:
                        growth_rate = 0.0
                except Exception as e:
                    logger.warning(f"{ticker}: 年度数据获取失败 - {e}")
                    growth_rate = 0.0
            
            # 计算PE
            if shares_outstanding and ttm_profit > 0:
                eps = ttm_profit / shares_outstanding
                pe = price / eps
            else:
                # 尝试从info获取
                pe = info.get('trailingPE') or info.get('forwardPE')
                if not pe:
                    logger.warning(f"{ticker}: 无法计算PE")
                    pe = 0.0
            
            # 计算PEG
            if pe > 0 and growth_rate > 0:
                peg = pe / (growth_rate * 100)
            else:
                peg = 0.0
                if growth_rate <= 0:
                    logger.info(f"{ticker}: 增长率为负或零，PEG设为0")
            
            # 确定货币
            currency = get_currency_from_ticker(ticker)
            
            # 获取收入数据（可选）
            ttm_revenue = None
            if 'Total Revenue' in quarterly_income.index:
                revenue_row = quarterly_income.loc['Total Revenue']
                if len(revenue_row) >= 4:
                    ttm_revenue = float(revenue_row.iloc[:4].sum())
            
            # 严格数据验证：宁可为空，不要使用错的数据
            should_reject, reject_reason = ValidationRules.should_reject_data(
                pe=float(pe),
                peg=float(peg),
                growth_rate=growth_rate,
                price=float(price),
                ticker=ticker
            )
            
            if should_reject:
                logger.error(f"{ticker}: 数据被拒绝 - {reject_reason}")
                return None
            
            # 构建StockData对象
            stock_data = StockData(
                ticker=ticker,
                date=date or datetime.now().strftime('%Y-%m-%d'),
                price=float(price),
                market_cap=float(market_cap) if market_cap else None,
                ttm_profit=ttm_profit,
                ttm_revenue=ttm_revenue,
                shares_outstanding=float(shares_outstanding) if shares_outstanding else None,
                growth_rate=growth_rate,
                pe=float(pe),
                peg=float(peg),
                currency=currency,
                data_source='yfinance',
                confidence='HIGH'
            )
            
            # 额外的警告检查
            _, pe_warning = ValidationRules.validate_pe(float(pe), ticker)
            _, peg_warning = ValidationRules.validate_peg(float(peg), ticker)
            _, growth_warning = ValidationRules.validate_growth_rate(growth_rate, ticker)
            
            if pe_warning or peg_warning or growth_warning:
                stock_data.confidence = 'MEDIUM'
                warnings = [w for w in [pe_warning, peg_warning, growth_warning] if w]
                stock_data.error_message = "; ".join(warnings)
            
            logger.info(f"{ticker}: 数据获取成功 - PE={pe:.2f}, PEG={peg:.2f}, 置信度={stock_data.confidence}")
            return stock_data
            
        except Exception as e:
            logger.error(f"{ticker}: 财务数据处理失败 - {str(e)}")
            return None
    
    except Exception as e:
        logger.error(f"{ticker}: 数据获取失败 - {str(e)}")
        return None


def validate_stock_data(data: StockData) -> bool:
    """
    验证股票数据质量
    
    Args:
        data: StockData对象
    
    Returns:
        是否通过验证
    """
    if not data:
        return False
    
    # 价格检查
    if data.price <= 0:
        logger.warning(f"{data.ticker}: 价格异常 ({data.price})")
        return False
    
    # PE检查
    if data.pe < 0 or data.pe > 300:
        logger.warning(f"{data.ticker}: PE异常 ({data.pe})")
        data.confidence = 'LOW'
    
    # PEG检查
    if data.peg < -5 or data.peg > 10:
        logger.warning(f"{data.ticker}: PEG异常 ({data.peg})")
        data.confidence = 'LOW'
    
    # 增长率检查
    if data.growth_rate < -1 or data.growth_rate > 5:
        logger.warning(f"{data.ticker}: 增长率异常 ({data.growth_rate})")
        data.confidence = 'LOW'
    
    return True


def get_company_name(ticker: str) -> str:
    """
    获取公司全称
    
    Args:
        ticker: 股票代码
    
    Returns:
        公司名称
    """
    try:
        ticker = normalize_ticker(ticker)
        stock = yf.Ticker(ticker)
        return stock.info.get('longName') or stock.info.get('shortName') or ticker
    except Exception as e:
        logger.error(f"获取{ticker}公司名失败: {e}")
        return ticker


if __name__ == '__main__':
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 测试美股
    print("\n=== 测试美股：微软 ===")
    msft_data = fetch_stock_data('MSFT')
    if msft_data:
        print(f"价格: ${msft_data.price:.2f}")
        print(f"净利润: {msft_data.ttm_profit/1e9:.1f}B")
        print(f"增长率: {msft_data.growth_rate:.1%}")
        print(f"PE: {msft_data.pe:.2f}")
        print(f"PEG: {msft_data.peg:.2f}")
        print(f"表格行: {msft_data.to_table_row()}")
    
    # 测试港股
    print("\n=== 测试港股：腾讯 ===")
    tencent_data = fetch_stock_data('00700.HK')
    if tencent_data:
        print(f"价格: HKD {tencent_data.price:.2f}")
        print(f"净利润: {tencent_data.ttm_profit/1e9:.1f}B")
        print(f"增长率: {tencent_data.growth_rate:.1%}")
        print(f"PE: {tencent_data.pe:.2f}")
        print(f"PEG: {tencent_data.peg:.2f}")

