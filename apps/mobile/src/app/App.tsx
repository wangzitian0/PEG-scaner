import React, { useEffect, useMemo, useState } from 'react';
import {
  SafeAreaView,
  StyleSheet,
  View,
  Text,
  StatusBar,
  FlatList,
} from 'react-native';
import { Root, Type } from 'protobufjs';

import pingDescriptor from '../proto/ping_descriptor.json';

interface PegStock {
  symbol: string;
  name: string;
  pe_ratio: number;
  earnings_growth: number;
  peg_ratio: number;
}

interface PingResponse {
  message: string;
  agent: string;
  timestampMs: number;
}

const API_BASE_URL = 'http://127.0.0.1:8000/api';

export const App = () => {
  const [stocks, setStocks] = useState<PegStock[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [ping, setPing] = useState<PingResponse | null>(null);
  const [pingError, setPingError] = useState<string | null>(null);

  const pingType = useMemo<Type>(() => {
    const root = Root.fromJSON(pingDescriptor as any);
    return root.lookupType('pegscanner.ping.PingResponse') as Type;
  }, []);

  const decodePing = (buffer: ArrayBuffer): PingResponse => {
    const message = pingType.decode(new Uint8Array(buffer));
    const object = pingType.toObject(message, { longs: Number });
    return {
      message: object.message ?? '',
      agent: object.agent ?? '',
      timestampMs: Number(object.timestamp_ms ?? 0),
    };
  };

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
  }, []);

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

    return (
      <View
        accessibilityRole="status"
        accessibilityLabel={label}
        style={[styles.pingIndicatorBase, indicatorStyle, styles.pingIndicatorNoPointer]}
        dataSet={{ pingstatus: status }}
        testID="ping-indicator"
      />
    );
  };

  const renderItem = ({ item }: { item: PegStock }) => (
    <View style={styles.item}>
      <View style={styles.itemHeader}>
        <Text style={styles.title}>{item.symbol}</Text>
        <Text style={styles.subtitle}>{item.name}</Text>
      </View>
      <View style={styles.itemBody}>
        <Text style={styles.pegRatio}>PEG: {item.peg_ratio.toFixed(2)}</Text>
        <Text>P/E: {item.pe_ratio.toFixed(2)}</Text>
        <Text>Growth: {(item.earnings_growth * 100).toFixed(2)}%</Text>
      </View>
    </View>
  );

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
              Please make sure the Django development server is running.
            </Text>
          </View>
        ) : (
          <FlatList
            data={stocks}
            renderItem={renderItem}
            keyExtractor={(item) => item.symbol}
          />
        )}
      </SafeAreaView>
    </>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f0f0',
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
  item: {
    backgroundColor: '#fff',
    padding: 20,
    marginVertical: 8,
    marginHorizontal: 16,
    borderRadius: 8,
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
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    fontSize: 18,
    color: 'red',
    textAlign: 'center',
  },
});

export default App;
