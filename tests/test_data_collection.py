"""
数据采集模块集成测试
"""

import pytest
from unittest.mock import Mock, patch
from core.models import StockData
from data_collection.fetch_yfinance import fetch_stock_data, validate_stock_data
from data_collection.cache_manager import CacheManager


class TestYFinanceDataSource:
    """测试yfinance数据源"""
    
    @pytest.mark.skipif(True, reason="需要网络连接，CI/CD环境跳过")
    def test_fetch_real_data(self):
        """测试获取真实数据（需要网络）"""
        data = fetch_stock_data('MSFT')
        
        assert data is not None
        assert data.ticker == 'MSFT'
        assert data.price > 0
        assert data.pe > 0
        assert data.data_source == 'yfinance'
    
    def test_fetch_invalid_ticker(self):
        """测试无效股票代码"""
        data = fetch_stock_data('INVALID_TICKER_XYZ')
        assert data is None
    
    def test_validate_valid_data(self):
        """测试验证有效数据"""
        valid_data = StockData(
            ticker='TEST',
            date='2025-11-15',
            price=100.0,
            ttm_profit=1_000_000_000,
            growth_rate=0.2,
            pe=20.0,
            peg=1.0,
            data_source='test'
        )
        
        assert validate_stock_data(valid_data) is True
    
    def test_validate_invalid_price(self):
        """测试验证无效价格"""
        invalid_data = StockData(
            ticker='TEST',
            date='2025-11-15',
            price=-10.0,  # 负价格
            ttm_profit=1_000_000_000,
            growth_rate=0.2,
            pe=20.0,
            peg=1.0,
            data_source='test'
        )
        
        assert validate_stock_data(invalid_data) is False


class TestCacheManager:
    """测试缓存管理器"""
    
    def test_cache_set_and_get(self, tmp_path):
        """测试缓存存取"""
        cache = CacheManager(cache_dir=str(tmp_path / 'cache'))
        
        test_data = StockData(
            ticker='TEST',
            date='2025-11-15',
            price=100.0,
            ttm_profit=1_000_000_000,
            growth_rate=0.2,
            pe=20.0,
            peg=1.0,
            data_source='test'
        )
        
        # 存储
        assert cache.set(test_data) is True
        
        # 读取
        cached = cache.get('TEST', '2025-11-15')
        assert cached is not None
        assert cached.ticker == 'TEST'
        assert cached.peg == 1.0
    
    def test_cache_expiry(self, tmp_path):
        """测试缓存过期"""
        cache = CacheManager(cache_dir=str(tmp_path / 'cache'), expiry_seconds=1)
        
        test_data = StockData(
            ticker='TEST',
            date='2025-11-15',
            price=100.0,
            ttm_profit=1_000_000_000,
            growth_rate=0.2,
            pe=20.0,
            peg=1.0,
            data_source='test'
        )
        
        cache.set(test_data)
        
        # 立即读取应该成功
        assert cache.get('TEST', '2025-11-15') is not None
        
        # 等待过期后应该返回None
        import time
        time.sleep(2)
        assert cache.get('TEST', '2025-11-15') is None
    
    def test_cache_clear(self, tmp_path):
        """测试清理缓存"""
        cache = CacheManager(cache_dir=str(tmp_path / 'cache'))
        
        # 创建多个缓存
        for i in range(5):
            test_data = StockData(
                ticker=f'TEST{i}',
                date='2025-11-15',
                price=100.0,
                ttm_profit=1_000_000_000,
                growth_rate=0.2,
                pe=20.0,
                peg=1.0,
                data_source='test'
            )
            cache.set(test_data)
        
        # 清理所有缓存
        count = cache.clear_all()
        assert count == 5
        
        # 验证缓存已清空
        count, size = cache.get_cache_size()
        assert count == 0


class TestDataAggregator:
    """测试数据聚合器"""
    
    @patch('data_collection.fetch_yfinance.fetch_stock_data')
    @patch('data_collection.fetch_alpha_vantage.fetch_stock_data')
    def test_cross_validation_both_succeed(self, mock_av, mock_yf):
        """测试双数据源都成功的情况"""
        from data_collection.data_aggregator import fetch_with_cross_validation
        
        # Mock数据
        mock_data_yf = StockData(
            ticker='TEST',
            date='2025-11-15',
            price=100.0,
            ttm_profit=1_000_000_000,
            growth_rate=0.2,
            pe=20.0,
            peg=1.0,
            data_source='yfinance'
        )
        
        mock_data_av = StockData(
            ticker='TEST',
            date='2025-11-15',
            price=101.0,  # 1%偏差，可接受
            ttm_profit=1_050_000_000,
            growth_rate=0.21,
            pe=20.5,
            peg=0.98,
            data_source='alpha_vantage'
        )
        
        mock_yf.return_value = mock_data_yf
        mock_av.return_value = mock_data_av
        
        # 执行
        result = fetch_with_cross_validation('TEST', use_cache=False)
        
        # 验证
        assert result is not None
        assert result.data_source == 'yfinance+alpha_vantage'
        assert result.confidence == 'HIGH'
    
    @patch('data_collection.fetch_yfinance.fetch_stock_data')
    @patch('data_collection.fetch_alpha_vantage.fetch_stock_data')
    def test_cross_validation_only_yf_succeeds(self, mock_av, mock_yf):
        """测试仅yfinance成功的情况"""
        from data_collection.data_aggregator import fetch_with_cross_validation
        
        mock_data_yf = StockData(
            ticker='TEST',
            date='2025-11-15',
            price=100.0,
            ttm_profit=1_000_000_000,
            growth_rate=0.2,
            pe=20.0,
            peg=1.0,
            data_source='yfinance'
        )
        
        mock_yf.return_value = mock_data_yf
        mock_av.return_value = None  # Alpha Vantage失败
        
        # 执行
        result = fetch_with_cross_validation('TEST', use_cache=False)
        
        # 验证
        assert result is not None
        assert result.data_source == 'yfinance'
        assert result.confidence == 'MEDIUM'  # 降低置信度


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

