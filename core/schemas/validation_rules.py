"""
数据验证规则

原则：宁可为空，不要使用错的数据
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ValidationRules:
    """数据验证规则集"""
    
    # PE合理范围
    PE_MIN = 0
    PE_MAX = 300
    PE_WARNING_LOW = 3   # PE<3可能异常低
    PE_WARNING_HIGH = 100  # PE>100可能异常高
    
    # PEG合理范围
    PEG_MIN = -5
    PEG_MAX = 10
    PEG_INVALID_THRESHOLD = 100  # PEG>100视为无效
    
    # 增长率合理范围
    GROWTH_RATE_MIN = -1.0   # -100%
    GROWTH_RATE_MAX = 5.0    # 500%
    GROWTH_RATE_WARNING = 3.0  # >300%警告
    
    # 价格合理性
    PRICE_MIN = 0.01  # 最低价格$0.01
    
    # 利润最低门槛（美元）
    MIN_PROFIT_USD = 10_000_000  # $10M
    
    # 数据偏差阈值
    CROSS_SOURCE_DEVIATION_THRESHOLD = 0.05  # 5%
    
    @staticmethod
    def validate_pe(pe: float, ticker: str = "") -> tuple[bool, Optional[str]]:
        """
        验证PE合理性
        
        Returns:
            (是否有效, 警告信息)
        """
        if pe < ValidationRules.PE_MIN:
            return False, f"{ticker}: PE为负 ({pe:.2f})"
        
        if pe > ValidationRules.PE_MAX:
            return False, f"{ticker}: PE过高 ({pe:.2f}), 超过{ValidationRules.PE_MAX}"
        
        if pe < ValidationRules.PE_WARNING_LOW:
            logger.warning(f"{ticker}: PE异常低 ({pe:.2f})")
            return True, f"PE异常低 ({pe:.2f})"
        
        if pe > ValidationRules.PE_WARNING_HIGH:
            logger.warning(f"{ticker}: PE异常高 ({pe:.2f})")
            return True, f"PE异常高 ({pe:.2f})"
        
        return True, None
    
    @staticmethod
    def validate_peg(peg: float, ticker: str = "") -> tuple[bool, Optional[str]]:
        """验证PEG合理性"""
        if peg < ValidationRules.PEG_MIN or peg > ValidationRules.PEG_MAX:
            return False, f"{ticker}: PEG超出范围 ({peg:.2f})"
        
        if abs(peg) > ValidationRules.PEG_INVALID_THRESHOLD:
            return False, f"{ticker}: PEG过大 ({peg:.2f}), 视为无效"
        
        return True, None
    
    @staticmethod
    def validate_growth_rate(rate: float, ticker: str = "") -> tuple[bool, Optional[str]]:
        """验证增长率合理性"""
        if rate < ValidationRules.GROWTH_RATE_MIN:
            return False, f"{ticker}: 增长率过低 ({rate*100:.1f}%)"
        
        if rate > ValidationRules.GROWTH_RATE_MAX:
            return False, f"{ticker}: 增长率过高 ({rate*100:.1f}%)"
        
        if rate > ValidationRules.GROWTH_RATE_WARNING:
            logger.warning(f"{ticker}: 增长率异常高 ({rate*100:.1f}%)")
            return True, f"增长率异常高 ({rate*100:.1f}%)"
        
        return True, None
    
    @staticmethod
    def validate_price(price: float, ticker: str = "") -> tuple[bool, Optional[str]]:
        """验证价格合理性"""
        if price < ValidationRules.PRICE_MIN:
            return False, f"{ticker}: 价格过低 (${price:.2f})"
        
        return True, None
    
    @staticmethod
    def validate_profit(profit: float, ticker: str = "", 
                       min_threshold: float = MIN_PROFIT_USD) -> tuple[bool, Optional[str]]:
        """验证利润门槛"""
        if abs(profit) < min_threshold:
            return False, f"{ticker}: 利润低于门槛 (${profit/1e6:.1f}M < ${min_threshold/1e6:.1f}M)"
        
        return True, None
    
    @staticmethod
    def check_cross_source_deviation(value1: float, value2: float, 
                                     metric_name: str = "", 
                                     ticker: str = "") -> tuple[bool, float]:
        """
        检查跨数据源偏差
        
        Returns:
            (是否可接受, 偏差率)
        """
        if value1 == 0 or value2 == 0:
            return False, 0.0
        
        deviation = abs(value1 - value2) / max(abs(value1), abs(value2))
        
        if deviation > ValidationRules.CROSS_SOURCE_DEVIATION_THRESHOLD:
            logger.warning(
                f"{ticker}: {metric_name}跨源偏差过大 "
                f"({deviation*100:.1f}%): {value1:.2f} vs {value2:.2f}"
            )
            return False, deviation
        
        return True, deviation
    
    @staticmethod
    def should_reject_data(pe: float, peg: float, growth_rate: float, 
                          price: float, ticker: str = "") -> tuple[bool, str]:
        """
        综合判断是否应拒绝数据
        
        原则：宁可为空，不要使用错的数据
        
        Returns:
            (是否拒绝, 拒绝原因)
        """
        # 价格检查
        valid, msg = ValidationRules.validate_price(price, ticker)
        if not valid:
            return True, f"价格无效: {msg}"
        
        # PE检查
        valid, msg = ValidationRules.validate_pe(pe, ticker)
        if not valid:
            return True, f"PE无效: {msg}"
        
        # PEG检查
        valid, msg = ValidationRules.validate_peg(peg, ticker)
        if not valid:
            return True, f"PEG无效: {msg}"
        
        # 增长率检查
        valid, msg = ValidationRules.validate_growth_rate(growth_rate, ticker)
        if not valid:
            return True, f"增长率无效: {msg}"
        
        return False, ""

