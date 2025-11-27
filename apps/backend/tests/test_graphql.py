def graphql(client, query: str, variables=None):
    return client.post('/graphql', json={'query': query, 'variables': variables or {}})


def test_ping_query_returns_payload(client):
    response = graphql(client, 'query Ping { ping { message agent timestampMs } }')
    assert response.status_code == 200
    payload = response.get_json()
    assert 'errors' not in payload
    data = payload['data']['ping']
    assert data['message'] == 'pong'
    assert data['agent'] == 'pegscanner-backend'
    assert data['timestampMs'] > 0


def test_single_stock_query_returns_payload(client):
    response = graphql(
        client,
        '''
        query Stock($symbol: String!) {
          singleStock(symbol: $symbol) {
            stock { symbol companyInfo { sector } }
            dailyKline { timestamp }
          }
        }
        ''',
        variables={'symbol': 'AAPL'},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert 'errors' not in payload
    data = payload['data']['singleStock']
    assert data is not None
    assert data['stock']['symbol'] == 'AAPL'
    assert data['stock']['companyInfo']['sector'] != ''


def test_single_stock_query_unknown_symbol_returns_null(client):
    response = graphql(client, 'query ($symbol: String!) { singleStock(symbol: $symbol) { stock { symbol } } }', variables={'symbol': 'ZZZ'})
    assert response.status_code == 200
    body = response.get_json()
    assert body['data']['singleStock'] is None


def test_peg_stocks_query_returns_list(client):
    response = graphql(client, 'query { pegStocks { symbol name pegRatio } }')
    assert response.status_code == 200
    data = response.get_json()
    assert 'errors' not in data
    items = data['data']['pegStocks']
    assert isinstance(items, list)
    assert any(entry['symbol'] == 'AAPL' for entry in items)
