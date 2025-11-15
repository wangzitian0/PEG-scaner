"""
数据缓存管理器
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
from core.models import StockData

logger = logging.getLogger(__name__)

# 默认配置（遵循数据持久化原则）
DEFAULT_CACHE_DIR = './data/cache'
DEFAULT_CACHE_EXPIRY = 24 * 3600  # 24小时


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str = DEFAULT_CACHE_DIR, expiry_seconds: int = DEFAULT_CACHE_EXPIRY):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录
            expiry_seconds: 缓存过期时间（秒）
        """
        self.cache_dir = Path(cache_dir)
        self.expiry_seconds = expiry_seconds
        
        # 创建缓存目录
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"缓存目录: {self.cache_dir}")
    
    def _get_cache_path(self, ticker: str, date: str = 'latest') -> Path:
        """
        获取缓存文件路径
        
        Args:
            ticker: 股票代码
            date: 日期
        
        Returns:
            缓存文件路径
        """
        safe_ticker = ticker.replace('/', '_').replace('\\', '_')
        return self.cache_dir / f"{safe_ticker}_{date}.json"
    
    def get(self, ticker: str, date: str = 'latest') -> Optional[StockData]:
        """
        从缓存读取数据
        
        Args:
            ticker: 股票代码
            date: 日期
        
        Returns:
            StockData对象，不存在或过期返回None
        """
        cache_file = self._get_cache_path(ticker, date)
        
        if not cache_file.exists():
            logger.debug(f"缓存不存在: {cache_file}")
            return None
        
        # 检查是否过期
        file_time = cache_file.stat().st_mtime
        if time.time() - file_time > self.expiry_seconds:
            logger.info(f"缓存已过期: {cache_file}")
            return None
        
        # 读取缓存
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data_dict = json.load(f)
            
            stock_data = StockData(**data_dict)
            logger.info(f"从缓存读取: {ticker}")
            return stock_data
        
        except Exception as e:
            logger.error(f"读取缓存失败: {cache_file} - {e}")
            return None
    
    def set(self, stock_data: StockData) -> bool:
        """
        保存数据到缓存
        
        Args:
            stock_data: StockData对象
        
        Returns:
            是否成功
        """
        try:
            cache_file = self._get_cache_path(stock_data.ticker, stock_data.date)
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(stock_data.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"保存到缓存: {stock_data.ticker}")
            return True
        
        except Exception as e:
            logger.error(f"保存缓存失败: {stock_data.ticker} - {e}")
            return False
    
    def clear_expired(self) -> int:
        """
        清理过期缓存
        
        Returns:
            清理的文件数量
        """
        count = 0
        current_time = time.time()
        
        for cache_file in self.cache_dir.glob('*.json'):
            file_time = cache_file.stat().st_mtime
            if current_time - file_time > self.expiry_seconds:
                try:
                    cache_file.unlink()
                    count += 1
                    logger.debug(f"删除过期缓存: {cache_file}")
                except Exception as e:
                    logger.error(f"删除缓存失败: {cache_file} - {e}")
        
        if count > 0:
            logger.info(f"清理了 {count} 个过期缓存")
        
        return count
    
    def clear_all(self) -> int:
        """
        清理所有缓存
        
        Returns:
            清理的文件数量
        """
        count = 0
        
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                cache_file.unlink()
                count += 1
            except Exception as e:
                logger.error(f"删除缓存失败: {cache_file} - {e}")
        
        logger.info(f"清理了 {count} 个缓存文件")
        return count
    
    def get_cache_size(self) -> tuple:
        """
        获取缓存统计信息
        
        Returns:
            (文件数量, 总大小MB)
        """
        count = 0
        total_size = 0
        
        for cache_file in self.cache_dir.glob('*.json'):
            count += 1
            total_size += cache_file.stat().st_size
        
        return count, total_size / (1024 * 1024)


# 全局缓存管理器实例
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """
    获取全局缓存管理器实例
    
    Returns:
        CacheManager实例
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


if __name__ == '__main__':
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    cache = CacheManager('./test_cache')
    
    # 测试存储
    test_data = StockData(
        ticker='TEST',
        date='2025-11-15',
        price=100.0,
        ttm_profit=1000000000,
        growth_rate=0.2,
        pe=20.0,
        peg=1.0
    )
    
    cache.set(test_data)
    
    # 测试读取
    cached = cache.get('TEST', '2025-11-15')
    if cached:
        print(f"读取成功: {cached.ticker}, PEG={cached.peg}")
    
    # 测试统计
    count, size = cache.get_cache_size()
    print(f"缓存文件: {count}个, 大小: {size:.2f}MB")

