"""EarningsReport and EpsFact node models."""

from typing import Any, Dict, Optional

from neomodel import (
    ArrayProperty,
    BooleanProperty,
    DateProperty,
    FloatProperty,
    IntegerProperty,
    JSONProperty,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
)

from .base import (
    NextPeriodRel,
    ProvenanceRel,
    ReportedRel,
    TimestampedNode,
    prefixed_label,
)


class EarningsReport(TimestampedNode):
    """Quarterly earnings report node."""
    
    __label__ = prefixed_label("EarningsReport")
    
    # Whitelist: required
    ticker = StringProperty(required=True, index=True)
    fiscal_period = StringProperty(required=True, index=True)
    
    # Whitelist: validated
    eps = FloatProperty()
    revenue = FloatProperty()
    pe_ratio = FloatProperty()
    
    # Pass-through fields
    fiscal_year = IntegerProperty()
    fiscal_quarter = IntegerProperty()
    report_date = DateProperty()
    filing_date = DateProperty()
    eps_estimated = FloatProperty()
    eps_surprise = FloatProperty()
    revenue_estimated = FloatProperty()
    net_income = FloatProperty()
    operating_cash_flow = FloatProperty()
    free_cash_flow = FloatProperty()
    total_assets = FloatProperty()
    total_liabilities = FloatProperty()
    total_equity = FloatProperty()
    pb_ratio = FloatProperty()
    ps_ratio = FloatProperty()
    roe = FloatProperty()
    current_ratio = FloatProperty()
    eps_growth = FloatProperty()
    revenue_growth = FloatProperty()
    embedding = ArrayProperty(FloatProperty())
    raw_data = JSONProperty(default=dict)
    
    # Relationships
    company = RelationshipFrom('company.Company', 'REPORTED', model=ReportedRel)
    next_report = RelationshipTo('EarningsReport', 'NEXT_PERIOD', model=NextPeriodRel)
    prev_report = RelationshipFrom('EarningsReport', 'NEXT_PERIOD', model=NextPeriodRel)
    provenance = RelationshipTo('source.DataSource', 'PROVENANCE_FROM', model=ProvenanceRel)
    
    def __str__(self):
        return f"EarningsReport({self.ticker}@{self.fiscal_period})"
    
    @property
    def peg_ratio(self) -> Optional[float]:
        if self.pe_ratio and self.eps_growth and self.eps_growth > 0:
            return self.pe_ratio / (self.eps_growth * 100)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'ticker': self.ticker,
            'fiscal_period': self.fiscal_period,
            'eps': self.eps,
            'revenue': self.revenue,
            'pe_ratio': self.pe_ratio,
        })
        return data


class EpsFact(TimestampedNode):
    """Standalone EPS fact node for fine-grained queries."""
    
    __label__ = prefixed_label("EpsFact")
    
    ticker = StringProperty(required=True, index=True)
    quarter = StringProperty(required=True, index=True)
    value = FloatProperty(required=True)
    confidence = FloatProperty(default=1.0)
    is_estimated = BooleanProperty(default=False)
    
    # Relationships
    company = RelationshipFrom('company.Company', 'HAS_EPS')
    provenance = RelationshipTo('source.DataSource', 'PROVENANCE_FROM', model=ProvenanceRel)
    
    def __str__(self):
        return f"EpsFact({self.ticker}@{self.quarter}: {self.value})"

