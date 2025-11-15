"""
数据验证规则测试
"""

import pytest
from core.schemas.validation_rules import ValidationRules


class TestValidationRules:
    """测试数据验证规则"""
    
    def test_validate_pe_normal(self):
        """测试正常PE值"""
        valid, msg = ValidationRules.validate_pe(20.0, "TEST")
        assert valid is True
        assert msg is None
    
    def test_validate_pe_negative(self):
        """测试负PE值（应拒绝）"""
        valid, msg = ValidationRules.validate_pe(-5.0, "TEST")
        assert valid is False
        assert "负" in msg
    
    def test_validate_pe_too_high(self):
        """测试过高PE值（应拒绝）"""
        valid, msg = ValidationRules.validate_pe(350.0, "TEST")
        assert valid is False
        assert "过高" in msg
    
    def test_validate_pe_warning_low(self):
        """测试异常低PE值（通过但警告）"""
        valid, msg = ValidationRules.validate_pe(2.5, "TEST")
        assert valid is True
        assert msg is not None
        assert "异常低" in msg
    
    def test_validate_pe_warning_high(self):
        """测试异常高PE值（通过但警告）"""
        valid, msg = ValidationRules.validate_pe(150.0, "TEST")
        assert valid is True
        assert msg is not None
        assert "异常高" in msg
    
    def test_validate_peg_normal(self):
        """测试正常PEG值"""
        valid, msg = ValidationRules.validate_peg(1.5, "TEST")
        assert valid is True
        assert msg is None
    
    def test_validate_peg_low(self):
        """测试低PEG值（正常）"""
        valid, msg = ValidationRules.validate_peg(0.3, "TEST")
        assert valid is True
    
    def test_validate_peg_out_of_range(self):
        """测试PEG超出范围（应拒绝）"""
        valid, msg = ValidationRules.validate_peg(15.0, "TEST")
        assert valid is False
        assert "超出范围" in msg
    
    def test_validate_growth_rate_normal(self):
        """测试正常增长率"""
        valid, msg = ValidationRules.validate_growth_rate(0.25, "TEST")  # 25%
        assert valid is True
        assert msg is None
    
    def test_validate_growth_rate_negative(self):
        """测试负增长率（合理范围内）"""
        valid, msg = ValidationRules.validate_growth_rate(-0.3, "TEST")  # -30%
        assert valid is True
    
    def test_validate_growth_rate_too_low(self):
        """测试过低增长率（应拒绝）"""
        valid, msg = ValidationRules.validate_growth_rate(-1.5, "TEST")  # -150%
        assert valid is False
        assert "过低" in msg
    
    def test_validate_growth_rate_too_high(self):
        """测试过高增长率（应拒绝）"""
        valid, msg = ValidationRules.validate_growth_rate(6.0, "TEST")  # 600%
        assert valid is False
        assert "过高" in msg
    
    def test_validate_price_normal(self):
        """测试正常价格"""
        valid, msg = ValidationRules.validate_price(100.50, "TEST")
        assert valid is True
        assert msg is None
    
    def test_validate_price_too_low(self):
        """测试过低价格（应拒绝）"""
        valid, msg = ValidationRules.validate_price(0.001, "TEST")
        assert valid is False
        assert "过低" in msg
    
    def test_validate_profit_above_threshold(self):
        """测试利润超过门槛"""
        valid, msg = ValidationRules.validate_profit(50_000_000, "TEST")
        assert valid is True
    
    def test_validate_profit_below_threshold(self):
        """测试利润低于门槛（应拒绝）"""
        valid, msg = ValidationRules.validate_profit(5_000_000, "TEST")
        assert valid is False
        assert "低于门槛" in msg
    
    def test_check_cross_source_deviation_acceptable(self):
        """测试可接受的跨源偏差"""
        acceptable, deviation = ValidationRules.check_cross_source_deviation(
            100.0, 102.0, "PE", "TEST"
        )
        assert acceptable is True
        assert deviation < 0.05
    
    def test_check_cross_source_deviation_unacceptable(self):
        """测试不可接受的跨源偏差"""
        acceptable, deviation = ValidationRules.check_cross_source_deviation(
            100.0, 120.0, "PE", "TEST"
        )
        assert acceptable is False
        assert deviation > 0.05
    
    def test_should_reject_data_valid(self):
        """测试有效数据（不应拒绝）"""
        should_reject, reason = ValidationRules.should_reject_data(
            pe=20.0,
            peg=1.5,
            growth_rate=0.3,
            price=100.0,
            ticker="TEST"
        )
        assert should_reject is False
        assert reason == ""
    
    def test_should_reject_data_invalid_pe(self):
        """测试无效PE（应拒绝）"""
        should_reject, reason = ValidationRules.should_reject_data(
            pe=-10.0,
            peg=1.5,
            growth_rate=0.3,
            price=100.0,
            ticker="TEST"
        )
        assert should_reject is True
        assert "PE无效" in reason
    
    def test_should_reject_data_invalid_peg(self):
        """测试无效PEG（应拒绝）"""
        should_reject, reason = ValidationRules.should_reject_data(
            pe=20.0,
            peg=15.0,
            growth_rate=0.3,
            price=100.0,
            ticker="TEST"
        )
        assert should_reject is True
        assert "PEG无效" in reason
    
    def test_should_reject_data_invalid_growth(self):
        """测试无效增长率（应拒绝）"""
        should_reject, reason = ValidationRules.should_reject_data(
            pe=20.0,
            peg=1.5,
            growth_rate=-2.0,
            price=100.0,
            ticker="TEST"
        )
        assert should_reject is True
        assert "增长率无效" in reason
    
    def test_should_reject_data_invalid_price(self):
        """测试无效价格（应拒绝）"""
        should_reject, reason = ValidationRules.should_reject_data(
            pe=20.0,
            peg=1.5,
            growth_rate=0.3,
            price=0.001,
            ticker="TEST"
        )
        assert should_reject is True
        assert "价格无效" in reason


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

