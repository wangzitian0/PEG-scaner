import React, { useEffect, useState } from 'react';
import {
  SafeAreaView,
  StyleSheet,
  ScrollView,
  View,
  Text,
  StatusBar,
  FlatList,
  TouchableOpacity,
} from 'react-native';

interface PegStock {
  symbol: string;
  name: string;
  pe_ratio: number;
  earnings_growth: number;
  peg_ratio: number;
}

export const App = () => {
  const [stocks, setStocks] = useState<PegStock[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/peg-stocks/');
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

    fetchStocks();
  }, []);

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
      <StatusBar barStyle="dark-content" />
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
