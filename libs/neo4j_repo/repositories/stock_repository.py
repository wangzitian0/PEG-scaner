"""
Stock Repository - Data access layer for stock entities.

Abstracts Neo4j/neomodel operations behind a clean interface.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Optional

from neo4j.exceptions import Neo4jError, ServiceUnavailable

from ..connection import get_driver, get_settings
from ..models.stock import CrawlerJobNode, StockDocumentNode, TrackingRecordNode


class StockRepository:
    """
    Stock Repository - Neo4j implementation using neomodel.
    
    Usage:
        repo = StockRepository()
        repo.upsert_stock_payload({"symbol": "AAPL", ...})
        payload = repo.fetch_stock_payload("AAPL")
    """

    def __init__(self) -> None:
        get_driver()  # Initialize neomodel connection
        settings = get_settings()
        self._wait_for_database(settings)

    def _wait_for_database(self, settings, retries: int = 10, delay_seconds: float = 2.0) -> None:
        for attempt in range(retries):
            try:
                self.has_stocks()
                return
            except (Neo4jError, ServiceUnavailable):
                if attempt == retries - 1:
                    print(f"\n[!] Critical Error: Failed to connect to Neo4j at {settings.neo4j_bolt_url}")
                    print("    Please ensure the Neo4j container is running.")
                    raise
                time.sleep(delay_seconds)

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

    def seed_if_needed(self, payloads: Iterable[Dict[str, Any]]) -> None:
        if self.has_stocks():
            return
        for payload in payloads:
            self.upsert_stock_payload(payload)
