from __future__ import annotations

import logging
import random
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def fetch_yfinance_payload(symbol: str) -> Optional[Dict[str, Any]]:
    try:
        import yfinance as yf
    except ImportError:  # pragma: no cover - yfinance is optional in CI
        logger.warning('yfinance not installed; falling back to sample payloads')
        return None

    ticker = yf.Ticker(symbol)
    try:
        info = ticker.get_info()
    except Exception as exc:  # pragma: no cover - network call
        logger.error('yfinance get_info failed for %s: %s', symbol, exc)
        return None

    base_payload = _base_payload(symbol, info)
    base_payload['daily_kline'] = _history_to_payload(_safe_history(ticker))
    base_payload['news'] = _yfinance_news_to_payload(getattr(ticker, 'news', []))
    _apply_financials_from_info(base_payload, info)
    return base_payload


def build_sample_payload(symbol: str, *, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    metadata = metadata or {}
    random.seed(symbol)
    base_price = 80 + random.random() * 30
    kline = _generate_kline_series(base_price, count=15)
    news = _generate_sample_news(symbol, metadata)

    valuation = {
        'ps_ratio': round(random.uniform(3, 12), 2),
        'pe_ratio': round(random.uniform(15, 40), 2),
        'pb_ratio': round(random.uniform(5, 25), 2),
    }
    indicators = {
        'eps': round(random.uniform(2, 10), 2),
        'fcf': round(random.uniform(1, 20), 2),
        'current_ratio': round(random.uniform(0.8, 3), 2),
        'roe': round(random.uniform(0.1, 0.4), 2),
    }
    earnings_growth = round(random.uniform(0.05, 0.4), 2)
    metrics = {
        'earnings_growth': earnings_growth,
        'peg_ratio': _compute_peg(valuation['pe_ratio'], earnings_growth),
    }

    return {
        'symbol': symbol.upper(),
        'name': metadata.get('name') or f'{symbol.upper()} Corp',
        'exchange': metadata.get('exchange') or 'NASDAQ',
        'currency': metadata.get('currency') or 'USD',
        'sector': metadata.get('sector') or 'Technology',
        'industry': metadata.get('industry') or 'AI Infrastructure',
        'description': metadata.get('description') or f'Sample payload for {symbol.upper()}',
        'daily_kline': kline,
        'news': news,
        'valuation': valuation,
        'indicators': indicators,
        'metrics': metrics,
    }


def _base_payload(symbol: str, info: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'symbol': symbol.upper(),
        'name': info.get('longName') or info.get('shortName') or symbol.upper(),
        'exchange': info.get('exchange') or 'NASDAQ',
        'currency': info.get('currency') or 'USD',
        'sector': info.get('sector') or '',
        'industry': info.get('industry') or '',
        'description': info.get('longBusinessSummary') or '',
    }


def _safe_history(ticker):
    try:
        return ticker.history(period='1mo', interval='1d')
    except Exception as exc:  # pragma: no cover
        logger.error('yfinance history failed for %s: %s', ticker.ticker, exc)
        return None


def _apply_financials_from_info(payload: Dict[str, Any], info: Dict[str, Any]) -> None:
    valuation = {
        'ps_ratio': _safe_float(info.get('priceToSalesTrailing12Months')),
        'pe_ratio': _safe_float(info.get('trailingPE') or info.get('forwardPE')),
        'pb_ratio': _safe_float(info.get('priceToBook')),
    }
    indicators = {
        'eps': _safe_float(info.get('trailingEps')),
        'fcf': _safe_float(info.get('freeCashflow'), scale=1e-6),
        'current_ratio': _safe_float(info.get('currentRatio')),
        'roe': _safe_float(info.get('returnOnEquity')),
    }
    earnings_growth = _safe_float(info.get('earningsQuarterlyGrowth')) or 0.1
    metrics = {
        'earnings_growth': earnings_growth,
        'peg_ratio': _compute_peg(valuation['pe_ratio'], earnings_growth),
    }
    payload['valuation'] = valuation
    payload['indicators'] = indicators
    payload['metrics'] = metrics


def _history_to_payload(history_df) -> List[Dict[str, Any]]:
    if history_df is None or getattr(history_df, 'empty', True):
        return []
    points: List[Dict[str, Any]] = []
    tail = history_df.tail(30)
    for index, row in tail.iterrows():
        timestamp = int(index.timestamp()) if hasattr(index, 'timestamp') else int(time.time())
        points.append(
            {
                'timestamp': timestamp,
                'open': float(row.get('Open', 0)),
                'high': float(row.get('High', 0)),
                'low': float(row.get('Low', 0)),
                'close': float(row.get('Close', 0)),
                'volume': int(row.get('Volume', 0)),
            }
        )
    return points


def _yfinance_news_to_payload(news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    payload: List[Dict[str, Any]] = []
    for idx, item in enumerate(news_items or []):
        payload.append(
            {
                'id': item.get('uuid') or f'news-{idx}',
                'title': item.get('title', ''),
                'url': item.get('link') or item.get('url', ''),
                'source': item.get('publisher', ''),
                'published_at': int(item.get('providerPublishTime') or item.get('published_at') or 0),
            }
        )
    return payload


def _generate_kline_series(base_price: float, count: int) -> List[Dict[str, Any]]:
    points = []
    ts = int(time.time()) - count * 86400
    price = base_price
    for _ in range(count):
        delta = random.uniform(-2, 2)
        open_price = max(price + random.uniform(-1, 1), 1)
        close_price = max(open_price + delta, 0.1)
        high = max(open_price, close_price) + random.random()
        low = min(open_price, close_price) - random.random()
        points.append(
            {
                'timestamp': ts,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close_price, 2),
                'volume': random.randint(500_000, 2_000_000),
            }
        )
        ts += 86400
        price = close_price
    return points


def _generate_sample_news(symbol: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    source = metadata.get('source') or 'M7 Research'
    return [
        {
            'id': f'{symbol.upper()}-news-{idx}',
            'title': f'{symbol.upper()} Update #{idx + 1}',
            'url': metadata.get('news_url') or f'https://news.example.com/{symbol}/{idx}',
            'source': source,
            'published_at': int(time.time()) - idx * 7200,
        }
        for idx in range(3)
    ]


def _safe_float(value, *, scale: float = 1.0) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value) / scale
    except (TypeError, ValueError):
        return None


def _compute_peg(pe_ratio: Optional[float], earnings_growth: Optional[float]) -> Optional[float]:
    if not pe_ratio or not earnings_growth:
        return None
    growth_percent = earnings_growth * 100
    if not growth_percent:
        return None
    return round(pe_ratio / growth_percent, 3)
