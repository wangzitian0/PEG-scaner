from apps.backend.proto.generated import ping_pb2, single_stock_page_pb2


def test_ping_endpoint_returns_protobuf(client):
    response = client.get('/api/ping/')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/x-protobuf'
    payload = ping_pb2.PingResponse()
    payload.ParseFromString(response.data)
    assert payload.message == 'pong'
    assert payload.agent == 'pegscanner-backend'
    assert payload.timestamp_ms > 0


def test_single_stock_page_returns_payload(client):
    response = client.get('/api/single-stock-page/', query_string={'symbol': 'AAPL'})
    assert response.status_code == 200
    payload = single_stock_page_pb2.SingleStockPageResponse()
    payload.ParseFromString(response.data)
    assert payload.stock.symbol == 'AAPL'
    assert payload.stock.company_info.sector != ''


def test_single_stock_page_missing_symbol(client):
    response = client.get('/api/single-stock-page/')
    assert response.status_code == 400
    assert 'symbol' in response.json['detail']


def test_single_stock_page_unknown_symbol(client):
    response = client.get('/api/single-stock-page/', query_string={'symbol': 'ZZZ'})
    assert response.status_code == 404


def test_peg_stock_listing_returns_json(client):
    response = client.get('/api/peg-stocks/')
    assert response.status_code == 200
    body = response.get_json()
    assert isinstance(body, list)
    assert any(entry['symbol'] == 'AAPL' for entry in body)
