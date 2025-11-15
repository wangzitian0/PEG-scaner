"""
数据IO工具

遵循 agent.md (30-31) 命名规范：
- 文件名格式：{schema}-{name}-{source}-{date}.csv
- 按schema组织数据目录
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 数据根目录（程序生成的数据放x-data/，遵循agent.md Line 48）
DATA_ROOT = Path("x-data")

# Schema目录映射
SCHEMA_DIRS = {
    "stock_daily": DATA_ROOT / "stock_daily",
    "stock_fundamental": DATA_ROOT / "stock_fundamental",
    "etf_portfolio": DATA_ROOT / "etf_portfolio",
    "backtest_result": DATA_ROOT / "backtest_result",
    "analysis_result": DATA_ROOT / "analysis_result",
}


def build_filename(schema: str, name: str, source: str, date: str) -> str:
    """
    构建符合规范的文件名
    
    格式: {schema}-{name}-{source}-{date}.csv
    
    Args:
        schema: stock_daily, stock_fundamental, etf_portfolio等
        name: 数据集名称（mag7, sp500, vgt等）
        source: 数据来源（yfinance, aggregated等）
        date: 日期（YYYYMMDD 或 YYYYMMDD_YYYYMMDD）
        
    Returns:
        文件名字符串
        
    Example:
        >>> build_filename("stock_fundamental", "mag7", "yfinance", "20251115")
        "stock_fundamental-mag7-yfinance-20251115.csv"
    """
    return f"{schema}-{name}-{source}-{date}.csv"


def get_schema_dir(schema: str) -> Path:
    """
    获取schema对应的目录
    
    Args:
        schema: schema名称
        
    Returns:
        Path对象
    """
    if schema not in SCHEMA_DIRS:
        raise ValueError(f"未知的schema: {schema}. 支持的schema: {list(SCHEMA_DIRS.keys())}")
    
    dir_path = SCHEMA_DIRS[schema]
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def save_to_csv(
    data: pd.DataFrame,
    schema: str,
    name: str,
    source: str,
    date: Optional[str] = None
) -> Path:
    """
    保存数据到CSV文件
    
    Args:
        data: DataFrame数据
        schema: schema名称
        name: 数据集名称
        source: 数据来源
        date: 日期（可选，默认使用今天）
        
    Returns:
        保存的文件路径
        
    Example:
        >>> df = pd.DataFrame(...)
        >>> path = save_to_csv(df, "stock_fundamental", "mag7", "yfinance")
        >>> print(path)
        data/stock_fundamental/stock_fundamental-mag7-yfinance-20251115.csv
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    # 获取目录
    dir_path = get_schema_dir(schema)
    
    # 构建文件名
    filename = build_filename(schema, name, source, date)
    filepath = dir_path / filename
    
    # 保存CSV
    data.to_csv(filepath, index=False, encoding='utf-8')
    logger.info(f"数据已保存: {filepath}")
    
    return filepath


def load_from_csv(
    schema: str,
    name: str,
    source: str,
    date: str
) -> pd.DataFrame:
    """
    从CSV文件加载数据
    
    Args:
        schema: schema名称
        name: 数据集名称
        source: 数据来源
        date: 日期
        
    Returns:
        DataFrame
        
    Raises:
        FileNotFoundError: 文件不存在
        
    Example:
        >>> df = load_from_csv("stock_fundamental", "mag7", "yfinance", "20251115")
    """
    dir_path = get_schema_dir(schema)
    filename = build_filename(schema, name, source, date)
    filepath = dir_path / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    df = pd.read_csv(filepath)
    logger.info(f"数据已加载: {filepath}, 行数={len(df)}")
    
    return df


def find_files(
    schema: str,
    name: Optional[str] = None,
    source: Optional[str] = None,
    date: Optional[str] = None
) -> List[Path]:
    """
    查找符合条件的文件
    
    Args:
        schema: schema名称（必须）
        name: 数据集名称（可选）
        source: 数据来源（可选）
        date: 日期（可选）
        
    Returns:
        文件路径列表
        
    Example:
        >>> # 找所有mag7的基本面数据
        >>> files = find_files("stock_fundamental", name="mag7")
        
        >>> # 找特定日期的aggregated数据
        >>> files = find_files("stock_fundamental", source="aggregated", date="20251115")
    """
    dir_path = get_schema_dir(schema)
    
    # 构建搜索模式
    parts = [schema]
    parts.append(name if name else "*")
    parts.append(source if source else "*")
    parts.append(date if date else "*")
    pattern = "-".join(parts) + ".csv"
    
    files = list(dir_path.glob(pattern))
    logger.info(f"找到 {len(files)} 个文件匹配 {pattern}")
    
    return sorted(files)


def load_all_sources(
    schema: str,
    name: str,
    date: str
) -> Dict[str, pd.DataFrame]:
    """
    加载同一数据的所有source
    
    Args:
        schema: schema名称
        name: 数据集名称
        date: 日期
        
    Returns:
        Dict[source, DataFrame]
        
    Example:
        >>> sources = load_all_sources("stock_fundamental", "mag7", "20251115")
        >>> print(sources.keys())
        dict_keys(['yfinance', 'alphavantage', 'aggregated'])
    """
    files = find_files(schema, name=name, date=date)
    
    result = {}
    for filepath in files:
        # 从文件名提取source
        # stock_fundamental-mag7-yfinance-20251115.csv -> yfinance
        parts = filepath.stem.split("-")
        if len(parts) >= 4:
            source = parts[2]
            df = pd.read_csv(filepath)
            result[source] = df
            logger.info(f"加载 {source}: {len(df)} 行")
    
    return result


def get_latest_file(
    schema: str,
    name: str,
    source: str
) -> Optional[Path]:
    """
    获取最新的文件
    
    Args:
        schema: schema名称
        name: 数据集名称
        source: 数据来源
        
    Returns:
        最新文件路径，如果不存在返回None
        
    Example:
        >>> path = get_latest_file("stock_fundamental", "mag7", "aggregated")
        >>> if path:
        >>>     df = pd.read_csv(path)
    """
    files = find_files(schema, name=name, source=source)
    
    if not files:
        return None
    
    # 按文件名排序（日期部分）返回最新的
    return files[-1]


def format_date_range(start_date: str, end_date: str) -> str:
    """
    格式化日期范围
    
    Args:
        start_date: 开始日期 (YYYY-MM-DD 或 YYYYMMDD)
        end_date: 结束日期 (YYYY-MM-DD 或 YYYYMMDD)
        
    Returns:
        格式化的日期范围 (YYYYMMDD_YYYYMMDD)
        
    Example:
        >>> format_date_range("2024-01-01", "2025-11-14")
        "20240101_20251114"
    """
    # 移除可能的分隔符
    start = start_date.replace("-", "")
    end = end_date.replace("-", "")
    return f"{start}_{end}"


def parse_filename(filename: str) -> Dict[str, str]:
    """
    解析文件名
    
    Args:
        filename: 文件名（不含路径）
        
    Returns:
        Dict包含schema, name, source, date
        
    Example:
        >>> info = parse_filename("stock_fundamental-mag7-yfinance-20251115.csv")
        >>> print(info)
        {'schema': 'stock_fundamental', 'name': 'mag7', 'source': 'yfinance', 'date': '20251115'}
    """
    # 移除.csv后缀
    if filename.endswith('.csv'):
        filename = filename[:-4]
    
    parts = filename.split("-")
    if len(parts) < 4:
        raise ValueError(f"文件名格式错误: {filename}. 应为 schema-name-source-date.csv")
    
    return {
        "schema": parts[0],
        "name": parts[1],
        "source": parts[2],
        "date": "-".join(parts[3:])  # 日期可能包含_
    }


# 导出所有函数
__all__ = [
    'build_filename',
    'get_schema_dir',
    'save_to_csv',
    'load_from_csv',
    'find_files',
    'load_all_sources',
    'get_latest_file',
    'format_date_range',
    'parse_filename',
]

