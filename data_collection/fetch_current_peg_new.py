"""
获取当前PEG数据（使用新的IO规范）

遵循 agent.md (30-31):
- 按schema组织数据
- 命名：schema-name-source-date.csv
"""

import logging
from datetime import datetime
from typing import List

from data_collection.fetch_yfinance import fetch_stock_data
from core.data_io import save_to_csv
import pandas as pd

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_mag7_tickers() -> List[str]:
    """获取美股+港股七姐妹ticker列表"""
    us_mag7 = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
    hk_mag7 = ["00700.HK", "09988.HK", "03690.HK", "01810.HK", "09618.HK", "01211.HK", "09999.HK"]
    return us_mag7 + hk_mag7


def fetch_peg_batch(tickers: List[str], use_cache: bool = True) -> List[dict]:
    """
    批量获取PEG数据
    
    Returns:
        List of dicts with schema: stock_fundamental
    """
    results = []
    date_today = datetime.now().strftime("%Y-%m-%d")
    
    for ticker in tickers:
        logger.info(f"获取 {ticker} 数据...")
        
        # 获取数据
        data = fetch_stock_data(ticker)
        
        if data:
            # 转换为符合schema的格式
            row = {
                "ticker": ticker,
                "date": date_today,
                "price": data.price,
                "pe": data.pe,
                "peg": data.peg,
                "net_income": data.profit if hasattr(data, 'profit') else None,
                "growth_rate": data.growth_rate,
                "market_cap": None,  # TODO: 添加市值计算
                "source": "yfinance",
                "confidence": data.confidence
            }
            results.append(row)
            logger.info(f"{ticker}: PE={data.pe}, PEG={data.peg}")
        else:
            logger.warning(f"{ticker}: 数据获取失败")
    
    return results


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("开始获取七姐妹PEG数据（新IO规范）")
    logger.info("=" * 60)
    
    # 获取ticker列表
    tickers = get_mag7_tickers()
    logger.info(f"目标股票: {', '.join(tickers)}")
    
    # 批量获取数据
    data_list = fetch_peg_batch(tickers, use_cache=True)
    
    if not data_list:
        logger.error("没有成功获取任何数据!")
        return
    
    logger.info(f"成功获取 {len(data_list)}/{len(tickers)} 只股票的数据")
    
    # 转换为DataFrame
    df = pd.DataFrame(data_list)
    
    # 使用新的IO工具保存
    # schema: stock_fundamental
    # name: mag7
    # source: yfinance
    # date: 自动使用今天
    
    csv_path = save_to_csv(
        data=df,
        schema="stock_fundamental",
        name="mag7",
        source="yfinance",
        date=None  # 自动使用今天
    )
    
    logger.info(f"✅ 数据已保存: {csv_path}")
    
    # 打印简要统计
    print("\n" + "=" * 80)
    print(f"成功获取 {len(df)} 只股票的PEG数据")
    print(f"文件路径: {csv_path}")
    print("=" * 80)
    print(f"\nPEG最低的5只股票:")
    top5 = df.nsmallest(5, 'peg')[['ticker', 'pe', 'peg', 'growth_rate', 'confidence']]
    print(top5.to_string(index=False))
    print("=" * 80)
    
    logger.info("完成!")


if __name__ == "__main__":
    main()

