"""DailyQuote node model."""

from typing import Any, Dict

from neomodel import (
    ArrayProperty,
    DateProperty,
    FloatProperty,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
)

from .base import (
    HasQuoteRel,
    NextPeriodRel,
    ProvenanceRel,
    TimestampedNode,
    prefixed_label,
)


class DailyQuote(TimestampedNode):
    """Daily OHLCV price data node."""
    
    __label__ = prefixed_label("DailyQuote")
    
    # Whitelist: required
    ticker = StringProperty(required=True, index=True)
    date = DateProperty(required=True, index=True)
    close = FloatProperty(required=True)
    
    # Whitelist: validated
    open = FloatProperty()
    high = FloatProperty()
    low = FloatProperty()
    volume = FloatProperty()
    
    # Pass-through fields
    adj_close = FloatProperty()
    sma_20 = FloatProperty()
    sma_50 = FloatProperty()
    sma_200 = FloatProperty()
    rsi_14 = FloatProperty()
    embedding = ArrayProperty(FloatProperty())
    
    # Relationships
    company = RelationshipFrom('company.Company', 'HAS_QUOTE', model=HasQuoteRel)
    next_quote = RelationshipTo('DailyQuote', 'NEXT_PERIOD', model=NextPeriodRel)
    prev_quote = RelationshipFrom('DailyQuote', 'NEXT_PERIOD', model=NextPeriodRel)
    provenance = RelationshipTo('source.DataSource', 'PROVENANCE_FROM', model=ProvenanceRel)
    
    def __str__(self):
        return f"DailyQuote({self.ticker}@{self.date})"
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'ticker': self.ticker,
            'date': self.date.isoformat() if self.date else None,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
        })
        return data

