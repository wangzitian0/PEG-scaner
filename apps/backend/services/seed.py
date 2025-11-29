"""
Seed Data - Default payloads for development.

Provides sample stock data when database is empty.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


def build_sample_payload(symbol: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Build a sample stock payload for testing/seeding."""
    metadata = metadata or {}
    base_ts = int(time.time() * 1000) - 86400 * 30 * 1000  # 30 days ago
    
    return {
        "symbol": symbol.upper(),
        "name": metadata.get("name", symbol.upper()),
        "exchange": metadata.get("exchange", "NASDAQ"),
        "currency": metadata.get("currency", "USD"),
        "sector": metadata.get("sector", "Technology"),
        "industry": metadata.get("industry", "Software"),
        "description": metadata.get("description", f"Sample data for {symbol}"),
        "valuation": {
            "ps_ratio": 8.5,
            "pe_ratio": 25.0,
            "pb_ratio": 12.0,
        },
        "indicators": {
            "eps": 6.5,
            "fcf": 100000000,
            "current_ratio": 1.2,
            "roe": 0.35,
        },
        "metrics": {
            "peg_ratio": 1.5,
            "earnings_growth": 0.15,
        },
        "daily_kline": [
            {
                "timestamp": base_ts + i * 86400 * 1000,
                "open": 150 + i,
                "high": 155 + i,
                "low": 148 + i,
                "close": 152 + i,
                "volume": 1000000 + i * 10000,
            }
            for i in range(30)
        ],
        "news": [
            {
                "title": f"{symbol} announces Q4 earnings",
                "url": f"https://example.com/news/{symbol.lower()}-q4",
                "source": "Reuters",
                "published_at": time.time() * 1000 - 86400 * 1000,
            },
            {
                "title": f"{symbol} launches new product line",
                "url": f"https://example.com/news/{symbol.lower()}-launch",
                "source": "Bloomberg",
                "published_at": time.time() * 1000 - 86400 * 2 * 1000,
            },
        ],
    }


def get_seed_payloads() -> List[Dict[str, Any]]:
    """Get default seed payloads for development."""
    return [
        build_sample_payload("AAPL", metadata={"name": "Apple Inc."}),
        build_sample_payload("MSFT", metadata={"name": "Microsoft Corporation"}),
        build_sample_payload("NVDA", metadata={"name": "NVIDIA Corporation"}),
    ]

