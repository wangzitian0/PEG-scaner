from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Optional

import logging

from neomodel import config as neo_config
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from .config import Settings
from .models import CrawlerJobNode, StockDocumentNode, TrackingRecordNode


class BaseGraphStore:
    def record_tracking(self) -> None:
        raise NotImplementedError

    def upsert_stock_payload(self, payload: Dict[str, Any]) -> None:
        raise NotImplementedError

    def fetch_stock_payload(self, symbol: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def list_peg_candidates(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def has_stocks(self) -> bool:
        raise NotImplementedError

    def list_jobs(self) -> List[CrawlerJobNode]:
        raise NotImplementedError

    def get_job(self, job_id: str) -> Optional[CrawlerJobNode]:
        raise NotImplementedError

    def ensure_job(self, *, symbol: str, name: str, metadata: Dict[str, Any]) -> CrawlerJobNode:
        raise NotImplementedError


class Neo4jGraphStore(BaseGraphStore):
    def __init__(self, settings: Settings) -> None:
        neo_config.DATABASE_URL = settings.neo4j_bolt_url
        self._settings = settings

    def record_tracking(self) -> None:
        TrackingRecordNode().save()

    def upsert_stock_payload(self, payload: Dict[str, Any]) -> None:
        symbol = payload.get('symbol')
        if not symbol:
            raise ValueError('payload must include symbol')
        doc = StockDocumentNode.nodes.get_or_none(symbol=symbol.upper())
        if not doc:
            doc = StockDocumentNode(symbol=symbol.upper())
        doc.apply_payload(payload)
        doc.save()

    def fetch_stock_payload(self, symbol: str) -> Optional[Dict[str, Any]]:
        doc = StockDocumentNode.nodes.get_or_none(symbol=symbol.upper())
        if not doc:
            return None
        return self._doc_to_payload(doc)

    def list_peg_candidates(self) -> List[Dict[str, Any]]:
        docs = StockDocumentNode.nodes.order_by('-updated_at')
        return [self._doc_to_candidate(doc) for doc in docs]

    def has_stocks(self) -> bool:
        return bool(StockDocumentNode.nodes.first())

    def list_jobs(self) -> List[CrawlerJobNode]:
        return list(CrawlerJobNode.nodes.order_by('-updated_at'))

    def get_job(self, job_id: str) -> Optional[CrawlerJobNode]:
        return CrawlerJobNode.nodes.get_or_none(uid=job_id)

    def ensure_job(self, *, symbol: str, name: str, metadata: Dict[str, Any]) -> CrawlerJobNode:
        existing = CrawlerJobNode.nodes.get_or_none(symbol=symbol.upper(), name=name)
        if existing:
            existing.metadata = metadata
            existing.save()
            return existing
        job = CrawlerJobNode(symbol=symbol.upper(), name=name)
        job.metadata = metadata
        job.save()
        return job

    @staticmethod
    def _doc_to_payload(doc: StockDocumentNode) -> Dict[str, Any]:
        return {
            'symbol': doc.symbol,
            'name': doc.name,
            'exchange': doc.exchange,
            'currency': doc.currency,
            'sector': doc.sector,
            'industry': doc.industry,
            'description': doc.description,
            'valuation': doc.valuation or {},
            'indicators': doc.indicators or {},
            'metrics': doc.metrics or {},
            'daily_kline': doc.daily_kline or [],
            'news': doc.news or [],
        }

    def _doc_to_candidate(self, doc: StockDocumentNode) -> Dict[str, Any]:
        metrics = doc.metrics or {}
        valuation = doc.valuation or {}
        return {
            'symbol': doc.symbol,
            'name': doc.name or doc.symbol,
            'pe_ratio': valuation.get('pe_ratio'),
            'earnings_growth': metrics.get('earnings_growth'),
            'peg_ratio': metrics.get('peg_ratio'),
        }


class FakeGraphStore(BaseGraphStore):
    def __init__(self) -> None:
        self._tracking: List[Dict[str, Any]] = []
        self._stocks: Dict[str, Dict[str, Any]] = {}
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def record_tracking(self) -> None:
        self._tracking.append({'created_at': time.time()})

    def upsert_stock_payload(self, payload: Dict[str, Any]) -> None:
        symbol = payload.get('symbol')
        if not symbol:
            raise ValueError('payload must include symbol')
        self._stocks[symbol.upper()] = payload.copy()

    def fetch_stock_payload(self, symbol: str) -> Optional[Dict[str, Any]]:
        return self._stocks.get(symbol.upper())

    def list_peg_candidates(self) -> List[Dict[str, Any]]:
        candidates = []
        for payload in self._stocks.values():
            valuation = payload.get('valuation') or {}
            metrics = payload.get('metrics') or {}
            candidates.append(
                {
                    'symbol': payload.get('symbol'),
                    'name': payload.get('name'),
                    'pe_ratio': valuation.get('pe_ratio'),
                    'earnings_growth': metrics.get('earnings_growth'),
                    'peg_ratio': metrics.get('peg_ratio'),
                }
            )
        return candidates

    def has_stocks(self) -> bool:
        return bool(self._stocks)

    def list_jobs(self) -> List[CrawlerJobNode]:
        return []

    def get_job(self, job_id: str) -> Optional[CrawlerJobNode]:  # pragma: no cover - fake mode skips admin
        return None

    def ensure_job(self, *, symbol: str, name: str, metadata: Dict[str, Any]) -> CrawlerJobNode:  # pragma: no cover
        raise RuntimeError('Crawler jobs unavailable in fake graph store')


class GraphStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._logger = logging.getLogger(__name__)
        self._impl: BaseGraphStore = self._init_store(settings)

    def _init_store(self, settings: Settings) -> BaseGraphStore:
        if settings.use_fake_graph:
            return FakeGraphStore()
        try:
            store = Neo4jGraphStore(settings)
            store.has_stocks()  # sanity check that the driver is reachable
            return store
        except (ServiceUnavailable, Neo4jError) as exc:
            self._logger.warning('Neo4j unavailable (%s); falling back to fake graph store', exc)
            return FakeGraphStore()

    def record_tracking(self) -> None:
        self._impl.record_tracking()

    def upsert_stock_payload(self, payload: Dict[str, Any]) -> None:
        self._impl.upsert_stock_payload(payload)

    def fetch_stock_payload(self, symbol: str) -> Optional[Dict[str, Any]]:
        return self._impl.fetch_stock_payload(symbol)

    def list_peg_candidates(self) -> List[Dict[str, Any]]:
        return self._impl.list_peg_candidates()

    def has_stocks(self) -> bool:
        return self._impl.has_stocks()

    def list_jobs(self) -> List[CrawlerJobNode]:
        return self._impl.list_jobs()

    def get_job(self, job_id: str) -> Optional[CrawlerJobNode]:
        return self._impl.get_job(job_id)

    def ensure_job(self, *, symbol: str, name: str, metadata: Dict[str, Any]) -> CrawlerJobNode:
        return self._impl.ensure_job(symbol=symbol, name=name, metadata=metadata)

    def seed_if_needed(self, payloads: Iterable[Dict[str, Any]]) -> None:
        if self.has_stocks():
            return
        for payload in payloads:
            self.upsert_stock_payload(payload)
