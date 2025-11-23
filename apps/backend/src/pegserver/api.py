from __future__ import annotations

from flask import Blueprint, Response, current_app, jsonify, request

from .config import get_settings
from .proto_responses import build_ping_response, build_single_stock_response

api = Blueprint('api', __name__, url_prefix='/api')


@api.get('/ping/')
def ping_endpoint() -> Response:
    store = current_app.extensions['graph_store']
    store.record_tracking()
    agent = get_settings().agent_name
    payload = build_ping_response(agent)
    return Response(payload, mimetype='application/x-protobuf')


@api.get('/peg-stocks/')
def peg_stocks():
    store = current_app.extensions['graph_store']
    return jsonify(store.list_peg_candidates())


@api.get('/single-stock-page/')
def single_stock_page() -> Response:
    symbol = (request.args.get('symbol') or '').strip().upper()
    if not symbol:
        return jsonify({'detail': 'symbol query parameter is required'}), 400

    store = current_app.extensions['graph_store']
    payload = store.fetch_stock_payload(symbol)
    if not payload:
        return jsonify({'detail': f'Stock {symbol} not found'}), 404
    response = build_single_stock_response(payload)
    return Response(response, mimetype='application/x-protobuf')
