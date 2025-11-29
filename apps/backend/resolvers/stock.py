"""
Stock Resolvers - Market domain queries.

Corresponds to: libs/schema/market/market.graphql
"""

from typing import Optional

import strawberry
from strawberry.types import Info


@strawberry.type
class PegStock:
    """PEG watchlist candidate entry."""
    symbol: str
    name: str
    pe_ratio: Optional[float] = strawberry.field(name="peRatio", default=None)
    earnings_growth: Optional[float] = strawberry.field(name="earningsGrowth", default=None)
    peg_ratio: Optional[float] = strawberry.field(name="pegRatio", default=None)


@strawberry.type
class CompanyValuation:
    """Company valuation metrics."""
    ps_ratio: Optional[float] = strawberry.field(name="psRatio", default=None)
    pe_ratio: Optional[float] = strawberry.field(name="peRatio", default=None)
    pb_ratio: Optional[float] = strawberry.field(name="pbRatio", default=None)


@strawberry.type
class FinancialIndicators:
    """Financial performance indicators."""
    eps: Optional[float] = None
    fcf: Optional[float] = None
    current_ratio: Optional[float] = strawberry.field(name="currentRatio", default=None)
    roe: Optional[float] = None


@strawberry.type
class CompanyInfo:
    """Detailed company information."""
    symbol: str
    description: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    valuation: Optional[CompanyValuation] = None
    indicators: Optional[FinancialIndicators] = None


@strawberry.type
class Stock:
    """Stock entity with metadata."""
    symbol: str
    name: str
    exchange: Optional[str] = None
    currency: Optional[str] = None
    company_info: Optional[CompanyInfo] = strawberry.field(name="companyInfo", default=None)


@strawberry.type
class KLinePoint:
    """K-line (OHLCV) data point."""
    timestamp: float
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None


@strawberry.type
class NewsItem:
    """News article item."""
    title: str
    url: Optional[str] = None
    source: Optional[str] = None
    published_at: Optional[float] = strawberry.field(name="publishedAt", default=None)


@strawberry.type
class SingleStockPage:
    """Single stock page aggregated data."""
    stock: Stock
    daily_kline: list[KLinePoint] = strawberry.field(name="dailyKline")
    news: list[NewsItem]


@strawberry.type
class StockQuery:
    """Stock domain queries."""
    
    @strawberry.field
    def peg_stocks(self, info: Info) -> list[PegStock]:
        """List PEG watchlist candidates."""
        service = info.context["stock_service"]
        candidates = service.list_peg_candidates()
        return [
            PegStock(
                symbol=entry.get("symbol", ""),
                name=entry.get("name") or entry.get("symbol", ""),
                pe_ratio=entry.get("pe_ratio"),
                earnings_growth=entry.get("earnings_growth"),
                peg_ratio=entry.get("peg_ratio"),
            )
            for entry in candidates
        ]
    
    @strawberry.field
    def single_stock(self, info: Info, symbol: str) -> Optional[SingleStockPage]:
        """Fetch single stock page data by symbol."""
        service = info.context["stock_service"]
        payload = service.get_single_stock_page(symbol)
        if not payload:
            return None
        return _to_single_stock_page(payload)


def _maybe_float(value) -> Optional[float]:
    """Convert value to float, handling None and errors."""
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def _to_single_stock_page(payload: dict) -> SingleStockPage:
    """Convert raw payload to SingleStockPage type."""
    company_info = _to_company_info(payload)
    
    stock = Stock(
        symbol=payload.get("symbol", ""),
        name=payload.get("name", ""),
        exchange=payload.get("exchange", ""),
        currency=payload.get("currency", ""),
        company_info=company_info,
    )
    
    daily_kline = [
        KLinePoint(
            timestamp=float(row.get("timestamp", 0)),
            open=_maybe_float(row.get("open")),
            high=_maybe_float(row.get("high")),
            low=_maybe_float(row.get("low")),
            close=_maybe_float(row.get("close")),
            volume=_maybe_float(row.get("volume")),
        )
        for row in payload.get("daily_kline") or []
    ]
    
    news = [
        NewsItem(
            title=item.get("title", ""),
            url=item.get("url"),
            source=item.get("source"),
            published_at=_maybe_float(item.get("published_at")),
        )
        for item in payload.get("news") or []
    ]
    
    return SingleStockPage(stock=stock, daily_kline=daily_kline, news=news)


def _to_company_info(payload: dict) -> CompanyInfo:
    """Convert payload to CompanyInfo type."""
    valuation_data = payload.get("valuation") or {}
    indicators_data = payload.get("indicators") or {}
    
    valuation = None
    if valuation_data:
        valuation = CompanyValuation(
            ps_ratio=_maybe_float(valuation_data.get("ps_ratio")),
            pe_ratio=_maybe_float(valuation_data.get("pe_ratio")),
            pb_ratio=_maybe_float(valuation_data.get("pb_ratio")),
        )
    
    indicators = None
    if indicators_data:
        indicators = FinancialIndicators(
            eps=_maybe_float(indicators_data.get("eps")),
            fcf=_maybe_float(indicators_data.get("fcf")),
            current_ratio=_maybe_float(indicators_data.get("current_ratio")),
            roe=_maybe_float(indicators_data.get("roe")),
        )
    
    return CompanyInfo(
        symbol=payload.get("symbol", ""),
        description=payload.get("description") or "",
        sector=payload.get("sector") or "",
        industry=payload.get("industry") or "",
        valuation=valuation,
        indicators=indicators,
    )

