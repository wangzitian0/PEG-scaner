from __future__ import annotations

import os
from pathlib import Path

import click
from flask import Flask
from flask_cors import CORS

from .admin import register_admin
from .api import api
from .config import get_settings
from .crawler import build_sample_payload, fetch_yfinance_payload
from .graph_store import GraphStore

_TEMPLATE_FOLDER = Path(__file__).parent / 'templates'


def create_app() -> Flask:
    settings = get_settings()
    app = Flask(__name__, template_folder=str(_TEMPLATE_FOLDER))
    app.config.update(
        SECRET_KEY=os.getenv('FLASK_SECRET_KEY', 'pegscanner-secret'),
        JSON_SORT_KEYS=False,
    )

    CORS(app, resources=settings.cors_resources())

    store = GraphStore(settings)
    app.extensions['graph_store'] = store
    _seed_default_payloads(store)

    app.register_blueprint(api)

    if not settings.use_fake_graph:
        register_admin(app, store)

    _register_cli(app, store)
    return app


def _seed_default_payloads(store: GraphStore) -> None:
    seeds = [
        build_sample_payload('AAPL', metadata={'name': 'Apple Inc.'}),
        build_sample_payload('MSFT', metadata={'name': 'Microsoft'}),
        build_sample_payload('NVDA', metadata={'name': 'NVIDIA'}),
    ]
    store.seed_if_needed(seeds)


def _register_cli(app: Flask, store: GraphStore) -> None:
    @app.cli.command('crawler-run')
    @click.option('--symbol', required=True, help='Ticker symbol to crawl (e.g. AAPL)')
    @click.option('--live/--sample', default=False, help='Fetch live data from yfinance or use synthetic payloads')
    def crawler_run(symbol: str, live: bool):
        """Runs a single crawler job and persists the stock payload."""
        payload = fetch_yfinance_payload(symbol) if live else None
        payload = payload or build_sample_payload(symbol)
        store.upsert_stock_payload(payload)
        click.echo(f'Persisted payload for {symbol.upper()}')

    @app.cli.command('crawler-job')
    @click.option('--symbol', required=True)
    @click.option('--name', required=True)
    @click.option('--metadata', default='', help='Optional metadata string (key=value pairs)')
    def crawler_job(symbol: str, name: str, metadata: str):
        metadata_map = {}
        for pair in metadata.split(','):
            if '=' in pair:
                key, value = pair.split('=', 1)
                metadata_map[key.strip()] = value.strip()
        job = store.ensure_job(symbol=symbol, name=name, metadata=metadata_map)
        click.echo(f'Ensured crawler job {job.uid} for {job.symbol}')
