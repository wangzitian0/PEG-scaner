import json
import logging
from functools import lru_cache
from typing import Any, Dict, List, Optional

try:
    from django.conf import settings
except ImportError:  # pragma: no cover - non-Django contexts
    settings = None  # type: ignore

try:
    from neo4j import GraphDatabase, basic_auth
    from neo4j.exceptions import Neo4jError, ServiceUnavailable
except ImportError:  # pragma: no cover
    GraphDatabase = None  # type: ignore
    basic_auth = None  # type: ignore
    Neo4jError = Exception  # type: ignore
    ServiceUnavailable = Exception  # type: ignore

logger = logging.getLogger(__name__)


def _get_setting(name: str, default: Optional[str] = None) -> Optional[str]:
    if settings and hasattr(settings, name):
        return getattr(settings, name)
    return default


@lru_cache(maxsize=1)
def _get_driver():
    if not GraphDatabase:
        logger.warning('neo4j driver not installed; skipping graph operations')
        return None

    uri = _get_setting('NEO4J_URI')
    if not uri:
        logger.info('NEO4J_URI not configured; graph persistence disabled')
        return None

    username = _get_setting('NEO4J_USER')
    password = _get_setting('NEO4J_PASSWORD', '')
    auth = basic_auth(username, password) if username else None

    try:
        return GraphDatabase.driver(uri, auth=auth)
    except Exception as exc:  # pragma: no cover
        logger.error('Failed to create neo4j driver: %s', exc)
        return None


def _database_scope():
    database = _get_setting('NEO4J_DATABASE', '')
    return database or None


def upsert_stock_document(payload: Dict[str, Any]) -> bool:
    """
    Persists a stock document (metadata, kline, news) into Neo4j.
    """
    driver = _get_driver()
    if not driver:
        return False

    kline_json = json.dumps(payload.get('daily_kline', []))
    news_items = payload.get('news', [])
    params = {
        'symbol': payload['symbol'],
        'name': payload.get('name', ''),
        'sector': payload.get('sector', ''),
        'industry': payload.get('industry', ''),
        'description': payload.get('description', ''),
        'kline_json': kline_json,
        'news': [
            {
                'id': item.get('id') or f"{payload['symbol']}-{idx}",
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'source': item.get('source', ''),
                'published_at': item.get('published_at', 0),
            }
            for idx, item in enumerate(news_items)
        ],
    }

    query = """
    MERGE (s:Stock {symbol: $symbol})
    SET s.name = $name,
        s.sector = $sector,
        s.industry = $industry,
        s.description = $description,
        s.kline_json = $kline_json
    WITH s
    UNWIND $news AS newsItem
      MERGE (n:News {id: newsItem.id})
      SET n.title = newsItem.title,
          n.url = newsItem.url,
          n.source = newsItem.source,
          n.published_at = newsItem.published_at
      MERGE (s)-[:HAS_NEWS]->(n)
    """

    try:
        with driver.session(database=_database_scope()) as session:
            session.run(query, **params)
        return True
    except (Neo4jError, ServiceUnavailable) as exc:  # pragma: no cover
        logger.error('Failed to persist stock payload to neo4j: %s', exc)
        return False


def fetch_stock_document(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Reads stock data and news from Neo4j. Returns None when no record is found
    or when Neo4j is not configured.
    """
    driver = _get_driver()
    if not driver:
        return None

    query = """
    MATCH (s:Stock {symbol: $symbol})
    OPTIONAL MATCH (s)-[:HAS_NEWS]->(n:News)
    RETURN s AS stock, collect(n) AS news
    """
    try:
        with driver.session(database=_database_scope()) as session:
            result = session.run(query, symbol=symbol)
            record = result.single()
            if not record:
                return None
            stock_node = record['stock']
            news_nodes = [node for node in record['news'] if node]
            return {
                'stock': dict(stock_node) if stock_node else None,
                'daily_kline': json.loads(stock_node.get('kline_json') or '[]') if stock_node else [],
                'news': [_node_to_dict(node) for node in news_nodes],
            }
    except (Neo4jError, ServiceUnavailable) as exc:  # pragma: no cover
        logger.error('Failed to fetch stock payload from neo4j: %s', exc)
        return None


def _node_to_dict(node) -> Dict[str, Any]:
    return {
        'id': node.get('id', ''),
        'title': node.get('title', ''),
        'url': node.get('url', ''),
        'source': node.get('source', ''),
        'published_at': node.get('published_at', 0),
    }
