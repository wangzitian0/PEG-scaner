"""
格式化工具测试
"""

import pytest
from core.format_utils import (
    format_profit,
    format_ticker_name,
    format_growth_rate,
    normalize_ticker,
    get_currency_from_ticker
)


class TestFormatUtils:
    """测试格式化工具"""
    
    def test_format_profit_billions(self):
        """测试十亿级利润格式化"""
        result = format_profit(88_100_000_000, 'USD')
        assert result == "$88.1B"
    
    def test_format_profit_millions(self):
        """测试百万级利润格式化"""
        result = format_profit(50_000_000, 'USD')
        assert result == "$50.0M"
    
    def test_format_profit_hkd(self):
        """测试港币格式化"""
        result = format_profit(179_400_000_000, 'HKD')
        assert result == "¥179.4B"
    
    def test_format_profit_zero(self):
        """测试零利润"""
        result = format_profit(0, 'USD')
        assert result == 'N/A'
    
    def test_format_ticker_name_us_stock(self):
        """测试美股格式化（小写）"""
        result = format_ticker_name('MSFT')
        assert result == '微软<msft.us>'
    
    def test_format_ticker_name_hk_stock(self):
        """测试港股格式化（保留00700格式）"""
        result = format_ticker_name('700.HK')
        assert result == '腾讯<00700.hk>'
    
    def test_format_ticker_name_unknown(self):
        """测试未知股票代码"""
        result = format_ticker_name('UNKN')
        assert 'unkn' in result.lower()
    
    def test_format_growth_rate_positive(self):
        """测试正增长率"""
        result = format_growth_rate(0.218)
        assert result == "21.8%"
    
    def test_format_growth_rate_negative(self):
        """测试负增长率"""
        result = format_growth_rate(-0.123)
        assert result == "-12.3%"
    
    def test_format_growth_rate_none(self):
        """测试None增长率"""
        result = format_growth_rate(None)
        assert result == 'N/A'
    
    def test_normalize_ticker_us(self):
        """测试美股代码标准化"""
        result = normalize_ticker('msft')
        assert result == 'MSFT'
    
    def test_normalize_ticker_hk(self):
        """测试港股代码标准化（去前导0）"""
        result = normalize_ticker('00700.HK')
        assert result == '700.HK'
    
    def test_normalize_ticker_hk_no_leading_zero(self):
        """测试港股代码（已无前导0）"""
        result = normalize_ticker('9988.HK')
        assert result == '9988.HK'
    
    def test_get_currency_from_ticker_us(self):
        """测试美股货币推断"""
        result = get_currency_from_ticker('MSFT')
        assert result == 'USD'
    
    def test_get_currency_from_ticker_hk(self):
        """测试港股货币推断"""
        result = get_currency_from_ticker('700.HK')
        assert result == 'HKD'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

