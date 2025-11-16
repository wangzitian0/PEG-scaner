"""
完整的多源数据采集脚本

遵循 agent.md Line 28: 至少两个数据源且相同，才进行下一步
"""

import logging
from datetime import datetime
from typing import List, Dict
import pandas as pd

from data_collection.fetch_yfinance import fetch_stock_data as fetch_yf
from data_collection.fetch_fmp import fetch_stock_data as fetch_fmp
from data_collection.data_aggregator import fetch_with_cross_validation
from core.data_io import save_to_csv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_mag7_tickers() -> List[str]:
    """获取美股+港股七姐妹"""
    us_mag7 = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
    hk_mag7 = ["00700.HK", "09988.HK", "03690.HK", "01810.HK", "09618.HK", "01211.HK", "09999.HK"]
    return us_mag7 + hk_mag7


def fetch_all_sources(tickers: List[str]) -> Dict:
    """
    从所有数据源获取数据
    
    Returns:
        {
            'yfinance': [股票数据列表],
            'alphavantage': [股票数据列表],
            'aggregated': [验证后的数据列表]
        }
    """
    date_today = datetime.now().strftime("%Y-%m-%d")
    
    results = {
        'yfinance': [],
        'fmp': [],
        'aggregated': []
    }
    
    for ticker in tickers:
        logger.info(f"\n{'='*60}")
        logger.info(f"处理 {ticker}")
        logger.info(f"{'='*60}")
        
        # 1. 从yfinance获取
        logger.info(f"[1/3] 从yfinance获取数据...")
        yf_data = fetch_yf(ticker)
        
        if yf_data:
            results['yfinance'].append({
                "ticker": ticker,
                "date": date_today,
                "price": yf_data.price,
                "pe": yf_data.pe,
                "peg": yf_data.peg,
                "net_income": None,
                "growth_rate": yf_data.growth_rate,
                "market_cap": None,
                "source": "yfinance",
                "confidence": yf_data.confidence
            })
            logger.info(f"✅ yfinance: PE={yf_data.pe:.2f}, PEG={yf_data.peg:.2f}")
        else:
            logger.warning(f"❌ yfinance: 获取失败")
        
        # 2. 从FMP获取
        logger.info(f"[2/3] 从Financial Modeling Prep获取数据...")
        fmp_data = fetch_fmp(ticker)
        
        if fmp_data:
            results['fmp'].append({
                "ticker": ticker,
                "date": date_today,
                "price": fmp_data.price,
                "pe": fmp_data.pe,
                "peg": fmp_data.peg,
                "net_income": None,
                "growth_rate": fmp_data.growth_rate,
                "market_cap": None,
                "source": "fmp",
                "confidence": fmp_data.confidence
            })
            logger.info(f"✅ fmp: PE={fmp_data.pe:.2f}, PEG={fmp_data.peg:.2f}")
        else:
            logger.warning(f"❌ fmp: 获取失败")
        
        # 3. 多源聚合验证（直接使用data_aggregator的交叉验证）
        logger.info(f"[3/3] 多源验证...")
        aggregated = fetch_with_cross_validation(ticker, use_cache=False, require_both_sources=True)
        
        if aggregated:
            results['aggregated'].append({
                    "ticker": ticker,
                    "date": date_today,
                    "price": aggregated.price,
                    "pe": aggregated.pe,
                    "peg": aggregated.peg,
                    "net_income": None,
                    "growth_rate": aggregated.growth_rate,
                    "market_cap": None,
                    "source": "aggregated",
                    "confidence": aggregated.confidence
                })
            logger.info(f"✅ aggregated: PE={aggregated.pe:.2f}, PEG={aggregated.peg:.2f}, confidence={aggregated.confidence}")
        else:
            logger.warning(f"❌ 多源验证失败：数据偏差过大或数据源不足")
    
    return results


def main():
    """主函数"""
    logger.info("="*80)
    logger.info("开始完整的多源数据采集（遵循agent.md Line 28）")
    logger.info("="*80)
    
    # 获取ticker列表
    tickers = get_mag7_tickers()
    logger.info(f"\n目标股票: {', '.join(tickers)}")
    logger.info(f"数据源: yfinance + Financial Modeling Prep")
    logger.info(f"验证要求: 至少2个数据源相同\n")
    
    # 获取所有源的数据
    all_data = fetch_all_sources(tickers)
    
    # 保存结果
    date_str = datetime.now().strftime("%Y%m%d")
    
    for source, data_list in all_data.items():
        if data_list:
            df = pd.DataFrame(data_list)
            path = save_to_csv(
                data=df,
                schema="stock_fundamental",
                name="mag7",
                source=source,
                date=date_str
            )
            logger.info(f"\n✅ {source}: 保存{len(df)}条数据到 {path}")
        else:
            logger.warning(f"\n⚠️ {source}: 无数据")
    
    # 统计
    logger.info(f"\n{'='*80}")
    logger.info("数据采集完成统计")
    logger.info(f"{'='*80}")
    logger.info(f"yfinance: {len(all_data['yfinance'])} 条")
    logger.info(f"fmp:      {len(all_data['fmp'])} 条")
    logger.info(f"aggregated: {len(all_data['aggregated'])} 条（通过验证）")
    logger.info(f"{'='*80}")
    
    if len(all_data['aggregated']) > 0:
        logger.info(f"\n✅ Phrase 1 真正完成！生成了{len(all_data['aggregated'])}条多源验证数据")
    else:
        logger.warning(f"\n⚠️ 没有通过多源验证的数据，Phrase 1未完成！")


if __name__ == "__main__":
    main()
