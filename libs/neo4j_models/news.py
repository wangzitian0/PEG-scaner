"""NewsArticle node model."""

from typing import Any, Dict

from neomodel import (
    ArrayProperty,
    BooleanProperty,
    DateTimeProperty,
    FloatProperty,
    IntegerProperty,
    RelationshipTo,
    StringProperty,
)

from .base import (
    MentionsRel,
    ProvenanceRel,
    TimestampedNode,
    prefixed_label,
)


class NewsArticle(TimestampedNode):
    """News article node for RAG and sentiment analysis."""
    
    __label__ = prefixed_label("NewsArticle")
    
    # Whitelist: required
    article_id = StringProperty(unique_index=True, required=True)
    title = StringProperty(required=True)
    
    # Whitelist: validated
    published_at = DateTimeProperty(index=True)
    source_name = StringProperty(index=True)
    
    # Pass-through fields
    url = StringProperty(index=True)
    summary = StringProperty()
    content = StringProperty()
    chunk_index = IntegerProperty(default=0)
    author = StringProperty()
    category = StringProperty()
    tags = ArrayProperty(StringProperty())
    sentiment_score = FloatProperty()
    sentiment_label = StringProperty()
    embedding = ArrayProperty(FloatProperty())
    is_processed = BooleanProperty(default=False)
    
    # Relationships
    mentions = RelationshipTo('company.Company', 'MENTIONS', model=MentionsRel)
    provenance = RelationshipTo('source.DataSource', 'PROVENANCE_FROM', model=ProvenanceRel)
    
    def __str__(self):
        return f"NewsArticle({self.title[:30]}...)"
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'article_id': self.article_id,
            'title': self.title,
            'source_name': self.source_name,
            'published_at': self.published_at.isoformat() if self.published_at else None,
        })
        return data

