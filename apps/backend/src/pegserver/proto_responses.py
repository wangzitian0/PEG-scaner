from __future__ import annotations

import time
from typing import Any, Dict

from apps.backend.proto.generated import ping_pb2, single_stock_page_pb2, stock_pb2


def build_ping_response(agent: str) -> bytes:
    payload = ping_pb2.PingResponse(
        message='pong',
        agent=agent,
        timestamp_ms=int(time.time() * 1000),
    )
    return payload.SerializeToString()


def build_single_stock_response(payload: Dict[str, Any]) -> bytes:
    response = single_stock_page_pb2.SingleStockPageResponse()
    stock_message = response.stock
    stock_message.symbol = payload.get('symbol', '')
    stock_message.name = payload.get('name', '')
    stock_message.exchange = payload.get('exchange', '')
    stock_message.currency = payload.get('currency', '')

    company_info = payload.get('company_info')
    if company_info is None:
        company_info = {
            'symbol': payload.get('symbol', ''),
            'description': payload.get('description', ''),
            'sector': payload.get('sector', ''),
            'industry': payload.get('industry', ''),
            'valuation': payload.get('valuation'),
            'indicators': payload.get('indicators'),
        }
    _apply_company_info(stock_message, company_info)

    for row in payload.get('daily_kline') or []:
        kline = response.daily_kline.add()
        kline.timestamp = int(row.get('timestamp', 0))
        kline.open = float(row.get('open', 0.0))
        kline.high = float(row.get('high', 0.0))
        kline.low = float(row.get('low', 0.0))
        kline.close = float(row.get('close', 0.0))
        kline.volume = int(row.get('volume', 0))

    for item in payload.get('news') or []:
        news = response.news.add()
        news.title = item.get('title', '')
        news.url = item.get('url', '')
        news.source = item.get('source', '')
        news.published_at = int(item.get('published_at', 0))

    return response.SerializeToString()


def _apply_company_info(stock_message: stock_pb2.Stock, company_info: Dict[str, Any]) -> None:
    if not company_info:
        return
    stock_message.company_info.symbol = company_info.get('symbol') or stock_message.symbol
    stock_message.company_info.description = company_info.get('description', '')
    stock_message.company_info.sector = company_info.get('sector', '')
    stock_message.company_info.industry = company_info.get('industry', '')

    valuation = company_info.get('valuation') or {}
    if valuation:
        stock_message.company_info.valuation.ps_ratio = float(valuation.get('ps_ratio') or 0.0)
        stock_message.company_info.valuation.pe_ratio = float(valuation.get('pe_ratio') or 0.0)
        stock_message.company_info.valuation.pb_ratio = float(valuation.get('pb_ratio') or 0.0)

    indicators = company_info.get('indicators') or {}
    if indicators:
        stock_message.company_info.indicators.eps = float(indicators.get('eps') or 0.0)
        stock_message.company_info.indicators.fcf = float(indicators.get('fcf') or 0.0)
        stock_message.company_info.indicators.current_ratio = float(indicators.get('current_ratio') or 0.0)
        stock_message.company_info.indicators.roe = float(indicators.get('roe') or 0.0)
