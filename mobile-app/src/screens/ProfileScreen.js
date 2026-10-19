import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
} from 'react-native';
import { Card, Title, Paragraph, Button, List, Switch, Divider } from 'react-native-paper';
import { User, Settings, Bell, Shield, Moon, HelpCircle, LogOut } from 'lucide-react-native';

const ProfileScreen = () => {
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [alertsEnabled, setAlertsEnabled] = useState(true);

  const patient = {
    name: 'John Doe',
    email: 'john.doe@email.com',
    age: 45,
    gender: 'Male',
    diabetesType: 'Type 2',
    diagnosisDate: '2020-05-15',
    bmi: 27.5,
  };

  return (
    <ScrollView style={styles.container}>
      {/* Profile Header */}
      <Card style={styles.card}>
        <Card.Content style={styles.profileHeader}>
          <View style={styles.avatar}>
            <User size={40} color="#0066cc" />
          </View>
          <Title style={styles.name}>{patient.name}</Title>
          <Paragraph style={styles.email}>{patient.email}</Paragraph>
          <View style={styles.badgeContainer}>
            <View style={styles.badge}>
              <Text style={styles.badgeText}>Type 2 Diabetes</Text>
            </View>
          </View>
        </Card.Content>
      </Card>

      {/* Medical Info */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.sectionTitle}>Medical Information</Title>
          <List.Item
            title="Age"
            description={`${patient.age} years`}
            left={props => <List.Icon {...props} icon="calendar" />}
          />
          <Divider />
          <List.Item
            title="Gender"
            description={patient.gender}
            left={props => <List.Icon {...props} icon="account" />}
          />
          <Divider />
          <List.Item
            title="BMI"
            description={`${patient.bmi}`}
            left={props => <List.Icon {...props} icon="scale-bathroom" />}
          />
          <Divider />
          <List.Item
            title="Diagnosis Date"
            description={patient.diagnosisDate}
            left={props => <List.Icon {...props} icon="calendar-check" />}
          />
          <Divider />
          <List.Item
            title="Diabetes Type"
            description={patient.diabetesType}
            left={props => <List.Icon {...props} icon="medical-bag" />}
          />
        </Card.Content>
      </Card>

      {/* Settings */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.sectionHeader}>
            <Settings size={20} color="#333" />
            <Title style={styles.sectionTitle}>Settings</Title>
          </View>

          <List.Item
            title="Push Notifications"
            description="Receive notifications for alerts"
            left={props => <List.Icon {...props} icon="bell" />}
            right={() => (
              <Switch value={notifications} onValueChange={setNotifications} color="#0066cc" />
            )}
          />
          <Divider />
          <List.Item
            title="Predictive Alerts"
            description="Get predictions before glucose spikes"
            left={props => <List.Icon {...props} icon="bell-alert" />}
            right={() => (
              <Switch value={alertsEnabled} onValueChange={setAlertsEnabled} color="#0066cc" />
            )}
          />
          <Divider />
          <List.Item
            title="Dark Mode"
            description="Use dark theme"
            left={props => <List.Icon {...props} icon="moon-waning-crescent" />}
            right={() => (
              <Switch value={darkMode} onValueChange={setDarkMode} color="#0066cc" />
            )}
          />
        </Card.Content>
      </Card>

      {/* Account */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.sectionTitle}>Account</Title>

          <List.Item
            title="Privacy & Security"
            description="Manage your data and privacy"
            left={props => <List.Icon {...props} icon="shield-account" />}
          />
          <Divider />
          <List.Item
            title="Help & Support"
            description="Get help with the app"
            left={props => <List.Icon {...props} icon="help-circle" />}
          />
          <Divider />
          <List.Item
            title="About"
            description="Version 1.0.0"
            left={props => <List.Icon {...props} icon="information" />}
          />
        </Card.Content>
      </Card>

      {/* Sign Out */}
      <Button
        mode="outlined"
        style={styles.signOutButton}
        textColor="#ff4757"
        onPress={() => console.log('Sign out')}
      >
        Sign Out
      </Button>

      <Text style={styles.version}>DiabetesTwin v1.0.0</Text>
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
    marginTop: 0,
    elevation: 2,
  },
  profileHeader: {
    alignItems: 'center',
    paddingVertical: 16,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#e3f2fd',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  email: {
    color: '#666',
  },
  badgeContainer: {
    marginTop: 12,
  },
  badge: {
    backgroundColor: '#e3f2fd',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  badgeText: {
    color: '#0066cc',
    fontWeight: '600',
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  sectionTitle: {
    marginLeft: 8,
    fontSize: 18,
    color: '#333',
  },
  signOutButton: {
    margin: 16,
    borderColor: '#ff4757',
  },
  version: {
    textAlign: 'center',
    color: '#999',
    marginBottom: 32,
  },
});

export default ProfileScreen;