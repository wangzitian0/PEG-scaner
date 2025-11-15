"""
股票数据Schema定义

遵循原则：宁可为空，不要使用错的数据
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class StockDataSchema(BaseModel):
    """
    股票数据Schema
    
    严格的数据验证，确保数据质量
    """
    
    # 基础信息
    ticker: str = Field(..., description="股票代码（标准化格式）")
    date: str = Field(..., description="数据日期 (YYYY-MM-DD)")
    
    # 价格数据
    price: float = Field(..., gt=0, description="当前价格（必须>0）")
    market_cap: Optional[float] = Field(None, gt=0, description="市值")
    
    # 财务数据
    ttm_profit: float = Field(..., description="TTM净利润")
    ttm_revenue: Optional[float] = Field(None, description="TTM收入")
    shares_outstanding: Optional[float] = Field(None, gt=0, description="流通股本")
    
    # 增长数据
    growth_rate: float = Field(..., description="YoY增长率")
    
    # 估值数据
    pe: float = Field(..., description="市盈率")
    peg: float = Field(..., description="PEG比率")
    
    # 元数据
    currency: Literal['USD', 'HKD', 'CNY'] = Field('USD', description="货币类型")
    data_source: str = Field(..., description="数据来源")
    confidence: Literal['HIGH', 'MEDIUM', 'LOW'] = Field('HIGH', description="数据置信度")
    error_message: Optional[str] = Field(None, description="错误信息")
    
    @field_validator('pe')
    @classmethod
    def validate_pe(cls, v: float) -> float:
        """验证PE合理性"""
        if v < 0:
            raise ValueError(f"PE不能为负: {v}")
        if v > 300:
            raise ValueError(f"PE异常过高 (>{v}), 可能数据错误")
        return v
    
    @field_validator('peg')
    @classmethod
    def validate_peg(cls, v: float) -> float:
        """验证PEG合理性"""
        if v < -5 or v > 10:
            raise ValueError(f"PEG异常 ({v}), 超出合理范围 [-5, 10]")
        return v
    
    @field_validator('growth_rate')
    @classmethod
    def validate_growth_rate(cls, v: float) -> float:
        """验证增长率合理性"""
        if v < -1.0:
            raise ValueError(f"增长率过低 ({v*100:.1f}%), 可能数据错误")
        if v > 5.0:
            raise ValueError(f"增长率过高 ({v*100:.1f}%), 可能数据错误")
        return v
    
    @field_validator('date')
    @classmethod
    def validate_date(cls, v: str) -> str:
        """验证日期格式"""
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"日期格式错误: {v}, 应为 YYYY-MM-DD")
        return v
    
    class Config:
        """Pydantic配置"""
        validate_assignment = True
        str_strip_whitespace = True


class ETFHoldingSchema(BaseModel):
    """ETF持仓Schema"""
    
    ticker: str = Field(..., description="股票代码")
    name: str = Field(..., description="公司名称")
    weight: float = Field(0.0, ge=0, le=100, description="权重百分比 [0-100]")
    shares: Optional[int] = Field(None, ge=0, description="持股数量")
    market_value: Optional[float] = Field(None, ge=0, description="持仓市值")
    
    class Config:
        validate_assignment = True


class BacktestResultSchema(BaseModel):
    """回测结果Schema"""
    
    ticker: str
    start_date: str
    end_date: str
    
    # 策略参数
    buy_threshold: float = Field(..., gt=0, description="买入阈值")
    sell_threshold: float = Field(..., gt=0, description="卖出阈值")
    
    # 绩效指标
    initial_value: float = Field(..., gt=0)
    final_value: float = Field(..., gt=0)
    total_return: float
    annual_return: float
    max_drawdown: float = Field(..., ge=0, le=1, description="最大回撤 [0-1]")
    sharpe_ratio: float
    
    # 交易统计
    num_trades: int = Field(..., ge=0)
    num_wins: int = Field(..., ge=0)
    win_rate: float = Field(..., ge=0, le=1, description="胜率 [0-1]")
    
    @field_validator('sell_threshold')
    @classmethod
    def validate_thresholds(cls, v: float, info) -> float:
        """验证买入卖出阈值关系"""
        if 'buy_threshold' in info.data:
            if v <= info.data['buy_threshold']:
                raise ValueError("卖出阈值必须大于买入阈值")
        return v
    
    class Config:
        validate_assignment = True

