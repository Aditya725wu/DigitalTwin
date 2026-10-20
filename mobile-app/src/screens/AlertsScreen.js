import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
} from 'react-native';
import { Card, Title, Paragraph, Button, Badge } from 'react-native-paper';
import { Bell, AlertTriangle, Info, CheckCircle, Clock } from 'lucide-react-native';
import apiClient from '../services/api';

const AlertsScreen = () => {
  const [alerts, setAlerts] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      const response = await apiClient.get('/api/alerts');
      setAlerts(response.data);
    } catch (error) {
      setAlerts([]);
      console.error(error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadAlerts();
    setRefreshing(false);
  };

  const acknowledgeAlert = async (alertId) => {
    try {
      await apiClient.post(`/api/alerts/${alertId}/acknowledge`);
      setAlerts(alerts.map(a =>
        a.alert_id === alertId ? { ...a, acknowledged: true } : a
      ));
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  };

  const getAlertIcon = (severity) => {
    switch (severity) {
      case 'HIGH':
      case 'CRITICAL':
        return <AlertTriangle size={24} color="#ff4757" />;
      case 'MEDIUM':
        return <Bell size={24} color="#ffa502" />;
      default:
        return <Info size={24} color="#2ed573" />;
    }
  };

  const getAlertColor = (severity) => {
    switch (severity) {
      case 'HIGH':
      case 'CRITICAL':
        return '#ff4757';
      case 'MEDIUM':
        return '#ffa502';
      default:
        return '#2ed573';
    }
  };

  const getTimeAgo = (timestamp) => {
    const now = new Date();
    const then = new Date(timestamp);
    const diff = Math.floor((now - then) / 60000);
    if (diff < 60) return `${diff} min ago`;
    if (diff < 1440) return `${Math.floor(diff / 60)} hours ago`;
    return `${Math.floor(diff / 1440)} days ago`;
  };

  const unreadCount = alerts.filter(a => !a.acknowledged).length;

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <Title style={styles.headerTitle}>Alerts</Title>
        {unreadCount > 0 && (
          <Badge style={styles.badge}>{unreadCount}</Badge>
        )}
      </View>

      {/* Alert List */}
      {alerts.length === 0 ? (
        <Card style={styles.emptyCard}>
          <Card.Content>
            <CheckCircle size={48} color="#2ed573" style={styles.emptyIcon} />
            <Text style={styles.emptyText}>No alerts</Text>
            <Paragraph style={styles.emptySubtext}>
              You're all caught up!
            </Paragraph>
          </Card.Content>
        </Card>
      ) : (
        alerts.map((alert) => (
          <Card
            key={alert.alert_id}
            style={[
              styles.card,
              alert.acknowledged && styles.acknowledgedCard,
            ]}
          >
            <Card.Content>
              <View style={styles.alertHeader}>
                {getAlertIcon(alert.severity)}
                <View style={styles.alertInfo}>
                  <Text style={[styles.alertSeverity, { color: getAlertColor(alert.severity) }]}>
                    {alert.severity}
                  </Text>
                  <View style={styles.alertTime}>
                    <Clock size={12} color="#999" />
                    <Text style={styles.alertTimestamp}>
                      {getTimeAgo(alert.timestamp)}
                    </Text>
                  </View>
                </View>
              </View>

              <Paragraph style={styles.alertMessage}>
                {alert.message}
              </Paragraph>

              {!alert.acknowledged && (
                <Button
                  mode="contained"
                  style={styles.acknowledgeButton}
                  onPress={() => acknowledgeAlert(alert.alert_id)}
                >
                  Acknowledge
                </Button>
              )}

              {alert.acknowledged && (
                <View style={styles.acknowledgedBadge}>
                  <CheckCircle size={14} color="#2ed573" />
                  <Text style={styles.acknowledgedText}>Acknowledged</Text>
                </View>
              )}
            </Card.Content>
          </Card>
        ))
      )}

      {/* Summary */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.summaryTitle}>Alert Summary</Title>
          <View style={styles.summaryRow}>
            <View style={styles.summaryItem}>
              <Text style={[styles.summaryValue, { color: '#ff4757' }]}>
                {alerts.filter(a => a.severity === 'HIGH' || a.severity === 'CRITICAL').length}
              </Text>
              <Text style={styles.summaryLabel}>High</Text>
            </View>
            <View style={styles.summaryItem}>
              <Text style={[styles.summaryValue, { color: '#ffa502' }]}>
                {alerts.filter(a => a.severity === 'MEDIUM').length}
              </Text>
              <Text style={styles.summaryLabel}>Medium</Text>
            </View>
            <View style={styles.summaryItem}>
              <Text style={[styles.summaryValue, { color: '#2ed573' }]}>
                {alerts.filter(a => a.severity === 'LOW').length}
              </Text>
              <Text style={styles.summaryLabel}>Low</Text>
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
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  badge: {
    backgroundColor: '#ff4757',
  },
  card: {
    margin: 16,
    marginTop: 0,
    elevation: 2,
  },
  acknowledgedCard: {
    opacity: 0.7,
  },
  emptyCard: {
    margin: 16,
    alignItems: 'center',
  },
  emptyIcon: {
    marginBottom: 16,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  emptySubtext: {
    color: '#666',
  },
  alertHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  alertInfo: {
    marginLeft: 12,
    flex: 1,
  },
  alertSeverity: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  alertTime: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  alertTimestamp: {
    fontSize: 12,
    color: '#999',
    marginLeft: 4,
  },
  alertMessage: {
    fontSize: 16,
    color: '#333',
    marginBottom: 12,
  },
  acknowledgeButton: {
    backgroundColor: '#0066cc',
  },
  acknowledgedBadge: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  acknowledgedText: {
    marginLeft: 4,
    color: '#2ed573',
    fontSize: 14,
  },
  summaryTitle: {
    fontSize: 18,
    marginBottom: 16,
    color: '#333',
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  summaryItem: {
    alignItems: 'center',
  },
  summaryValue: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  summaryLabel: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
});

export default AlertsScreen;