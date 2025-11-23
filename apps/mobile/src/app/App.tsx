import React, { useCallback, useEffect, useMemo, useState } from 'react';
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
import { Root, Type } from 'protobufjs';

import pingDescriptor from '../proto/ping_descriptor.json';
import singleStockDescriptor from '../proto/single_stock_page_descriptor.json';

interface PegStock {
  symbol: string;
  name: string;
  pe_ratio: number;
  earnings_growth: number;
  peg_ratio: number | null;
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
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface SingleStockNewsItem {
  title: string;
  url: string;
  source: string;
  publishedAt: number;
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

const API_BASE_URL = 'http://127.0.0.1:8000/api';

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

  const pingType = useMemo<Type>(() => {
    const root = Root.fromJSON(pingDescriptor as any);
    return root.lookupType('pegscanner.ping.PingResponse') as Type;
  }, []);

  const singleStockPageType = useMemo<Type>(() => {
    const root = Root.fromJSON(singleStockDescriptor as any);
    return root.lookupType(
      'pegscanner.single_stock_page.SingleStockPageResponse',
    ) as Type;
  }, []);

  const decodePing = useCallback(
    (buffer: ArrayBuffer): PingResponse => {
      const message = pingType.decode(new Uint8Array(buffer));
      const object = pingType.toObject(message, { longs: Number });
      return {
        message: object.message ?? '',
        agent: object.agent ?? '',
        timestampMs: Number(object.timestamp_ms ?? 0),
      };
    },
    [pingType],
  );

  const decodeSingleStockPage = useCallback(
    (buffer: ArrayBuffer): SingleStockPageData => {
      const message = singleStockPageType.decode(new Uint8Array(buffer));
      const object = singleStockPageType.toObject(message, {
        longs: Number,
      }) as any;

      const valuation = object.stock?.company_info?.valuation;
      const indicators = object.stock?.company_info?.indicators;
      const companyInfo = object.stock?.company_info
        ? {
            symbol: object.stock.company_info.symbol ?? '',
            description: object.stock.company_info.description ?? '',
            sector: object.stock.company_info.sector ?? '',
            industry: object.stock.company_info.industry ?? '',
            valuation: valuation
              ? {
                  psRatio: valuation.ps_ratio ?? null,
                  peRatio: valuation.pe_ratio ?? null,
                  pbRatio: valuation.pb_ratio ?? null,
                }
              : null,
            indicators: indicators
              ? {
                  eps: indicators.eps ?? null,
                  fcf: indicators.fcf ?? null,
                  currentRatio: indicators.current_ratio ?? null,
                  roe: indicators.roe ?? null,
                }
              : null,
          }
        : null;

      return {
        stock: {
          symbol: object.stock?.symbol ?? '',
          name: object.stock?.name ?? '',
          exchange: object.stock?.exchange ?? '',
          currency: object.stock?.currency ?? '',
          companyInfo,
        },
        dailyKline: (object.daily_kline ?? []).map((row: any) => ({
          timestamp: Number(row.timestamp ?? 0),
          open: Number(row.open ?? 0),
          high: Number(row.high ?? 0),
          low: Number(row.low ?? 0),
          close: Number(row.close ?? 0),
          volume: Number(row.volume ?? 0),
        })),
        news: (object.news ?? []).map((item: any) => ({
          title: item.title ?? '',
          url: item.url ?? '',
          source: item.source ?? '',
          publishedAt: Number(item.published_at ?? 0),
        })),
      };
    },
    [singleStockPageType],
  );

  useEffect(() => {
    const fetchPing = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/ping/`);
        if (!response.ok) {
          throw new Error('Ping endpoint unavailable');
        }
        const buffer = await response.arrayBuffer();
        setPing(decodePing(buffer));
      } catch (e) {
        if (e instanceof Error) {
          setPingError(e.message);
        } else {
          setPingError('Unknown ping failure');
        }
      }
    };

    const fetchStocks = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/peg-stocks/`);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setStocks(data);
      } catch (e) {
        if (e instanceof Error) {
          setError(e.message);
        } else {
          setError('An unknown error occurred');
        }
      }
    };

    fetchPing();
    fetchStocks();
  }, [decodePing]);

  const fetchSingleStockPage = useCallback(
    async (symbol: string) => {
      setIsSingleStockLoading(true);
      setSingleStockError(null);
      try {
        const response = await fetch(
          `${API_BASE_URL}/single-stock-page/?symbol=${symbol}`,
        );
        if (!response.ok) {
          throw new Error('Single stock endpoint unavailable');
        }
        const buffer = await response.arrayBuffer();
        setSingleStock(decodeSingleStockPage(buffer));
      } catch (e) {
        setSingleStock(null);
        setSingleStockError(
          e instanceof Error ? e.message : 'Unknown single stock failure',
        );
      } finally {
        setIsSingleStockLoading(false);
      }
    },
    [decodeSingleStockPage],
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
              label="ROE"
              value={formatPercent(singleStock.stock.companyInfo?.indicators?.roe)}
            />
          </View>
          <View style={styles.sectionCard}>
            <Text style={styles.sectionSubtitle}>Recent Daily K-Line</Text>
            {singleStock.dailyKline.length === 0 ? (
              <Text style={styles.mutedText}>No K-line data available yet.</Text>
            ) : (
              singleStock.dailyKline.slice(0, 5).map((row) => (
                <View key={row.timestamp} style={styles.klineRow}>
                  <Text style={styles.klineLabel}>
                    {formatTimestamp(row.timestamp)}
                  </Text>
                  <Text style={styles.klineValue}>
                    O {row.open.toFixed(2)} · C {row.close.toFixed(2)} · V{' '}
                    {formatVolume(row.volume)}
                  </Text>
                </View>
              ))
            )}
          </View>
          <View style={styles.sectionCard}>
            <Text style={styles.sectionSubtitle}>News</Text>
            {singleStock.news.length === 0 ? (
              <Text style={styles.mutedText}>
                News feed not ingested yet. This is a placeholder.
              </Text>
            ) : (
              singleStock.news.slice(0, 3).map((item) => (
                <View key={item.url} style={styles.newsItem}>
                  <Text style={styles.newsItemTitle}>{item.title}</Text>
                  <Text style={styles.newsItemMeta}>
                    {item.source} · {formatTimestamp(item.publishedAt)}
                  </Text>
                </View>
              ))
            )}
          </View>
        </>
      )}
    </View>
  );

  const renderItem = ({ item }: { item: PegStock }) => {
    const isSelected = selectedSymbol === item.symbol;
    return (
      <TouchableOpacity
        onPress={() => applySymbolSelection(item.symbol)}
        style={[styles.item, isSelected && styles.selectedItem]}
        activeOpacity={0.8}
      >
        <View style={styles.itemHeader}>
          <Text style={styles.title}>{item.symbol}</Text>
          <Text style={styles.subtitle}>{item.name}</Text>
        </View>
        <View style={styles.itemBody}>
          <Text style={styles.pegRatio}>
            PEG: {formatNumber(item.peg_ratio)}
          </Text>
          <Text>P/E: {formatNumber(item.pe_ratio)}</Text>
          <Text>Growth: {formatPercent(item.earnings_growth)}</Text>
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <>
      {renderPingIndicator()}
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.headerText}>PEG Scanner</Text>
        </View>
        {error ? (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>Error: {error}</Text>
            <Text style={styles.errorText}>
              Please make sure the Flask backend server is running.
            </Text>
          </View>
        ) : (
          <FlatList
            data={stocks}
            renderItem={renderItem}
            keyExtractor={(item) => item.symbol}
            extraData={selectedSymbol}
            ListHeaderComponent={renderSingleStockSection}
            ListEmptyComponent={
              <Text style={styles.emptyText}>
                No PEG watchlist data available yet.
              </Text>
            }
            contentContainerStyle={styles.listContent}
          />
        )}
      </SafeAreaView>
    </>
  );
};

export default App;

const InfoBadge = ({ label, value }: { label: string; value: string }) => (
  <View style={styles.infoBadge}>
    <Text style={styles.infoBadgeLabel}>{label}</Text>
    <Text style={styles.infoBadgeValue}>{value}</Text>
  </View>
);

const formatNumber = (
  value: number | null | undefined,
  digits: number = 2,
): string => {
  if (value === null || value === undefined) {
    return '—';
  }
  return Number(value).toFixed(digits);
};

const formatPercent = (value: number | null | undefined): string => {
  if (value === null || value === undefined) {
    return '—';
  }
  return `${(value * 100).toFixed(2)}%`;
};

const formatTimestamp = (value: number | null | undefined): string => {
  if (!value) {
    return '—';
  }
  const date = new Date(value * 1000);
  if (Number.isNaN(date.getTime())) {
    return '—';
  }
  return date.toLocaleDateString();
};

const formatVolume = (value: number | null | undefined): string => {
  if (value === null || value === undefined) {
    return '—';
  }
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`;
  }
  if (value >= 1_000) {
    return `${(value / 1_000).toFixed(1)}K`;
  }
  return value.toString();
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f4f5f7',
  },
  header: {
    backgroundColor: '#fff',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  headerText: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  listContent: {
    paddingBottom: 48,
  },
  singleStockSection: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginTop: 16,
    marginBottom: 8,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOpacity: 0.04,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 6,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
  },
  sectionSubtitle: {
    fontSize: 14,
    color: '#475569',
    marginTop: 4,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
  },
  statusText: {
    color: '#0f172a',
    marginLeft: 8,
  },
  singleStockHeader: {
    marginTop: 12,
  },
  singleStockSymbol: {
    fontSize: 28,
    fontWeight: '700',
  },
  singleStockName: {
    fontSize: 18,
    color: '#475569',
  },
  singleStockMeta: {
    fontSize: 14,
    color: '#8891aa',
    marginTop: 4,
  },
  companyInfoBlock: {
    marginTop: 12,
  },
  companyInfoLabel: {
    color: '#475569',
    marginBottom: 4,
  },
  symbolInputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
  },
  symbolInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginRight: 8,
    backgroundColor: '#fff',
  },
  symbolInputButton: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    backgroundColor: '#0ea5e9',
    borderRadius: 8,
  },
  symbolInputButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  valuationRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 12,
  },
  infoBadge: {
    flex: 1,
    backgroundColor: '#f1f5f9',
    padding: 10,
    borderRadius: 8,
    marginHorizontal: 4,
  },
  infoBadgeLabel: {
    fontSize: 12,
    color: '#475569',
  },
  infoBadgeValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#0f172a',
  },
  sectionCard: {
    marginTop: 16,
  },
  klineRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 4,
  },
  klineLabel: {
    fontWeight: '600',
  },
  klineValue: {
    color: '#475569',
  },
  newsItem: {
    marginTop: 8,
  },
  newsItemTitle: {
    fontWeight: '600',
  },
  newsItemMeta: {
    color: '#94a3b8',
    fontSize: 12,
  },
  mutedText: {
    color: '#94a3b8',
    marginTop: 4,
  },
  item: {
    backgroundColor: '#fff',
    padding: 20,
    marginVertical: 8,
    marginHorizontal: 16,
    borderRadius: 8,
  },
  selectedItem: {
    borderWidth: 1,
    borderColor: '#0ea5e9',
  },
  itemHeader: {
    marginBottom: 10,
  },
  itemBody: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
  },
  pegRatio: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#007bff',
  },
  errorContainer: {
    padding: 16,
  },
  errorText: {
    color: '#d7263d',
  },
  emptyText: {
    textAlign: 'center',
    color: '#94a3b8',
    marginTop: 24,
  },
  pingIndicatorBase: {
    position: 'absolute',
    top: 8,
    left: 8,
    width: 9,
    height: 9,
    borderRadius: 2,
    zIndex: 100,
  },
  pingIndicatorOk: {
    backgroundColor: '#2b8a3e',
  },
  pingIndicatorError: {
    backgroundColor: '#d7263d',
  },
  pingIndicatorChecking: {
    backgroundColor: '#d0e2ff',
  },
  pingIndicatorNoPointer: {
    pointerEvents: 'none' as const,
  },
});
