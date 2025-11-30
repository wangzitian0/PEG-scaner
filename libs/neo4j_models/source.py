"""DataSource node model."""

from typing import Any, Dict

from neomodel import (
    BooleanProperty,
    FloatProperty,
    JSONProperty,
    StringProperty,
)

from .base import TimestampedNode, prefixed_label


class DataSource(TimestampedNode):
    """Provenance tracking node."""
    
    __label__ = prefixed_label("DataSource")
    
    name = StringProperty(unique_index=True, required=True)
    source_type = StringProperty()  # api, crawler, manual, llm
    base_url = StringProperty()
    description = StringProperty()
    is_active = BooleanProperty(default=True)
    reliability_score = FloatProperty(default=1.0)
    metadata = JSONProperty(default=dict)
    
    def __str__(self):
        return f"DataSource({self.name})"
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'name': self.name,
            'source_type': self.source_type,
            'base_url': self.base_url,
            'reliability_score': self.reliability_score,
        })
        return data

