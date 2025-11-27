import React, { useCallback, useEffect, useState } from 'react';
import {
  SafeAreaView,
  StyleSheet,
  View,
  Text,
  FlatList,
  ViewProps,
  ActivityIndicator,
  TouchableOpacity,
  TextInput,
} from 'react-native';

interface PegStock {
  symbol: string;
  name: string;
  peRatio: number | null;
  earningsGrowth: number | null;
  pegRatio: number | null;
}

interface PingResponse {
  message: string;
  agent: string;
  timestampMs: number;
}

interface CompanyValuationDetails {
  psRatio: number | null;
  peRatio: number | null;
  pbRatio: number | null;
}

interface FinancialIndicatorsDetails {
  eps: number | null;
  fcf: number | null;
  currentRatio: number | null;
  roe: number | null;
}

interface SingleStockCompanyInfo {
  symbol: string;
  description: string;
  sector: string;
  industry: string;
  valuation: CompanyValuationDetails | null;
  indicators: FinancialIndicatorsDetails | null;
}

interface KLinePoint {
  timestamp: number;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  volume: number | null;
}

interface SingleStockNewsItem {
  title: string;
  url: string | null;
  source: string | null;
  publishedAt: number | null;
}

interface SingleStockPageData {
  stock: {
    symbol: string;
    name: string;
    exchange: string;
    currency: string;
    companyInfo: SingleStockCompanyInfo | null;
  };
  dailyKline: KLinePoint[];
  news: SingleStockNewsItem[];
}

type GraphQLErrorItem = { message?: string };
type GraphQLResponse<T> = { data: T; errors?: GraphQLErrorItem[] };

const resolveGraphqlUrl = () => {
  // If a full URL is provided via env, honor it (e.g., https://api.truealpha.club/graphql)
  if (process.env.PEG_GRAPHQL_URL && process.env.PEG_GRAPHQL_URL.trim().length > 0) {
    return process.env.PEG_GRAPHQL_URL.trim();
  }
  if (typeof window !== 'undefined') {
    // Use current host in web builds to avoid 127.0.0.1 in production bundles
    return `${window.location.origin.replace(/\/$/, '')}/graphql`;
  }
  // Native/SSR fallback via env; default to localhost for dev
  return process.env.PEG_GRAPHQL_URL || 'http://127.0.0.1:8000/graphql';
};

const GRAPHQL_URL = resolveGraphqlUrl();

const PING_QUERY = /* GraphQL */ `
  query Ping {
    ping {
      message
      agent
      timestampMs
    }
  }
`;

const PEG_STOCKS_QUERY = /* GraphQL */ `
  query PegStocks {
    pegStocks {
      symbol
      name
      peRatio
      earningsGrowth
      pegRatio
    }
  }
`;

const SINGLE_STOCK_QUERY = /* GraphQL */ `
  query SingleStock($symbol: String!) {
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
          valuation {
            psRatio
            peRatio
            pbRatio
          }
          indicators {
            eps
            fcf
            currentRatio
            roe
          }
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
`;

const getInitialSymbolFromLocation = (): string | null => {
  if (typeof window === 'undefined') {
    return null;
  }
  try {
    const params = new URLSearchParams(window.location.search);
    const symbol = params.get('symbol');
    return symbol ? symbol.trim().toUpperCase() : null;
  } catch {
    return null;
  }
};

const updateSymbolQueryParam = (symbol: string) => {
  if (typeof window === 'undefined' || typeof window.history?.replaceState !== 'function') {
    return;
  }
  try {
    const url = new URL(window.location.href);
    url.searchParams.set('symbol', symbol);
    window.history.replaceState({}, '', url);
  } catch {
    // ignore if URL manipulation fails
  }
};

async function executeGraphQL<T>(
  query: string,
  variables?: Record<string, any>,
): Promise<T> {
  const resp = await fetch(GRAPHQL_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, variables }),
  });
  if (!resp.ok) {
    throw new Error(`GraphQL HTTP ${resp.status}`);
  }
  const body: GraphQLResponse<T> = await resp.json();
  if (body.errors && body.errors.length > 0) {
    const message = body.errors.map((e) => e.message || 'GraphQL error').join('; ');
    throw new Error(message);
  }
  return body.data;
}

export const App = () => {
  const [stocks, setStocks] = useState<PegStock[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [ping, setPing] = useState<PingResponse | null>(null);
  const [pingError, setPingError] = useState<string | null>(null);
  const initialQuerySymbol = getInitialSymbolFromLocation();
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(initialQuerySymbol);
  const [symbolInput, setSymbolInput] = useState(initialQuerySymbol ?? '');
  const [singleStock, setSingleStock] = useState<SingleStockPageData | null>(null);
  const [singleStockError, setSingleStockError] = useState<string | null>(null);
  const [isSingleStockLoading, setIsSingleStockLoading] = useState(false);

  const fetchPing = useCallback(async () => {
    try {
      const result = await executeGraphQL<{ ping: PingResponse }>(PING_QUERY);
      setPing(result.ping);
      setPingError(null);
    } catch (e) {
      setPing(null);
      setPingError(e instanceof Error ? e.message : 'Unknown ping failure');
    }
  }, []);

  const fetchPegStocks = useCallback(async () => {
    try {
      const result = await executeGraphQL<{ pegStocks: PegStock[] }>(PEG_STOCKS_QUERY);
      setStocks(result.pegStocks);
      setError(null);
    } catch (e) {
      setStocks([]);
      setError(e instanceof Error ? e.message : 'Unknown error occurred');
    }
  }, []);

  const fetchSingleStockPage = useCallback(
    async (symbol: string) => {
      setIsSingleStockLoading(true);
      setSingleStockError(null);
      try {
        const result = await executeGraphQL<{ singleStock: SingleStockPageData | null }>(
          SINGLE_STOCK_QUERY,
          { symbol },
        );
        if (!result.singleStock) {
          throw new Error(`Single stock data not found for ${symbol}`);
        }
        setSingleStock(result.singleStock);
      } catch (e) {
        setSingleStock(null);
        setSingleStockError(
          e instanceof Error ? e.message : 'Unknown single stock failure',
        );
      } finally {
        setIsSingleStockLoading(false);
      }
    },
    [],
  );

  const applySymbolSelection = useCallback(
    (symbol: string) => {
      const normalized = symbol.trim().toUpperCase();
      if (!normalized) {
        return;
      }
      setSelectedSymbol(normalized);
      setSymbolInput(normalized);
      updateSymbolQueryParam(normalized);
    },
    [],
  );

  useEffect(() => {
    fetchPing();
    fetchPegStocks();
  }, [fetchPing, fetchPegStocks]);

  useEffect(() => {
    if (selectedSymbol) {
      return;
    }
    if (symbolInput) {
      setSelectedSymbol(symbolInput);
      updateSymbolQueryParam(symbolInput);
      return;
    }
    if (stocks.length > 0) {
      applySymbolSelection(stocks[0].symbol);
    }
  }, [selectedSymbol, symbolInput, stocks, applySymbolSelection]);

  useEffect(() => {
    if (!selectedSymbol) {
      return;
    }
    fetchSingleStockPage(selectedSymbol);
  }, [selectedSymbol, fetchSingleStockPage]);

  const renderPingIndicator = () => {
    let indicatorStyle = styles.pingIndicatorChecking;
    let label = 'Backend status: checking';
    let status: 'checking' | 'ok' | 'error' = 'checking';

    if (pingError) {
      indicatorStyle = styles.pingIndicatorError;
      label = `Backend status error: ${pingError}`;
      status = 'error';
    } else if (ping) {
      indicatorStyle = styles.pingIndicatorOk;
      label = `Backend status ok at ${new Date(
        ping.timestampMs,
      ).toISOString()}`;
      status = 'ok';
    }

    const pingDatasetProps = {
      dataSet: { pingstatus: status },
      'data-pingstatus': status,
    } as unknown as ViewProps;

    return (
      <View
        accessibilityLabel={label}
        style={[
          styles.pingIndicatorBase,
          indicatorStyle,
          styles.pingIndicatorNoPointer,
        ]}
        {...pingDatasetProps}
        testID="ping-indicator"
      />
    );
  };

  const renderSingleStockSection = () => (
    <View style={styles.singleStockSection}>
      <Text style={styles.sectionTitle}>Single Stock Page</Text>
      <View style={styles.symbolInputRow}>
        <TextInput
          value={symbolInput}
          onChangeText={(text) => setSymbolInput(text.toUpperCase())}
          placeholder="Enter symbol (e.g. AAPL)"
          autoCapitalize="characters"
          style={styles.symbolInput}
          onSubmitEditing={() => applySymbolSelection(symbolInput)}
        />
        <TouchableOpacity
          style={styles.symbolInputButton}
          onPress={() => applySymbolSelection(symbolInput)}
        >
          <Text style={styles.symbolInputButtonText}>Load</Text>
        </TouchableOpacity>
      </View>
      {selectedSymbol && (
        <Text style={styles.sectionSubtitle}>Symbol: {selectedSymbol}</Text>
      )}
      {isSingleStockLoading && (
        <View style={styles.statusRow}>
          <ActivityIndicator size="small" color="#0d9488" />
          <Text style={styles.statusText}>Loading data…</Text>
        </View>
      )}
      {singleStockError && (
        <Text style={styles.errorText}>Single stock error: {singleStockError}</Text>
      )}
      {!isSingleStockLoading && singleStock && (
        <>
          <View style={styles.singleStockHeader}>
            <Text style={styles.singleStockSymbol}>
              {singleStock.stock.symbol}
            </Text>
            <Text style={styles.singleStockName}>{singleStock.stock.name}</Text>
            <Text style={styles.singleStockMeta}>
              {singleStock.stock.exchange} · {singleStock.stock.currency}
            </Text>
          </View>
          {singleStock.stock.companyInfo && (
            <View style={styles.companyInfoBlock}>
              <Text style={styles.companyInfoLabel}>
                Sector: {singleStock.stock.companyInfo.sector || '—'}
              </Text>
              <Text style={styles.companyInfoLabel}>
                Industry: {singleStock.stock.companyInfo.industry || '—'}
              </Text>
              <Text style={styles.companyInfoLabel}>
                {singleStock.stock.companyInfo.description || 'No description yet.'}
              </Text>
            </View>
          )}
          <View style={styles.valuationRow}>
            <InfoBadge
              label="P/S"
              value={formatNumber(singleStock.stock.companyInfo?.valuation?.psRatio)}
            />
            <InfoBadge
              label="P/E"
              value={formatNumber(singleStock.stock.companyInfo?.valuation?.peRatio)}
            />
            <InfoBadge
              label="P/B"
              value={formatNumber(singleStock.stock.companyInfo?.valuation?.pbRatio)}
            />
          </View>
          <View style={styles.valuationRow}>
            <InfoBadge
              label="EPS"
              value={formatNumber(singleStock.stock.companyInfo?.indicators?.eps)}
            />
            <InfoBadge
              label="FCF"
              value={formatNumber(singleStock.stock.companyInfo?.indicators?.fcf)}
            />
            <InfoBadge
              label="Curr. Ratio"
              value={formatNumber(singleStock.stock.companyInfo?.indicators?.currentRatio)}
            />
            <InfoBadge
              label="ROE"
              value={formatNumber(singleStock.stock.companyInfo?.indicators?.roe)}
            />
          </View>
          <View style={styles.newsSection}>
            <Text style={styles.sectionSubtitle}>News</Text>
            {singleStock.news.length === 0 && (
              <Text style={styles.statusText}>No news yet.</Text>
            )}
            {singleStock.news.map((item) => (
              <View key={item.title} style={styles.newsCard}>
                <Text style={styles.newsTitle}>{item.title}</Text>
                <Text style={styles.newsMeta}>
                  {item.source || 'Unknown source'} ·{' '}
                  {item.publishedAt
                    ? new Date(item.publishedAt).toISOString()
                    : 'N/A'}
                </Text>
              </View>
            ))}
          </View>
        </>
      )}
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>PEG Scanner (GraphQL)</Text>
        {renderPingIndicator()}
      </View>
      {error && <Text style={styles.errorText}>{error}</Text>}
      <Text style={styles.sectionTitle}>PEG Watchlist</Text>
      <FlatList
        data={stocks}
        keyExtractor={(item) => item.symbol}
        renderItem={({ item }) => (
          <PegCard
            stock={item}
            onPress={() => applySymbolSelection(item.symbol)}
          />
        )}
        style={styles.list}
      />
      {renderSingleStockSection()}
    </SafeAreaView>
  );
};

const PegCard = ({ stock, onPress }: { stock: PegStock; onPress: () => void }) => (
  <TouchableOpacity style={styles.card} onPress={onPress}>
    <View style={styles.cardHeader}>
      <Text style={styles.cardSymbol}>{stock.symbol}</Text>
      <Text style={styles.cardName}>{stock.name}</Text>
    </View>
    <View style={styles.cardMetrics}>
      <InfoBadge label="P/E" value={formatNumber(stock.peRatio)} />
      <InfoBadge label="Earnings Growth" value={formatNumber(stock.earningsGrowth)} />
      <InfoBadge label="PEG" value={formatNumber(stock.pegRatio)} />
    </View>
  </TouchableOpacity>
);

const InfoBadge = ({ label, value }: { label: string; value: string }) => (
  <View style={styles.badge}>
    <Text style={styles.badgeLabel}>{label}</Text>
    <Text style={styles.badgeValue}>{value}</Text>
  </View>
);

const formatNumber = (value: number | null | undefined): string => {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return '—';
  }
  if (Math.abs(value) >= 1000) {
    return value.toFixed(0);
  }
  return value.toFixed(2);
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0b1120',
    padding: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    color: '#f8fafc',
    fontSize: 20,
    fontWeight: '700',
  },
  list: {
    marginBottom: 24,
  },
  card: {
    backgroundColor: '#111827',
    padding: 12,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#1f2937',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  cardSymbol: {
    color: '#fbbf24',
    fontSize: 18,
    fontWeight: '700',
  },
  cardName: {
    color: '#e5e7eb',
    fontSize: 14,
  },
  cardMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  badge: {
    backgroundColor: '#1f2937',
    paddingVertical: 6,
    paddingHorizontal: 8,
    borderRadius: 8,
    minWidth: 70,
  },
  badgeLabel: {
    color: '#9ca3af',
    fontSize: 12,
  },
  badgeValue: {
    color: '#e5e7eb',
    fontSize: 14,
    fontWeight: '600',
  },
  sectionTitle: {
    color: '#f8fafc',
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 8,
  },
  sectionSubtitle: {
    color: '#cbd5e1',
    fontSize: 14,
    marginBottom: 8,
  },
  singleStockSection: {
    backgroundColor: '#0f172a',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#1f2937',
  },
  singleStockHeader: {
    marginTop: 12,
    marginBottom: 12,
  },
  singleStockSymbol: {
    color: '#fbbf24',
    fontSize: 22,
    fontWeight: '800',
  },
  singleStockName: {
    color: '#e5e7eb',
    fontSize: 16,
  },
  singleStockMeta: {
    color: '#94a3b8',
    fontSize: 14,
    marginTop: 4,
  },
  companyInfoBlock: {
    backgroundColor: '#111827',
    padding: 12,
    borderRadius: 12,
    marginBottom: 12,
  },
  companyInfoLabel: {
    color: '#e5e7eb',
    fontSize: 14,
    marginBottom: 4,
  },
  valuationRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  newsSection: {
    marginTop: 12,
  },
  newsCard: {
    backgroundColor: '#111827',
    padding: 10,
    borderRadius: 10,
    marginBottom: 8,
  },
  newsTitle: {
    color: '#e5e7eb',
    fontSize: 14,
    fontWeight: '600',
  },
  newsMeta: {
    color: '#94a3b8',
    fontSize: 12,
    marginTop: 4,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 4,
  },
  statusText: {
    color: '#cbd5e1',
    marginLeft: 8,
  },
  pingIndicatorBase: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  pingIndicatorNoPointer: {
    pointerEvents: 'none',
  },
  pingIndicatorChecking: {
    backgroundColor: '#f59e0b',
  },
  pingIndicatorOk: {
    backgroundColor: '#22c55e',
  },
  pingIndicatorError: {
    backgroundColor: '#ef4444',
  },
  symbolInputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  symbolInput: {
    flex: 1,
    backgroundColor: '#111827',
    color: '#f8fafc',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#1f2937',
    marginRight: 8,
  },
  symbolInputButton: {
    backgroundColor: '#10b981',
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 10,
  },
  symbolInputButtonText: {
    color: '#0b1120',
    fontWeight: '700',
  },
  errorText: {
    color: '#ef4444',
    marginBottom: 8,
  },
});
