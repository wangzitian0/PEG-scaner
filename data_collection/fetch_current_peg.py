"""
获取当前七姐妹的PEG数据
"""

import logging
import pandas as pd
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from data_collection.fetch_yfinance import fetch_stock_data, validate_stock_data
from data_collection.cache_manager import get_cache_manager
from core.models import StockData

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config() -> dict:
    """加载配置文件"""
    config_path = Path(__file__).parent.parent / 'config.yaml'
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.warning(f"加载配置文件失败: {e}，使用默认配置")
        return {}


def get_mag7_tickers() -> List[str]:
    """获取美股+港股七姐妹股票代码"""
    config = load_config()
    
    # 从配置文件获取
    if 'target_stocks' in config:
        us_stocks = [s['ticker'] for s in config['target_stocks'].get('mag7_us', [])]
        hk_stocks = [s['ticker'] for s in config['target_stocks'].get('hk_tech', [])]
        return us_stocks + hk_stocks
    
    # 默认列表
    return [
        # 美股七姐妹
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
        # 港股七姐妹
        '00700.HK', '09988.HK', '03690.HK', '01810.HK', 
        '09618.HK', '01211.HK', '09999.HK'
    ]


def fetch_peg_data(ticker: str, use_cache: bool = True) -> StockData:
    """
    获取单只股票的PEG数据
    
    Args:
        ticker: 股票代码
        use_cache: 是否使用缓存
    
    Returns:
        StockData对象
    """
    date = datetime.now().strftime('%Y-%m-%d')
    cache = get_cache_manager()
    
    # 尝试从缓存读取
    if use_cache:
        cached_data = cache.get(ticker, date)
        if cached_data:
            logger.info(f"{ticker}: 使用缓存数据")
            return cached_data
    
    # 从API获取
    logger.info(f"{ticker}: 从API获取数据")
    stock_data = fetch_stock_data(ticker, date)
    
    if stock_data and validate_stock_data(stock_data):
        # 保存到缓存
        cache.set(stock_data)
        return stock_data
    else:
        logger.error(f"{ticker}: 数据获取失败")
        return None


def fetch_peg_batch(tickers: List[str], use_cache: bool = True, max_workers: int = 10) -> List[StockData]:
    """
    并行获取多只股票的PEG数据
    
    Args:
        tickers: 股票代码列表
        use_cache: 是否使用缓存
        max_workers: 最大并行数
    
    Returns:
        StockData列表
    """
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交任务
        future_to_ticker = {
            executor.submit(fetch_peg_data, ticker, use_cache): ticker
            for ticker in tickers
        }
        
        # 收集结果
        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                data = future.result()
                if data:
                    results.append(data)
            except Exception as e:
                logger.error(f"{ticker}: 处理失败 - {e}")
    
    return results


def save_results(data_list: List[StockData], output_dir: str = './results'):
    """
    保存结果到CSV和Markdown
    
    Args:
        data_list: StockData列表
        output_dir: 输出目录
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    date = datetime.now().strftime('%Y-%m-%d')
    
    # 转换为DataFrame
    rows = [data.to_table_row() for data in data_list]
    df = pd.DataFrame(rows)
    
    # 保存CSV
    csv_file = output_path / f'mag7_peg_{date}.csv'
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    logger.info(f"CSV已保存: {csv_file}")
    
    # 保存Markdown
    md_file = output_path / f'mag7_peg_{date}.md'
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# 美股+港股七姐妹 PEG数据\n\n")
        f.write(f"**更新时间**: {date}\n\n")
        f.write(df.to_markdown(index=False))
        f.write(f"\n\n---\n")
        f.write(f"*数据来源: yfinance*\n")
    
    logger.info(f"Markdown已保存: {md_file}")
    
    # 打印摘要
    print("\n" + "="*60)
    print(f"{'公司名称':<20} {'净利润':<15} {'增速':<10} {'PE':<8} {'PEG':<8}")
    print("="*60)
    for data in data_list:
        row = data.to_table_row()
        print(f"{row['公司名称']:<20} {row['净利润']:<15} {row['利润增速']:<10} {row['TTM PE']:<8} {row['PEG']:<8}")
    print("="*60)


def main():
    """主函数"""
    logger.info("开始获取七姐妹PEG数据...")
    
    # 获取股票列表
    tickers = get_mag7_tickers()
    logger.info(f"目标股票: {', '.join(tickers)}")
    
    # 批量获取数据
    data_list = fetch_peg_batch(tickers, use_cache=True)
    
    if not data_list:
        logger.error("没有成功获取任何数据!")
        return
    
    logger.info(f"成功获取 {len(data_list)}/{len(tickers)} 只股票的数据")
    
    # 保存结果
    save_results(data_list)
    
    logger.info("完成!")


if __name__ == '__main__':
    main()

