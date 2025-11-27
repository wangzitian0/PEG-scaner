from __future__ import annotations

import time
import os
from pathlib import Path
from typing import Any, Dict, Optional

from ariadne import QueryType, graphql_sync, load_schema_from_path, make_executable_schema
from flask import Blueprint, current_app, jsonify, request

from .config import get_settings


def _find_schema_path() -> Path:
    # 1) Env override
    env_path = os.getenv('PEG_SCHEMA_PATH')
    if env_path:
        candidate = Path(env_path).expanduser().resolve()
        if candidate.exists():
            return candidate
    # 2) Walk up to find libs/schema/schema.graphql
    here = Path(__file__).resolve()
    for ancestor in [here, *here.parents]:
        candidate = ancestor / 'libs' / 'schema' / 'schema.graphql'
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Cannot locate GraphQL schema (tried PEG_SCHEMA_PATH and libs/schema/schema.graphql)")


_SCHEMA_PATH = _find_schema_path()

query = QueryType()


def _get_store():
    return current_app.extensions['graph_store']


@query.field('ping')
def resolve_ping(*_: Any) -> Dict[str, Any]:
    store = _get_store()
    store.record_tracking()
    agent = get_settings().agent_name
    return {
        'message': 'pong',
        'agent': agent,
        'timestampMs': float(int(time.time() * 1000)),
    }


@query.field('pegStocks')
def resolve_peg_stocks(*_: Any) -> list[Dict[str, Any]]:
    store = _get_store()
    candidates = store.list_peg_candidates()
    return [
        {
            'symbol': entry.get('symbol', ''),
            'name': entry.get('name') or entry.get('symbol', ''),
            'peRatio': entry.get('pe_ratio'),
            'earningsGrowth': entry.get('earnings_growth'),
            'pegRatio': entry.get('peg_ratio'),
        }
        for entry in candidates
    ]


@query.field('singleStock')
def resolve_single_stock(*_: Any, symbol: str) -> Optional[Dict[str, Any]]:
    store = _get_store()
    payload = store.fetch_stock_payload(symbol)
    if not payload:
        return None
    return _to_single_stock_page(payload)


def _to_single_stock_page(payload: Dict[str, Any]) -> Dict[str, Any]:
    stock = {
        'symbol': payload.get('symbol', ''),
        'name': payload.get('name', ''),
        'exchange': payload.get('exchange', ''),
        'currency': payload.get('currency', ''),
        'companyInfo': _to_company_info(payload),
    }
    daily_kline = [
        {
            'timestamp': float(row.get('timestamp', 0)),
            'open': _maybe_float(row.get('open')),
            'high': _maybe_float(row.get('high')),
            'low': _maybe_float(row.get('low')),
            'close': _maybe_float(row.get('close')),
            'volume': _maybe_float(row.get('volume')),
        }
        for row in payload.get('daily_kline') or []
    ]
    news = [
        {
            'title': item.get('title', ''),
            'url': item.get('url'),
            'source': item.get('source'),
            'publishedAt': _maybe_float(item.get('published_at')),
        }
        for item in payload.get('news') or []
    ]
    return {'stock': stock, 'dailyKline': daily_kline, 'news': news}


def _to_company_info(payload: Dict[str, Any]) -> Dict[str, Any]:
    valuation = payload.get('valuation') or {}
    indicators = payload.get('indicators') or {}
    return {
        'symbol': payload.get('symbol', ''),
        'description': payload.get('description') or '',
        'sector': payload.get('sector') or '',
        'industry': payload.get('industry') or '',
        'valuation': {
            'psRatio': _maybe_float(valuation.get('ps_ratio')),
            'peRatio': _maybe_float(valuation.get('pe_ratio')),
            'pbRatio': _maybe_float(valuation.get('pb_ratio')),
        }
        if valuation
        else None,
        'indicators': {
            'eps': _maybe_float(indicators.get('eps')),
            'fcf': _maybe_float(indicators.get('fcf')),
            'currentRatio': _maybe_float(indicators.get('current_ratio')),
            'roe': _maybe_float(indicators.get('roe')),
        }
        if indicators
        else None,
    }


def _maybe_float(value: Any) -> Optional[float]:
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


type_defs = load_schema_from_path(_SCHEMA_PATH)
schema = make_executable_schema(type_defs, query)

graphql_api = Blueprint('graphql', __name__)


@graphql_api.route('/graphql', methods=['GET', 'POST'])
def graphql_server():
    settings = get_settings()
    if request.method == 'GET':
        return jsonify({'detail': 'GraphQL endpoint. POST a {query, variables} JSON payload.'})
    data = request.get_json(force=True, silent=True) or {}
    success, result = graphql_sync(
        schema,
        data,
        context_value={'request': request, 'settings': settings, 'store': _get_store()},
        debug=settings.debug,
    )
    status_code = 200 if success and 'errors' not in result else 400
    return jsonify(result), status_code
