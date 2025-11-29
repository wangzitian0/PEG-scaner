"""
Stock Repository - Data access layer for stock entities.

Abstracts Neo4j/neomodel operations behind a clean interface.
Supports both real Neo4j and fake in-memory store for testing.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Optional

from neo4j.exceptions import Neo4jError, ServiceUnavailable

from ..connection import get_settings
from ..models.stock import CrawlerJobNode, StockDocumentNode, TrackingRecordNode


class BaseRepository:
    """Abstract base for repository implementations."""

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


class Neo4jStockRepository(BaseRepository):
    """Real Neo4j implementation using neomodel."""

    def record_tracking(self) -> None:
        TrackingRecordNode().save()

    def upsert_stock_payload(self, payload: Dict[str, Any]) -> None:
        symbol = payload.get("symbol")
        if not symbol:
            raise ValueError("payload must include symbol")
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
        docs = StockDocumentNode.nodes.order_by("-updated_at")
        return [self._doc_to_candidate(doc) for doc in docs]

    def has_stocks(self) -> bool:
        try:
            return bool(StockDocumentNode.nodes.first())
        except StockDocumentNode.DoesNotExist:
            return False

    @staticmethod
    def _doc_to_payload(doc: StockDocumentNode) -> Dict[str, Any]:
        return {
            "symbol": doc.symbol,
            "name": doc.name,
            "exchange": doc.exchange,
            "currency": doc.currency,
            "sector": doc.sector,
            "industry": doc.industry,
            "description": doc.description,
            "valuation": doc.valuation or {},
            "indicators": doc.indicators or {},
            "metrics": doc.metrics or {},
            "daily_kline": doc.daily_kline or [],
            "news": doc.news or [],
        }

    def _doc_to_candidate(self, doc: StockDocumentNode) -> Dict[str, Any]:
        metrics = doc.metrics or {}
        valuation = doc.valuation or {}
        return {
            "symbol": doc.symbol,
            "name": doc.name or doc.symbol,
            "pe_ratio": valuation.get("pe_ratio"),
            "earnings_growth": metrics.get("earnings_growth"),
            "peg_ratio": metrics.get("peg_ratio"),
        }


class FakeStockRepository(BaseRepository):
    """In-memory fake for testing without Neo4j."""

    def __init__(self) -> None:
        self._tracking: List[Dict[str, Any]] = []
        self._stocks: Dict[str, Dict[str, Any]] = {}

    def record_tracking(self) -> None:
        self._tracking.append({"created_at": time.time()})

    def upsert_stock_payload(self, payload: Dict[str, Any]) -> None:
        symbol = payload.get("symbol")
        if not symbol:
            raise ValueError("payload must include symbol")
        self._stocks[symbol.upper()] = payload.copy()

    def fetch_stock_payload(self, symbol: str) -> Optional[Dict[str, Any]]:
        return self._stocks.get(symbol.upper())

    def list_peg_candidates(self) -> List[Dict[str, Any]]:
        candidates = []
        for payload in self._stocks.values():
            valuation = payload.get("valuation") or {}
            metrics = payload.get("metrics") or {}
            candidates.append(
                {
                    "symbol": payload.get("symbol"),
                    "name": payload.get("name"),
                    "pe_ratio": valuation.get("pe_ratio"),
                    "earnings_growth": metrics.get("earnings_growth"),
                    "peg_ratio": metrics.get("peg_ratio"),
                }
            )
        return candidates

    def has_stocks(self) -> bool:
        return bool(self._stocks)


class StockRepository:
    """
    Stock Repository facade - auto-selects real/fake implementation.
    
    Usage:
        repo = StockRepository()
        repo.upsert_stock_payload({"symbol": "AAPL", ...})
        payload = repo.fetch_stock_payload("AAPL")
    """

    def __init__(self) -> None:
        settings = get_settings()
        if settings.use_fake_graph:
            self._impl: BaseRepository = FakeStockRepository()
        else:
            from ..connection import get_driver
            get_driver()  # Initialize neomodel connection
            self._impl = Neo4jStockRepository()
            self._wait_for_database(settings)

    def _wait_for_database(self, settings, retries: int = 10, delay_seconds: float = 2.0) -> None:
        for attempt in range(retries):
            try:
                self._impl.has_stocks()
                return
            except (Neo4jError, ServiceUnavailable):
                if attempt == retries - 1:
                    print(f"\n[!] Critical Error: Failed to connect to Neo4j at {settings.neo4j_bolt_url}")
                    print("    Please ensure the Neo4j container is running.")
                    raise
                time.sleep(delay_seconds)

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

    def seed_if_needed(self, payloads: Iterable[Dict[str, Any]]) -> None:
        if self.has_stocks():
            return
        for payload in payloads:
            self.upsert_stock_payload(payload)

