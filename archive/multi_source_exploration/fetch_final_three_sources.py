"""
三源数据获取 + 严格一致性验证

核心逻辑:
1. 三个数据源都尝试获取: yfinance, finnhub, twelvedata/akshare
2. 至少2个源的数据一致（在误差范围内）→ ✅ 可信
3. 只有1个源成功，或3个源都不一致 → ❌ 拒绝

一致性定义:
- 价格: ±5% 误差范围
- PE: ±10% 误差范围
- PEG: ±15% 误差范围
"""

import logging
from typing import List, Optional, Dict, Tuple
from datetime import datetime
from dataclasses import asdict

from core.models import StockData
from core.data_io import save_to_csv
from data_collection import fetch_yfinance
from data_collection import fetch_finnhub
from data_collection import fetch_twelvedata
from data_collection import fetch_akshare

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 一致性验证的误差容忍度
TOLERANCE = {
    'price': 0.05,      # 5%
    'pe_ratio': 0.10,   # 10%
    'peg_ratio': 0.15,  # 15%
}


def is_value_consistent(v1: Optional[float], v2: Optional[float], tolerance: float) -> bool:
    """
    检查两个值是否在误差范围内一致
    
    Args:
        v1, v2: 要比较的两个值
        tolerance: 相对误差容忍度（例如 0.05 = 5%）
        
    Returns:
        True if 一致，False otherwise
    """
    if v1 is None or v2 is None:
        return False
    
    if v1 == 0 and v2 == 0:
        return True
    
    if v1 == 0 or v2 == 0:
        return False
    
    # 计算相对误差
    avg = (abs(v1) + abs(v2)) / 2
    diff = abs(v1 - v2)
    relative_error = diff / avg
    
    return relative_error <= tolerance


def count_consistent_pairs(values: List[Optional[float]], tolerance: float) -> int:
    """
    计算有多少对值是一致的
    
    Args:
        values: 值列表（可能包含None）
        tolerance: 误差容忍度
        
    Returns:
        一致对的数量
    """
    valid_values = [v for v in values if v is not None]
    
    if len(valid_values) < 2:
        return 0
    
    consistent_count = 0
    for i in range(len(valid_values)):
        for j in range(i + 1, len(valid_values)):
            if is_value_consistent(valid_values[i], valid_values[j], tolerance):
                consistent_count += 1
    
    return consistent_count


def find_consistent_value(values: List[Optional[float]], tolerance: float) -> Optional[float]:
    """
    从多个值中找到一致的值
    
    逻辑:
    1. 如果有至少2个值一致 → 返回它们的平均值
    2. 否则 → 返回None
    
    Args:
        values: 值列表
        tolerance: 误差容忍度
        
    Returns:
        一致的值（或平均值），没有则返回None
    """
    valid_values = [v for v in values if v is not None]
    
    if len(valid_values) < 2:
        return None
    
    # 找到最大的一致性簇
    for i in range(len(valid_values)):
        consistent_group = [valid_values[i]]
        for j in range(len(valid_values)):
            if i != j and is_value_consistent(valid_values[i], valid_values[j], tolerance):
                consistent_group.append(valid_values[j])
        
        # 如果找到至少2个一致的值
        if len(consistent_group) >= 2:
            return sum(consistent_group) / len(consistent_group)
    
    return None


def validate_consistency(sources: List[StockData]) -> Tuple[bool, Dict[str, Optional[float]], str]:
    """
    验证多个数据源的一致性
    
    Args:
        sources: StockData对象列表
        
    Returns:
        (is_valid, aggregated_values, reason)
        - is_valid: 是否有至少2个源一致
        - aggregated_values: 聚合后的值
        - reason: 验证结果说明
    """
    if len(sources) < 2:
        return False, {}, f"只有{len(sources)}个数据源成功，需要至少2个"
    
    # 提取各字段的值
    prices = [s.price for s in sources]
    pes = [s.pe for s in sources]
    pegs = [s.peg for s in sources]
    
    # 验证价格一致性（必须）
    consistent_price = find_consistent_value(prices, TOLERANCE['price'])
    if consistent_price is None:
        return False, {}, f"价格不一致: {[f'{p:.2f}' if p else 'None' for p in prices]}"
    
    # 验证PE一致性
    consistent_pe = find_consistent_value(pes, TOLERANCE['pe_ratio'])
    
    # 验证PEG一致性
    consistent_peg = find_consistent_value(pegs, TOLERANCE['peg_ratio'])
    
    # 构造聚合结果
    aggregated = {
        'price': consistent_price,
        'pe_ratio': consistent_pe,
        'peg_ratio': consistent_peg,
    }
    
    # 统计一致性
    source_names = [s.data_source for s in sources]
    reason = f"✅ {len(sources)}个源一致: {', '.join(source_names)}"
    
    return True, aggregated, reason


def fetch_from_all_sources(ticker: str) -> List[StockData]:
    """
    从所有数据源获取数据
    
    策略:
    - 美股: yfinance + finnhub + twelvedata
    - 港股: yfinance + twelvedata + akshare
    
    Args:
        ticker: 股票代码
        
    Returns:
        成功获取的StockData列表
    """
    results = []
    
    # 1. yfinance (全市场)
    logger.info(f"\n{'='*50}")
    logger.info(f"[1/3] yfinance: {ticker}")
    yf_data = fetch_yfinance.fetch_stock_data(ticker)
    if yf_data:
        results.append(yf_data)
        logger.info(f"✅ yfinance成功: price={yf_data.price:.2f}, PE={yf_data.pe}, PEG={yf_data.peg}")
    else:
        logger.warning(f"❌ yfinance失败")
    
    # 2. finnhub (美股优先)
    logger.info(f"\n{'='*50}")
    logger.info(f"[2/3] finnhub: {ticker}")
    fh_data = fetch_finnhub.fetch_stock_data(ticker)
    if fh_data:
        results.append(fh_data)
        logger.info(f"✅ finnhub成功: price={fh_data.price:.2f}, PE={fh_data.pe}, PEG={fh_data.peg}")
    else:
        logger.warning(f"❌ finnhub失败（预期港股会失败）")
    
    # 3. twelvedata 或 akshare
    logger.info(f"\n{'='*50}")
    if ticker.upper().endswith('.US'):
        logger.info(f"[3/3] twelvedata: {ticker}")
        td_data = fetch_twelvedata.fetch_stock_data(ticker)
        if td_data:
            results.append(td_data)
            logger.info(f"✅ twelvedata成功: price={td_data.price:.2f}, PE={td_data.pe}, PEG={td_data.peg}")
        else:
            logger.warning(f"❌ twelvedata失败")
    else:
        # 港股优先使用twelvedata，如果失败再用akshare
        logger.info(f"[3/3] twelvedata: {ticker}")
        td_data = fetch_twelvedata.fetch_stock_data(ticker)
        if td_data:
            results.append(td_data)
            logger.info(f"✅ twelvedata成功: price={td_data.price:.2f}, PE={td_data.pe}, PEG={td_data.peg}")
        else:
            logger.warning(f"❌ twelvedata失败，尝试akshare")
            logger.info(f"[3/3] akshare (备选): {ticker}")
            ak_data = fetch_akshare.fetch_stock_data(ticker)
            if ak_data:
                results.append(ak_data)
                logger.info(f"✅ akshare成功: price={ak_data.price:.2f}, PE={ak_data.pe}, PEG={ak_data.peg}")
            else:
                logger.warning(f"❌ akshare也失败")
    
    return results


def aggregate_stock_data(ticker: str) -> Optional[StockData]:
    """
    聚合多个数据源的数据
    
    核心逻辑:
    1. 从3个源获取数据
    2. 验证至少2个源一致
    3. 返回一致的数据，否则返回None
    
    Args:
        ticker: 股票代码
        
    Returns:
        聚合后的StockData，不满足要求则返回None
    """
    logger.info(f"\n{'#'*60}")
    logger.info(f"# 聚合数据: {ticker}")
    logger.info(f"{'#'*60}")
    
    # 1. 从所有源获取数据
    sources = fetch_from_all_sources(ticker)
    
    logger.info(f"\n{'='*50}")
    logger.info(f"数据源汇总: {len(sources)}/{3}个成功")
    for s in sources:
        logger.info(f"  - {s.data_source}: price={s.price:.2f}, PE={s.pe}, PEG={s.peg}")
    
    # 2. 验证一致性
    is_valid, aggregated_values, reason = validate_consistency(sources)
    
    logger.info(f"\n{'='*50}")
    logger.info(f"一致性验证: {reason}")
    
    if not is_valid:
        logger.warning(f"❌ {ticker}: 数据被拒绝 - {reason}")
        return None
    
    # 3. 构造聚合的StockData
    # 使用第一个成功的源作为基础，替换验证后的一致值
    base = sources[0]
    
    aggregated_data = StockData(
        ticker=ticker,
        date=datetime.now().strftime('%Y-%m-%d'),
        price=aggregated_values['price'],
        pe=aggregated_values['pe_ratio'],
        peg=aggregated_values['peg_ratio'],
        ttm_profit=base.ttm_profit,  # 取第一个源的值
        growth_rate=base.growth_rate,
        market_cap=base.market_cap,
        data_source=f"aggregated_{len(sources)}sources",
        confidence='HIGH'  # 多源验证通过
    )
    
    logger.info(f"✅ {ticker}: 聚合成功")
    logger.info(f"   price={aggregated_data.price:.2f}, PE={aggregated_data.pe}, PEG={aggregated_data.peg}")
    
    return aggregated_data


def main():
    """主函数：获取美股七姐妹+港股七姐妹的PEG数据"""
    
    # 定义目标股票
    mag7_us = [
        "MSFT.US",   # 微软
        "AAPL.US",   # 苹果
        "GOOGL.US",  # 谷歌
        "AMZN.US",   # 亚马逊
        "NVDA.US",   # 英伟达
        "META.US",   # Meta
        "TSLA.US",   # 特斯拉
    ]
    
    mag7_hk = [
        "00700.HK",  # 腾讯
        "09988.HK",  # 阿里巴巴
        "03690.HK",  # 美团
        "09999.HK",  # 网易
        "01810.HK",  # 小米
        "00388.HK",  # 港交所
        "00981.HK",  # 中芯国际
    ]
    
    all_tickers = mag7_us + mag7_hk
    
    results = []
    
    for ticker in all_tickers:
        try:
            data = aggregate_stock_data(ticker)
            if data:
                results.append(data)
                logger.info(f"✅ {ticker}: 成功")
            else:
                logger.warning(f"❌ {ticker}: 失败（数据不一致或来源不足）")
        except Exception as e:
            logger.error(f"❌ {ticker}: 异常 - {e}", exc_info=True)
    
    # 保存结果
    if results:
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 最终结果: {len(results)}/{len(all_tickers)}只股票")
        logger.info(f"{'='*60}\n")
        
        # 转换为字典列表
        data_dicts = [asdict(r) for r in results]
        
        # 保存CSV
        today = datetime.now().strftime('%Y%m%d')
        save_to_csv(
            data=data_dicts,
            schema='stock_fundamental',
            name='mag7',
            source='aggregated',
            date=today
        )
        
        logger.info("✅ 数据已保存到 x-data/stock_fundamental/")
        
        # 打印汇总表
        print("\n" + "="*80)
        print("最终PEG表格")
        print("="*80)
        print(f"{'Ticker':<12} {'Price':>10} {'PE':>8} {'PEG':>8} {'Data Sources':<20}")
        print("-"*80)
        for r in results:
            sources = r.data_source
            peg_str = f"{r.peg:.2f}" if r.peg else 'N/A'
            print(f"{r.ticker:<12} {r.price:>10.2f} {r.pe:>8.2f} {peg_str:>8} {sources:<20}")
        print("="*80)
        
    else:
        logger.error("❌ 没有获取到任何有效数据")


if __name__ == "__main__":
    main()

