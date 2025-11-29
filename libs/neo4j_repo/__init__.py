"""
Neo4j Repository Layer - 共享数据访问层

Provides:
- Connection management (get_driver, lifespan)
- Repository classes (StockRepository)
- Model definitions (neomodel nodes)

Usage:
    from neo4j_repo import StockRepository, get_settings
    
    repo = StockRepository()
    payload = repo.fetch_stock_payload("AAPL")
"""

from .connection import get_driver, get_settings, lifespan
from .repositories.stock_repository import StockRepository

__all__ = ["get_driver", "get_settings", "lifespan", "StockRepository"]

