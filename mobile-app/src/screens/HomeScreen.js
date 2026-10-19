import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
} from 'react-native';
import { Card, Title, Paragraph, Button, ProgressBar } from 'react-native-paper';
import { Heart, AlertCircle, TrendingUp, Shield } from 'lucide-react-native';
import apiClient from '../services/api';

const HomeScreen = () => {
  const [glucose, setGlucose] = useState(145);
  const [glucoseStatus, setGlucoseStatus] = useState('Normal');
  const [riskScore, setRiskScore] = useState(0.65);
  const [refreshing, setRefreshing] = useState(false);
  const [lastSync, setLastSync] = useState(new Date());

  const onRefresh = async () => {
    setRefreshing(true);
    // Fetch latest data
    await new Promise(resolve => setTimeout(resolve, 1000));
    setRefreshing(false);
    setLastSync(new Date());
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      // Fetch patient data
      const response = await apiClient.get('/api/patients/current');
      if (response.data) {
        setGlucose(response.data.last_glucose || 145);
        setRiskScore(response.data.risk_score || 0.65);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const getGlucoseStatus = (value) => {
    if (value < 70) return 'Low';
    if (value > 180) return 'High';
    return 'Normal';
  };

  const getRiskLevel = (score) => {
    if (score > 0.8) return 'High';
    if (score > 0.5) return 'Medium';
    return 'Low';
  };

  const statusColor = glucoseStatus === 'Normal' ? '#2ed573' : glucoseStatus === 'High' ? '#ff4757' : '#ffa502';
  const riskLevel = getRiskLevel(riskScore);
  const riskColor = riskLevel === 'High' ? '#ff4757' : riskLevel === 'Medium' ? '#ffa502' : '#2ed573';

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Welcome Card */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.title}>Welcome Back!</Title>
          <Paragraph style={styles.subtitle}>
            Your health is being monitored 24/7
          </Paragraph>
          <Text style={styles.lastSync}>
            Last sync: {lastSync.toLocaleTimeString()}
          </Text>
        </Card.Content>
      </Card>

      {/* Current Status */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.statusHeader}>
            <Heart size={24} color={statusColor} />
            <Title style={styles.statusTitle}>Current Glucose</Title>
          </View>
          <View style={styles.glucoseDisplay}>
            <Text style={[styles.glucoseValue, { color: statusColor }]}>{glucose}</Text>
            <Text style={styles.glucoseUnit}>mg/dL</Text>
          </View>
          <Text style={[styles.statusText, { color: statusColor }]}>
            Status: {glucoseStatus}
          </Text>
          <ProgressBar
            progress={Math.min(glucose / 250, 1)}
            color={statusColor}
            style={styles.progressBar}
          />
        </Card.Content>
      </Card>

      {/* Risk Assessment */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.statusHeader}>
            <Shield size={24} color={riskColor} />
            <Title style={styles.statusTitle}>Risk Assessment</Title>
          </View>
          <View style={styles.riskContainer}>
            <Text style={[styles.riskScore, { color: riskColor }]}>
              {Math.round(riskScore * 100)}%
            </Text>
            <Text style={[styles.riskLevel, { color: riskColor }]}>
              {riskLevel} Risk
            </Text>
          </View>
          <View style={styles.riskIndicators}>
            <View style={[styles.riskIndicator, riskLevel === 'Low' && styles.activeRisk]}>
              <Text style={styles.riskText}>Low</Text>
            </View>
            <View style={[styles.riskIndicator, riskLevel === 'Medium' && styles.activeRisk]}>
              <Text style={styles.riskText}>Medium</Text>
            </View>
            <View style={[styles.riskIndicator, riskLevel === 'High' && styles.activeRisk]}>
              <Text style={styles.riskText}>High</Text>
            </View>
          </View>
        </Card.Content>
      </Card>

      {/* Quick Actions */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.actionTitle}>Quick Actions</Title>
          <View style={styles.actionsRow}>
            <Button
              mode="contained"
              style={styles.actionButton}
              onPress={() => console.log('Log Glucose')}
            >
              Log Glucose
            </Button>
            <Button
              mode="outlined"
              style={styles.actionButton}
              onPress={() => console.log('View Trends')}
            >
              View Trends
            </Button>
          </View>
          <View style={styles.actionsRow}>
            <Button
              mode="outlined"
              style={styles.actionButton}
              onPress={() => console.log('Medication')}
            >
              Medication
            </Button>
            <Button
              mode="outlined"
              style={styles.actionButton}
              onPress={() => console.log('Contact Doctor')}
            >
              Contact Doctor
            </Button>
          </View>
        </Card.Content>
      </Card>

      {/* Prediction Card */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.statusHeader}>
            <TrendingUp size={24} color="#0066cc" />
            <Title style={styles.statusTitle}>Prediction</Title>
          </View>
          <Paragraph style={styles.predictionText}>
            Based on your recent data, the next 2 hours are predicted to be:
          </Paragraph>
          <Text style={styles.predictionOutcome}>Stable Glucose</Text>
          <Paragraph style={styles.predictionConfidence}>
            Confidence: 85%
          </Paragraph>
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
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#0066cc',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginTop: 4,
  },
  lastSync: {
    fontSize: 12,
    color: '#999',
    marginTop: 8,
  },
  statusHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  statusTitle: {
    marginLeft: 12,
    fontSize: 18,
    color: '#333',
  },
  glucoseDisplay: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginBottom: 8,
  },
  glucoseValue: {
    fontSize: 48,
    fontWeight: 'bold',
  },
  glucoseUnit: {
    fontSize: 20,
    color: '#666',
    marginLeft: 8,
  },
  statusText: {
    fontSize: 16,
    marginBottom: 12,
  },
  progressBar: {
    height: 8,
    borderRadius: 4,
    marginTop: 8,
  },
  riskContainer: {
    alignItems: 'center',
    marginVertical: 16,
  },
  riskScore: {
    fontSize: 48,
    fontWeight: 'bold',
  },
  riskLevel: {
    fontSize: 20,
    marginTop: 8,
  },
  riskIndicators: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 16,
  },
  riskIndicator: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#e0e0e0',
  },
  activeRisk: {
    backgroundColor: '#0066cc',
  },
  riskText: {
    color: '#fff',
    fontWeight: '600',
  },
  actionTitle: {
    fontSize: 18,
    marginBottom: 16,
    color: '#333',
  },
  actionsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  actionButton: {
    flex: 1,
    marginHorizontal: 4,
  },
  predictionText: {
    fontSize: 16,
    color: '#666',
    marginBottom: 12,
  },
  predictionOutcome: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#0066cc',
    marginBottom: 8,
  },
  predictionConfidence: {
    fontSize: 14,
    color: '#999',
  },
});

export default HomeScreen;
