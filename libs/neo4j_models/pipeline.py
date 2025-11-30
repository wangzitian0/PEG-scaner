"""Pipeline node models for workflow management."""

from typing import Any, Dict

from neomodel import (
    ArrayProperty,
    BooleanProperty,
    DateTimeProperty,
    IntegerProperty,
    JSONProperty,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
)

from .base import TimestampedNode, prefixed_label


class CrawlerTask(TimestampedNode):
    """Crawler task definition."""
    
    __label__ = prefixed_label("CrawlerTask")
    
    name = StringProperty(required=True)
    source_type = StringProperty()  # yfinance, sec, news
    target_symbols = ArrayProperty(StringProperty())
    schedule_cron = StringProperty()
    
    # Status: pending, running, completed, failed
    status = StringProperty(default="pending")
    is_active = BooleanProperty(default=True)
    last_run_at = DateTimeProperty()
    last_error = StringProperty()
    metadata = JSONProperty(default=dict)
    
    # Relationships
    batches = RelationshipTo('DataBatch', 'PRODUCED')
    
    def __str__(self):
        return f"CrawlerTask({self.name})"
    
    def mark_running(self):
        from datetime import datetime
        self.status = "running"
        self.last_run_at = datetime.utcnow()
        self.save()
    
    def mark_completed(self):
        self.status = "completed"
        self.last_error = ""
        self.save()
    
    def mark_failed(self, error: str):
        self.status = "failed"
        self.last_error = error[:1000]
        self.save()


class DataBatch(TimestampedNode):
    """Data batch - core pipeline entity."""
    
    __label__ = prefixed_label("DataBatch")
    
    batch_id = StringProperty(unique_index=True, required=True)
    source = StringProperty(required=True)  # yfinance, sec
    data_type = StringProperty()  # quote, earnings, news, company
    
    # Status: raw → cleaning → clean → reviewing → approved → committed
    # rejected can go back to cleaning
    status = StringProperty(default="raw")
    
    # Data
    raw_data = JSONProperty()
    cleaned_data = JSONProperty()
    validation_errors = JSONProperty()
    
    # Stats
    record_count = IntegerProperty(default=0)
    error_count = IntegerProperty(default=0)
    
    # Review
    reviewer = StringProperty()
    reviewed_at = DateTimeProperty()
    review_note = StringProperty()
    
    # Relationships
    crawler_task = RelationshipFrom('CrawlerTask', 'PRODUCED')
    
    def __str__(self):
        return f"DataBatch({self.batch_id}:{self.status})"
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'batch_id': self.batch_id,
            'source': self.source,
            'data_type': self.data_type,
            'status': self.status,
            'record_count': self.record_count,
            'error_count': self.error_count,
            'reviewer': self.reviewer,
        })
        return data

