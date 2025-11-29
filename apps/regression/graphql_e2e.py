#!/usr/bin/env python3
"""
End-to-end GraphQL tests for all queries.

Usage:
    python3 apps/regression/graphql_e2e.py

Environment Variables:
    PEGSCANNER_GRAPHQL_URL: Override the endpoint (default http://127.0.0.1:8000/graphql).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

GRAPHQL_URL = os.environ.get("PEGSCANNER_GRAPHQL_URL", "http://127.0.0.1:8000/graphql")


def graphql_request(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Send GraphQL request and return parsed response."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        GRAPHQL_URL, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def test_ping() -> bool:
    """Test ping query returns expected payload."""
    print("[e2e] Testing ping query...")
    
    result = graphql_request("query { ping { message agent timestampMs } }")
    
    if "errors" in result:
        print(f"  ❌ GraphQL errors: {result['errors']}")
        return False
    
    data = result.get("data", {}).get("ping", {})
    if data.get("message") != "pong":
        print(f"  ❌ Expected message='pong', got: {data}")
        return False
    
    if not data.get("agent"):
        print(f"  ❌ Missing agent field")
        return False
    
    if not data.get("timestampMs"):
        print(f"  ❌ Missing timestampMs field")
        return False
    
    print(f"  ✅ ping OK: agent={data['agent']}")
    return True


def test_peg_stocks() -> bool:
    """Test pegStocks query returns list of candidates."""
    print("[e2e] Testing pegStocks query...")
    
    result = graphql_request("query { pegStocks { symbol name peRatio earningsGrowth pegRatio } }")
    
    if "errors" in result:
        print(f"  ❌ GraphQL errors: {result['errors']}")
        return False
    
    stocks = result.get("data", {}).get("pegStocks", [])
    
    if not isinstance(stocks, list):
        print(f"  ❌ Expected list, got: {type(stocks)}")
        return False
    
    if len(stocks) == 0:
        print(f"  ⚠️  pegStocks returned empty list (may be OK if no data)")
        return True
    
    # Validate first stock has required fields
    first = stocks[0]
    required_fields = ["symbol", "name"]
    for field in required_fields:
        if field not in first:
            print(f"  ❌ Missing required field: {field}")
            return False
    
    symbols = [s["symbol"] for s in stocks]
    print(f"  ✅ pegStocks OK: {len(stocks)} stocks ({', '.join(symbols[:3])}{'...' if len(symbols) > 3 else ''})")
    return True


def test_single_stock() -> bool:
    """Test singleStock query returns complete stock data."""
    print("[e2e] Testing singleStock query...")
    
    query = """
    query ($symbol: String!) {
      singleStock(symbol: $symbol) {
        stock {
          symbol
          name
          exchange
          currency
          companyInfo {
            symbol
            description
            sector
            industry
            valuation { psRatio peRatio pbRatio }
            indicators { eps fcf currentRatio roe }
          }
        }
        dailyKline {
          timestamp
          open
          high
          low
          close
          volume
        }
        news {
          title
          url
          source
          publishedAt
        }
      }
    }
    """
    
    result = graphql_request(query, {"symbol": "AAPL"})
    
    if "errors" in result:
        print(f"  ❌ GraphQL errors: {result['errors']}")
        return False
    
    data = result.get("data", {}).get("singleStock")
    
    if data is None:
        print(f"  ⚠️  singleStock(AAPL) returned null (may be OK if no data)")
        return True
    
    # Validate stock
    stock = data.get("stock", {})
    if stock.get("symbol") != "AAPL":
        print(f"  ❌ Expected symbol='AAPL', got: {stock.get('symbol')}")
        return False
    
    # Validate dailyKline
    kline = data.get("dailyKline", [])
    if not isinstance(kline, list):
        print(f"  ❌ dailyKline should be list, got: {type(kline)}")
        return False
    
    # Validate news
    news = data.get("news", [])
    if not isinstance(news, list):
        print(f"  ❌ news should be list, got: {type(news)}")
        return False
    
    print(f"  ✅ singleStock OK: {stock.get('name')}, {len(kline)} kline points, {len(news)} news items")
    return True


def test_single_stock_not_found() -> bool:
    """Test singleStock with unknown symbol returns null."""
    print("[e2e] Testing singleStock with unknown symbol...")
    
    result = graphql_request(
        "query ($symbol: String!) { singleStock(symbol: $symbol) { stock { symbol } } }",
        {"symbol": "ZZZNOTEXIST"}
    )
    
    if "errors" in result:
        print(f"  ❌ GraphQL errors: {result['errors']}")
        return False
    
    data = result.get("data", {}).get("singleStock")
    
    if data is not None:
        print(f"  ❌ Expected null for unknown symbol, got: {data}")
        return False
    
    print(f"  ✅ singleStock(unknown) correctly returns null")
    return True


def main() -> int:
    print(f"\n{'='*60}")
    print(f"GraphQL E2E Tests - {GRAPHQL_URL}")
    print(f"{'='*60}\n")
    
    tests = [
        ("ping", test_ping),
        ("pegStocks", test_peg_stocks),
        ("singleStock", test_single_stock),
        ("singleStock (not found)", test_single_stock_not_found),
    ]
    
    results: List[tuple] = []
    
    for name, test_fn in tests:
        try:
            passed = test_fn()
            results.append((name, passed, None))
        except urllib.error.URLError as e:
            print(f"  ❌ Network error: {e}")
            results.append((name, False, str(e)))
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            results.append((name, False, str(e)))
    
    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    
    passed = sum(1 for _, p, _ in results if p)
    failed = len(results) - passed
    
    for name, p, err in results:
        status = "✅ PASS" if p else "❌ FAIL"
        print(f"  {status}: {name}")
        if err:
            print(f"         Error: {err}")
    
    print(f"\nTotal: {passed}/{len(results)} passed")
    
    if failed > 0:
        print("\n❌ Some tests failed!")
        return 1
    
    print("\n✅ All tests passed!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

