"""
双重验证数据采集

策略：使用yfinance的不同方法作为两个验证源
- Source 1: 单端点（info）- 快速但可能不准确
- Source 2: 多端点交叉验证 - 慢但更可靠
- Aggregated: 两个源都通过验证的数据

虽然同属yfinance，但通过不同方法提取和验证，提高数据可靠性
"""

import logging
from datetime import datetime
from typing import List, Dict
import pandas as pd

from data_collection.fetch_yfinance import fetch_stock_data as fetch_single
from data_collection.fetch_yfinance_multiendpoint import fetch_stock_data_multiendpoint as fetch_multi
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
    从两个验证源获取数据
    
    Returns:
        {
            'yfinance_single': [单端点数据列表],
            'yfinance_multi': [多端点数据列表],
            'aggregated': [两个源都通过的数据列表]
        }
    """
    date_today = datetime.now().strftime("%Y-%m-%d")
    
    results = {
        'yfinance_single': [],
        'yfinance_multi': [],
        'aggregated': []
    }
    
    for ticker in tickers:
        logger.info(f"\n{'='*60}")
        logger.info(f"处理 {ticker}")
        logger.info(f"{'='*60}")
        
        # 1. 单端点方法
        logger.info(f"[1/3] 单端点方法...")
        single_data = fetch_single(ticker)
        
        if single_data:
            results['yfinance_single'].append({
                "ticker": ticker,
                "date": date_today,
                "price": single_data.price,
                "pe": single_data.pe,
                "peg": single_data.peg,
                "net_income": single_data.ttm_profit,
                "growth_rate": single_data.growth_rate,
                "market_cap": single_data.market_cap,
                "source": "yfinance_single",
                "confidence": single_data.confidence
            })
            logger.info(f"✅ 单端点: PE={single_data.pe:.2f}, PEG={single_data.peg:.2f}")
        else:
            logger.warning(f"❌ 单端点: 获取失败")
        
        # 2. 多端点交叉验证方法
        logger.info(f"[2/3] 多端点验证...")
        multi_data = fetch_multi(ticker)
        
        if multi_data:
            results['yfinance_multi'].append({
                "ticker": ticker,
                "date": date_today,
                "price": multi_data.price,
                "pe": multi_data.pe,
                "peg": multi_data.peg,
                "net_income": multi_data.ttm_profit,
                "growth_rate": multi_data.growth_rate,
                "market_cap": multi_data.market_cap,
                "source": "yfinance_multi",
                "confidence": multi_data.confidence
            })
            logger.info(f"✅ 多端点: PE={multi_data.pe:.2f}, PEG={multi_data.peg:.2f}")
        else:
            logger.warning(f"❌ 多端点: 获取失败")
        
        # 3. 双重验证：比较两个源的数据一致性
        if single_data and multi_data:
            logger.info(f"[3/3] 双重验证...")
            
            # 比较关键指标
            pe_deviation = abs(single_data.pe - multi_data.pe) / max(abs(multi_data.pe), 0.01)
            peg_deviation = abs(single_data.peg - multi_data.peg) / max(abs(multi_data.peg), 0.01)
            
            logger.info(f"  PE偏差: {pe_deviation*100:.1f}%")
            logger.info(f"  PEG偏差: {peg_deviation*100:.1f}%")
            
            # 如果偏差不大，认为数据可靠
            if pe_deviation < 0.15 and peg_deviation < 0.20:  # PE偏差<15%, PEG偏差<20%
                # 使用多端点的数据（更可靠）
                confidence = "HIGH" if pe_deviation < 0.05 and peg_deviation < 0.10 else "MEDIUM"
                
                results['aggregated'].append({
                    "ticker": ticker,
                    "date": date_today,
                    "price": multi_data.price,
                    "pe": multi_data.pe,
                    "peg": multi_data.peg,
                    "net_income": multi_data.ttm_profit,
                    "growth_rate": multi_data.growth_rate,
                    "market_cap": multi_data.market_cap,
                    "source": "aggregated_dual_verified",
                    "confidence": confidence
                })
                logger.info(f"✅ 双重验证通过: confidence={confidence}")
            else:
                logger.warning(f"❌ 双重验证失败: PE或PEG偏差过大")
        else:
            logger.warning(f"⚠️ 跳过双重验证：缺少数据源")
    
    return results


def main():
    """主函数"""
    logger.info("="*80)
    logger.info("开始双重验证数据采集")
    logger.info("="*80)
    
    # 获取ticker列表
    tickers = get_mag7_tickers()
    logger.info(f"\n目标股票: {', '.join(tickers)}")
    logger.info(f"验证策略: yfinance单端点 + yfinance多端点交叉验证")
    logger.info(f"验证要求: PE偏差<15%, PEG偏差<20%\n")
    
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
    logger.info(f"yfinance_single: {len(all_data['yfinance_single'])} 条")
    logger.info(f"yfinance_multi:  {len(all_data['yfinance_multi'])} 条")
    logger.info(f"aggregated:      {len(all_data['aggregated'])} 条（通过双重验证）")
    logger.info(f"{'='*80}")
    
    if len(all_data['aggregated']) >= 7:
        logger.info(f"\n✅ Phrase 1 完成！生成了{len(all_data['aggregated'])}条双重验证数据")
        logger.info(f"验证方式: yfinance单端点 + yfinance多端点交叉验证")
    else:
        logger.warning(f"\n⚠️ 双重验证数据不足7条，Phrase 1未达标")


if __name__ == "__main__":
    main()

