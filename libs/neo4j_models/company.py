"""Company and Sector node models."""

from typing import Any, Dict

from neomodel import (
    ArrayProperty,
    BooleanProperty,
    DateProperty,
    FloatProperty,
    JSONProperty,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
)

from .base import (
    CompetesWithRel,
    HasQuoteRel,
    HasSectorRel,
    MentionsRel,
    ProvenanceRel,
    ReportedRel,
    TimestampedNode,
    prefixed_label,
)


class Sector(TimestampedNode):
    """Industry sector node."""
    
    __label__ = prefixed_label("Sector")
    
    name = StringProperty(unique_index=True, required=True)
    code = StringProperty(index=True)
    description = StringProperty()
    
    # Relationships
    companies = RelationshipFrom('Company', 'HAS_SECTOR', model=HasSectorRel)
    
    def __str__(self):
        return f"Sector({self.name})"


class Company(TimestampedNode):
    """Core company entity node."""
    
    __label__ = prefixed_label("Company")
    
    # Whitelist: required
    ticker = StringProperty(unique_index=True, required=True)
    name = StringProperty(required=True)
    
    # Whitelist: validated
    exchange = StringProperty(default="NASDAQ", index=True)
    sector = StringProperty(index=True)
    industry = StringProperty(index=True)
    
    # Pass-through fields
    currency = StringProperty(default="USD")
    country = StringProperty(default="US")
    description = StringProperty()
    market_cap = FloatProperty()
    shares_outstanding = FloatProperty()
    is_active = BooleanProperty(default=True)
    delisted_at = DateProperty()
    embedding = ArrayProperty(FloatProperty())
    metadata = JSONProperty(default=dict)
    
    # Relationships
    quotes = RelationshipTo('quote.DailyQuote', 'HAS_QUOTE', model=HasQuoteRel)
    earnings = RelationshipTo('earnings.EarningsReport', 'REPORTED', model=ReportedRel)
    sectors = RelationshipTo('Sector', 'HAS_SECTOR', model=HasSectorRel)
    competitors = RelationshipTo('Company', 'COMPETES_WITH', model=CompetesWithRel)
    mentioned_in = RelationshipFrom('news.NewsArticle', 'MENTIONS', model=MentionsRel)
    provenance = RelationshipTo('source.DataSource', 'PROVENANCE_FROM', model=ProvenanceRel)
    
    def __str__(self):
        return f"Company({self.ticker})"
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'ticker': self.ticker,
            'name': self.name,
            'exchange': self.exchange,
            'sector': self.sector,
            'industry': self.industry,
            'market_cap': self.market_cap,
        })
        return data

