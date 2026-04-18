import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
} from 'react-native';

const alertSeverityColors = {
  Critical: { bg: '#ffe8e8', text: '#d63031', dot: '#d63031', icon: '🚨' },
  High: { bg: '#fdf3e8', text: '#e17055', dot: '#e17055', icon: '⚠️' },
  Moderate: { bg: '#fff3e8', text: '#fdcb6e', dot: '#fdcb6e', icon: '⚡' },
  Low: { bg: '#e8fdf4', text: '#00b894', dot: '#00b894', icon: 'ℹ️' },
};

export default function WeatherAlertsCard({ alerts = [], loading = false }) {
  const [expanded, setExpanded] = useState({});

  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Loading alerts...</Text>
      </View>
    );
  }

  if (!alerts || alerts.length === 0) {
    return (
      <View style={styles.container}>
        <View style={styles.noAlertsContent}>
          <Text style={styles.noAlertsEmoji}>✅</Text>
          <Text style={styles.noAlertsText}>No active weather alerts</Text>
        </View>
      </View>
    );
  }

  const toggleExpanded = (id) => {
    setExpanded((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const renderAlert = ({ item }) => {
    const severityColor = alertSeverityColors[item.severity] || alertSeverityColors.Low;
    const isExpanded = expanded[item.id];

    return (
      <TouchableOpacity
        activeOpacity={0.7}
        onPress={() => toggleExpanded(item.id)}
        style={[styles.alertCard, { borderLeftColor: severityColor.dot }]}
      >
        <View style={styles.alertHeader}>
          <View style={styles.headerLeft}>
            <Text style={styles.severityIcon}>{severityColor.icon}</Text>
            <View style={styles.headerText}>
              <Text style={styles.alertType} numberOfLines={1}>
                {item.type}
              </Text>
              <Text style={styles.alertLocation}>{item.location}</Text>
            </View>
          </View>
          <View style={[styles.severityBadge, { backgroundColor: severityColor.bg }]}>
            <Text style={[styles.severityLabel, { color: severityColor.text }]}>
              {item.severity}
            </Text>
          </View>
        </View>

        {isExpanded && (
          <View style={styles.alertDetails}>
            <Text style={styles.alertDescription}>{item.description}</Text>
            <Text style={styles.alertTime}>{item.time}</Text>
          </View>
        )}
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      <FlatList
        data={alerts}
        renderItem={renderAlert}
        keyExtractor={(item) => item.id}
        scrollEnabled={false}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginHorizontal: 16,
    marginBottom: 12,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.07,
    shadowRadius: 8,
    elevation: 3,
  },
  loadingText: {
    padding: 16,
    textAlign: 'center',
    color: '#636e72',
    fontSize: 14,
  },
  noAlertsContent: {
    padding: 20,
    alignItems: 'center',
  },
  noAlertsEmoji: {
    fontSize: 40,
    marginBottom: 8,
  },
  noAlertsText: {
    fontSize: 14,
    color: '#636e72',
    fontWeight: '500',
  },
  alertCard: {
    borderLeftWidth: 5,
    padding: 14,
  },
  alertHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  severityIcon: {
    fontSize: 18,
    marginRight: 10,
  },
  headerText: {
    flex: 1,
  },
  alertType: {
    fontSize: 15,
    fontWeight: '700',
    color: '#2d3436',
    marginBottom: 3,
  },
  alertLocation: {
    fontSize: 12,
    color: '#636e72',
  },
  severityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    marginLeft: 10,
  },
  severityLabel: {
    fontSize: 11,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  alertDetails: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  alertDescription: {
    fontSize: 13,
    color: '#2d3436',
    lineHeight: 18,
    marginBottom: 8,
  },
  alertTime: {
    fontSize: 11,
    color: '#b2bec3',
    fontWeight: '500',
  },
  separator: {
    height: 1,
    backgroundColor: '#f0f0f0',
  },
});
