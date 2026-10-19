import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { Card, Title, Paragraph, Button, TextInput } from 'react-native-paper';
import { VictoryLine, VictoryChart, VictoryTheme, VictoryAxis, VictoryScatter } from 'victory-native';
import { Calendar, Clock, TrendingUp, TrendingDown } from 'lucide-react-native';

const GlucoseScreen = () => {
  const [timeRange, setTimeRange] = useState('24h');
  const [glucoseInput, setGlucoseInput] = useState('');
  const [glucoseData, setGlucoseData] = useState(generateMockData());

  function generateMockData() {
    const data = [];
    for (let i = 0; i < 24; i++) {
      const hour = i;
      const glucose = 120 + Math.sin(i / 3) * 30 + Math.random() * 20;
      const target = 120;
      data.push({ hour, glucose, target });
    }
    return data;
  }

  const handleLogGlucose = () => {
    if (glucoseInput) {
      const now = new Date();
      const newReading = {
        hour: now.getHours(),
        glucose: parseFloat(glucoseInput),
        target: 120,
        manual: true,
      };
      setGlucoseData([...glucoseData, newReading]);
      setGlucoseInput('');
    }
  };

  const currentReading = glucoseData[glucoseData.length - 1];
  const glucoseTrend = currentReading.glucose > glucoseData[glucoseData.length - 2]?.glucose ? 'rising' : 'falling';

  return (
    <ScrollView style={styles.container}>
      {/* Current Reading */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.currentReadingHeader}>
            <View>
              <Text style={styles.sectionTitle}>Current Reading</Text>
              <Text style={styles.lastUpdated}>Updated just now</Text>
            </View>
            <View style={styles.currentValueContainer}>
              <Text style={styles.currentValue}>
                {currentReading?.glucose.toFixed(1)}
              </Text>
              <Text style={styles.currentUnit}>mg/dL</Text>
            </View>
          </View>

          <View style={styles.trendContainer}>
            {glucoseTrend === 'rising' ? (
              <TrendingUp size={20} color="#ff4757" />
            ) : (
              <TrendingDown size={20} color="#2ed573" />
            )}
            <Text style={[styles.trendText, { color: glucoseTrend === 'rising' ? '#ff4757' : '#2ed573' }]}>
              {glucoseTrend === 'rising' ? 'Rising' : 'Falling'}
            </Text>
          </View>
        </Card.Content>
      </Card>

      {/* Time Range Selector */}
      <Card style={styles.card}>
        <Card.Content>
          <Text style={styles.sectionTitle}>Time Range</Text>
          <View style={styles.timeRangeContainer}>
            {['6h', '12h', '24h', '3d', '1w'].map((range) => (
              <TouchableOpacity
                key={range}
                style={[styles.timeRangeButton, timeRange === range && styles.timeRangeActive]}
                onPress={() => setTimeRange(range)}
              >
                <Text style={[styles.timeRangeText, timeRange === range && styles.timeRangeActiveText]}>
                  {range}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </Card.Content>
      </Card>

      {/* Glucose Chart */}
      <Card style={styles.card}>
        <Card.Content>
          <Text style={styles.sectionTitle}>Glucose Trends</Text>
          <View style={styles.chartContainer}>
            <VictoryChart theme={VictoryTheme.material} height={250}>
              <VictoryAxis
                style={{
                  axis: { stroke: '#ccc' },
                  tickLabels: { fontSize: 10, padding: 5 },
                }}
              />
              <VictoryAxis
                dependentAxis
                style={{
                  axis: { stroke: '#ccc' },
                  tickLabels: { fontSize: 10, padding: 5 },
                }}
              />
              <VictoryLine
                data={glucoseData}
                x="hour"
                y="glucose"
                style={{
                  data: { stroke: '#0066cc', strokeWidth: 3 },
                }}
              />
              <VictoryLine
                data={glucoseData}
                x="hour"
                y="target"
                style={{
                  data: { stroke: '#00c9a7', strokeWidth: 2, strokeDasharray: '5,5' },
                }}
              />
              <VictoryScatter
                data={glucoseData.filter(d => d.manual)}
                x="hour"
                y="glucose"
                size={5}
                style={{ data: { fill: '#ff4757' } }}
              />
            </VictoryChart>
          </View>
        </Card.Content>
      </Card>

      {/* Log Manual Reading */}
      <Card style={styles.card}>
        <Card.Content>
          <Text style={styles.sectionTitle}>Log Manual Reading</Text>
          <View style={styles.inputContainer}>
            <TextInput
              mode="outlined"
              style={styles.input}
              keyboardType="numeric"
              value={glucoseInput}
              onChangeText={setGlucoseInput}
              placeholder="Enter glucose value"
              outlineColor="#0066cc"
              activeOutlineColor="#0066cc"
            />
            <Button
              mode="contained"
              style={styles.logButton}
              onPress={handleLogGlucose}
              disabled={!glucoseInput}
            >
              Log
            </Button>
          </View>
          <View style={styles.historyContainer}>
            <Text style={styles.historyTitle}>Recent Readings</Text>
            {glucoseData.slice(-3).reverse().map((reading, index) => (
              <View key={index} style={styles.historyItem}>
                <View style={styles.historyTime}>
                  <Clock size={14} color="#666" />
                  <Text style={styles.historyTimeText}>
                    {reading.hour}:00
                  </Text>
                </View>
                <Text style={[
                  styles.historyValue,
                  { color: reading.glucose > 180 ? '#ff4757' : reading.glucose < 70 ? '#ffa502' : '#2ed573' }
                ]}>
                  {reading.glucose.toFixed(1)} mg/dL
                </Text>
              </View>
            ))}
          </View>
        </Card.Content>
      </Card>

      {/* Statistics */}
      <Card style={styles.card}>
        <Card.Content>
          <Text style={styles.sectionTitle}>Statistics</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>
                {glucoseData.reduce((sum, d) => sum + d.glucose, 0) / glucoseData.length}
              </Text>
              <Text style={styles.statLabel}>Average</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>
                {Math.max(...glucoseData.map(d => d.glucose))}
              </Text>
              <Text style={styles.statLabel}>Peak</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>
                {glucoseData.filter(d => d.glucose > 180).length}
              </Text>
              <Text style={styles.statLabel}>High Spikes</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>
                {glucoseData.filter(d => d.glucose < 70).length}
              </Text>
              <Text style={styles.statLabel}>Low Spikes</Text>
            </View>
          </View>
        </Card.Content>
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  card: {
    margin: 16,
    elevation: 2,
  },
  currentReadingHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  lastUpdated: {
    fontSize: 12,
    color: '#999',
  },
  currentValueContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  currentValue: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#0066cc',
  },
  currentUnit: {
    fontSize: 16,
    color: '#666',
    marginLeft: 4,
  },
  trendContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  trendText: {
    marginLeft: 8,
    fontSize: 16,
    fontWeight: '500',
  },
  timeRangeContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  timeRangeButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    backgroundColor: '#e0e0e0',
  },
  timeRangeActive: {
    backgroundColor: '#0066cc',
  },
  timeRangeText: {
    fontSize: 14,
    color: '#666',
  },
  timeRangeActiveText: {
    color: '#fff',
  },
  chartContainer: {
    marginTop: 16,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
  },
  input: {
    flex: 1,
    marginRight: 12,
  },
  logButton: {
    backgroundColor: '#0066cc',
  },
  historyContainer: {
    marginTop: 16,
  },
  historyTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  historyItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  historyTime: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  historyTimeText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#666',
  },
  historyValue: {
    fontSize: 16,
    fontWeight: '500',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  statItem: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#0066cc',
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
});

export default GlucoseScreen;
