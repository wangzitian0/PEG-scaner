"""Base node classes and relationship definitions."""

from datetime import datetime
from typing import Any, Dict

from neomodel import (
    DateTimeProperty,
    FloatProperty,
    IntegerProperty,
    StringProperty,
    StructuredNode,
    StructuredRel,
    UniqueIdProperty,
)

# SSOT: Use settings from libs.config
from libs.config import settings


def prefixed_label(base: str) -> str:
    """Get prefixed label for Neo4j node."""
    return settings.prefixed_label(base)


# =============================================================================
# Relationship Models
# =============================================================================

class TimestampedRel(StructuredRel):
    """Base relationship with timestamp."""
    created_at = DateTimeProperty(default_now=True)
    confidence = FloatProperty(default=1.0)


class HasQuoteRel(TimestampedRel):
    """Company -[HAS_QUOTE]-> DailyQuote"""
    pass


class ReportedRel(TimestampedRel):
    """Company -[REPORTED]-> EarningsReport"""
    quarter = StringProperty()


class HasSectorRel(TimestampedRel):
    """Company -[HAS_SECTOR]-> Sector"""
    pass


class CompetesWithRel(TimestampedRel):
    """Company -[COMPETES_WITH]-> Company"""
    similarity_score = FloatProperty()


class MentionsRel(TimestampedRel):
    """NewsArticle -[MENTIONS]-> Company"""
    sentiment_score = FloatProperty()
    mention_count = IntegerProperty(default=1)


class ProvenanceRel(TimestampedRel):
    """* -[PROVENANCE_FROM]-> DataSource"""
    fetched_at = DateTimeProperty(default_now=True)


class NextPeriodRel(StructuredRel):
    """Temporal chain relationship."""
    period_type = StringProperty()
    created_at = DateTimeProperty(default_now=True)


# =============================================================================
# Base Node
# =============================================================================

class TimestampedNode(StructuredNode):
    """Abstract base node with auto-timestamps."""
    
    __abstract_node__ = True
    
    uid = UniqueIdProperty()
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary."""
        return {
            'uid': self.uid,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

