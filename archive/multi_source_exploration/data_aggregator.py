"""
数据聚合器：整合多数据源并进行交叉验证

原则：宁可为空，不要使用错的数据
"""

import logging
from typing import Optional, List, Tuple
from datetime import datetime

from core.models import StockData
from core.schemas.validation_rules import ValidationRules
from data_collection import fetch_yfinance
from data_collection import fetch_alpha_vantage
from data_collection.cache_manager import get_cache_manager

logger = logging.getLogger(__name__)


def fetch_with_cross_validation(
    ticker: str,
    date: Optional[str] = None,
    use_cache: bool = True,
    require_both_sources: bool = False
) -> Optional[StockData]:
    """
    使用双数据源交叉验证获取股票数据
    
    策略：
    1. 尝试从缓存读取
    2. 从yfinance获取（主数据源）
    3. 从Alpha Vantage获取（备用数据源）
    4. 交叉验证两个数据源的结果
    5. 根据一致性选择最终数据
    
    Args:
        ticker: 股票代码
        date: 数据日期
        use_cache: 是否使用缓存
        require_both_sources: 是否要求两个数据源都成功
    
    Returns:
        StockData对象，验证失败返回None
    """
    date = date or datetime.now().strftime('%Y-%m-%d')
    cache = get_cache_manager()
    
    # 1. 尝试从缓存读取
    if use_cache:
        cached_data = cache.get(ticker, date)
        if cached_data:
            logger.info(f"{ticker}: 使用缓存数据")
            return cached_data
    
    # 2. 从主数据源获取（yfinance）
    logger.info(f"{ticker}: 从yfinance获取数据...")
    data_yf = fetch_yfinance.fetch_stock_data(ticker, date)
    
    # 3. 从备用数据源获取（Alpha Vantage）
    logger.info(f"{ticker}: 从Alpha Vantage获取数据...")
    data_av = fetch_alpha_vantage.fetch_stock_data(ticker, date)
    
    # 4. 交叉验证
    if data_yf and data_av:
        logger.info(f"{ticker}: 两个数据源都成功，进行交叉验证")
        final_data, confidence = _cross_validate(ticker, data_yf, data_av)
        
        if final_data:
            final_data.confidence = confidence
            cache.set(final_data)
            return final_data
        else:
            logger.error(f"{ticker}: 交叉验证失败，数据不一致")
            if require_both_sources:
                return None
            # 回退到单数据源
            logger.warning(f"{ticker}: 回退到yfinance单数据源")
            data_yf.confidence = 'LOW'
            cache.set(data_yf)
            return data_yf
    
    elif data_yf:
        logger.warning(f"{ticker}: 仅yfinance成功，Alpha Vantage失败")
        if require_both_sources:
            return None
        data_yf.confidence = 'MEDIUM'
        data_yf.error_message = "仅单数据源（yfinance）"
        cache.set(data_yf)
        return data_yf
    
    elif data_av:
        logger.warning(f"{ticker}: 仅Alpha Vantage成功，yfinance失败")
        if require_both_sources:
            return None
        data_av.confidence = 'MEDIUM'
        data_av.error_message = "仅单数据源（Alpha Vantage）"
        cache.set(data_av)
        return data_av
    
    else:
        logger.error(f"{ticker}: 所有数据源都失败")
        return None


def _cross_validate(
    ticker: str,
    data1: StockData,
    data2: StockData
) -> Tuple[Optional[StockData], str]:
    """
    交叉验证两个数据源的数据
    
    Returns:
        (最终数据, 置信度)
    """
    # 检查关键指标的偏差
    pe_ok, pe_dev = ValidationRules.check_cross_source_deviation(
        data1.pe, data2.pe, "PE", ticker
    )
    
    peg_ok, peg_dev = ValidationRules.check_cross_source_deviation(
        data1.peg, data2.peg, "PEG", ticker
    ) if data1.peg > 0 and data2.peg > 0 else (True, 0.0)
    
    growth_ok, growth_dev = ValidationRules.check_cross_source_deviation(
        data1.growth_rate, data2.growth_rate, "增长率", ticker
    )
    
    price_ok, price_dev = ValidationRules.check_cross_source_deviation(
        data1.price, data2.price, "价格", ticker
    )
    
    # 统计一致性
    checks = [price_ok, pe_ok, peg_ok, growth_ok]
    consistency_rate = sum(checks) / len(checks)
    
    logger.info(
        f"{ticker}: 数据一致性={consistency_rate*100:.0f}% "
        f"(价格偏差={price_dev*100:.1f}%, PE偏差={pe_dev*100:.1f}%, "
        f"PEG偏差={peg_dev*100:.1f}%, 增长率偏差={growth_dev*100:.1f}%)"
    )
    
    # 决策逻辑
    if consistency_rate >= 0.75:  # 75%以上一致
        # 使用平均值
        final_data = _average_data(data1, data2)
        
        if consistency_rate == 1.0:
            confidence = 'HIGH'
        else:
            confidence = 'MEDIUM'
        
        logger.info(f"{ticker}: 交叉验证通过，置信度={confidence}")
        return final_data, confidence
    
    else:
        # 不一致度太高，拒绝数据
        logger.warning(f"{ticker}: 数据源差异过大（一致性仅{consistency_rate*100:.0f}%），拒绝")
        return None, 'LOW'


def _average_data(data1: StockData, data2: StockData) -> StockData:
    """
    合并两个数据源的数据（使用平均值）
    
    优先使用yfinance的非关键字段（如市值、流通股等）
    """
    return StockData(
        ticker=data1.ticker,
        date=data1.date,
        # 价格和估值指标使用平均值
        price=(data1.price + data2.price) / 2,
        pe=(data1.pe + data2.pe) / 2,
        peg=(data1.peg + data2.peg) / 2 if data1.peg > 0 and data2.peg > 0 else data1.peg or data2.peg,
        growth_rate=(data1.growth_rate + data2.growth_rate) / 2,
        ttm_profit=(data1.ttm_profit + data2.ttm_profit) / 2,
        # 其他字段优先使用yfinance
        market_cap=data1.market_cap or data2.market_cap,
        ttm_revenue=data1.ttm_revenue or data2.ttm_revenue,
        shares_outstanding=data1.shares_outstanding or data2.shares_outstanding,
        currency=data1.currency,
        data_source='yfinance+alpha_vantage',
        confidence='HIGH'
    )


def fetch_batch_with_validation(
    tickers: List[str],
    use_cache: bool = True,
    max_workers: int = 5  # Alpha Vantage限流，降低并发数
) -> List[StockData]:
    """
    批量获取并验证数据
    
    Args:
        tickers: 股票代码列表
        use_cache: 是否使用缓存
        max_workers: 最大并发数（考虑Alpha Vantage限流）
    
    Returns:
        StockData列表
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ticker = {
            executor.submit(fetch_with_cross_validation, ticker, None, use_cache): ticker
            for ticker in tickers
        }
        
        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                data = future.result()
                if data:
                    results.append(data)
            except Exception as e:
                logger.error(f"{ticker}: 批量处理失败 - {e}")
    
    return results


if __name__ == '__main__':
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("\n=== 测试双数据源交叉验证 ===\n")
    
    # 测试单只股票
    print("测试MSFT...")
    data = fetch_with_cross_validation('MSFT', use_cache=False)
    if data:
        print(f"✓ 价格: ${data.price:.2f}")
        print(f"✓ PE: {data.pe:.2f}")
        print(f"✓ PEG: {data.peg:.2f}")
        print(f"✓ 数据源: {data.data_source}")
        print(f"✓ 置信度: {data.confidence}")
    else:
        print("✗ 数据获取失败")

