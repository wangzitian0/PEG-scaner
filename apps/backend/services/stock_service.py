"""
Stock Service - Business logic layer.

Sits between GraphQL resolvers and repository layer.
"""

from typing import Any, Dict, List, Optional

from neo4j_repo import StockRepository


class StockService:
    """
    Stock business logic service.
    
    Thin layer that delegates to repository, but can add:
    - Business validation
    - Data transformation
    - Caching
    - Cross-entity operations
    """
    
    def __init__(self, repo: StockRepository) -> None:
        self.repo = repo
    
    def get_single_stock_page(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch single stock page data.
        
        Returns payload with: symbol, name, sector, daily_kline, news, etc.
        """
        return self.repo.fetch_stock_payload(symbol)
    
    def list_peg_candidates(self) -> List[Dict[str, Any]]:
        """
        List PEG watchlist candidates.
        
        Returns list of: symbol, name, pe_ratio, earnings_growth, peg_ratio
        """
        return self.repo.list_peg_candidates()
    
    def upsert_stock(self, payload: Dict[str, Any]) -> None:
        """Upsert stock data."""
        self.repo.upsert_stock_payload(payload)

