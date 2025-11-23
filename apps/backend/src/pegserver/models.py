from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from neomodel import (
    BooleanProperty,
    DateTimeProperty,
    JSONProperty,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
)

from .config import get_settings

_SETTINGS = get_settings()


def _label(base: str) -> str:
    return _SETTINGS.prefixed_label(base)


class _TimestampedNode(StructuredNode):
    __abstract_node__ = True

    uid = UniqueIdProperty()
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)

    def save(self, *args, **kwargs):  # pragma: no cover - exercised indirectly
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


class StockDocumentNode(_TimestampedNode):
    __label__ = _label('StockDocument')

    symbol = StringProperty(unique_index=True, required=True)
    name = StringProperty()
    exchange = StringProperty(default='NASDAQ')
    currency = StringProperty(default='USD')
    sector = StringProperty()
    industry = StringProperty()
    description = StringProperty()
    valuation = JSONProperty(default=dict)
    indicators = JSONProperty(default=dict)
    metrics = JSONProperty(default=dict)
    daily_kline = JSONProperty(default=list)
    news = JSONProperty(default=list)

    def apply_payload(self, payload: Dict[str, Any]) -> None:
        self.symbol = payload.get('symbol', self.symbol)
        self.name = payload.get('name') or self.name or self.symbol
        self.exchange = payload.get('exchange') or self.exchange or 'NASDAQ'
        self.currency = payload.get('currency') or self.currency or 'USD'
        self.sector = payload.get('sector') or self.sector
        self.industry = payload.get('industry') or self.industry
        self.description = payload.get('description') or self.description
        self.valuation = payload.get('valuation') or self.valuation or {}
        self.indicators = payload.get('indicators') or self.indicators or {}
        self.metrics = payload.get('metrics') or self.metrics or {}
        self.daily_kline = payload.get('daily_kline') or []
        self.news = payload.get('news') or []


class CrawlerJobNode(_TimestampedNode):
    __label__ = _label('CrawlerJob')

    STATUS_PENDING = 'pending'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    name = StringProperty(required=True)
    symbol = StringProperty(required=True, index=True)
    target_url = StringProperty()
    schedule_cron = StringProperty()
    status = StringProperty(default=STATUS_PENDING)
    is_active = BooleanProperty(default=True)
    last_error = StringProperty()
    metadata = JSONProperty(default=dict)

    def mark_running(self) -> None:
        self.status = self.STATUS_RUNNING
        self.save()

    def mark_completed(self) -> None:
        self.status = self.STATUS_COMPLETED
        self.last_error = ''
        self.save()

    def mark_failed(self, error_message: str) -> None:
        self.status = self.STATUS_FAILED
        self.last_error = error_message[:1000]
        self.save()


class TrackingRecordNode(StructuredNode):
    __label__ = _label('TrackingRecord')

    uid = UniqueIdProperty()
    created_at = DateTimeProperty(default_now=True)


__all__ = ['StockDocumentNode', 'CrawlerJobNode', 'TrackingRecordNode']
