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

interface Stock {
  symbol: string;
  name: string;
  exchange: string;
  currency: string;
}

export const App = () => {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/stocks/');
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

  const renderItem = ({ item }: { item: Stock }) => (
    <TouchableOpacity style={styles.item}>
      <Text style={styles.title}>{item.symbol}</Text>
      <Text style={styles.subtitle}>{item.name}</Text>
    </TouchableOpacity>
  );

  return (
    <>
      <StatusBar barStyle="dark-content" />
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.headerText}>Stocks</Text>
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
  title: {
    fontSize: 24,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
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
