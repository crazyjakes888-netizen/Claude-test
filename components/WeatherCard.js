import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

// Map WMO weather interpretation codes to emoji + description
const getWeatherInfo = (code) => {
  if (code === 0) return { emoji: '☀️', label: 'Clear Sky' };
  if (code === 1) return { emoji: '🌤️', label: 'Mainly Clear' };
  if (code === 2) return { emoji: '⛅', label: 'Partly Cloudy' };
  if (code === 3) return { emoji: '☁️', label: 'Overcast' };
  if (code >= 45 && code <= 48) return { emoji: '🌫️', label: 'Foggy' };
  if (code >= 51 && code <= 55) return { emoji: '🌦️', label: 'Drizzle' };
  if (code >= 61 && code <= 65) return { emoji: '🌧️', label: 'Rain' };
  if (code >= 71 && code <= 75) return { emoji: '❄️', label: 'Snow' };
  if (code >= 80 && code <= 82) return { emoji: '🌨️', label: 'Rain Showers' };
  if (code >= 95 && code <= 99) return { emoji: '⛈️', label: 'Thunderstorm' };
  return { emoji: '🌡️', label: 'Unknown' };
};

const getGradientColors = (code) => {
  if (code === 0 || code === 1) return ['#FF9500', '#FFD700'];   // sunny
  if (code === 2 || code === 3) return ['#636e72', '#b2bec3'];   // cloudy
  if (code >= 45 && code <= 48) return ['#74b9ff', '#a29bfe'];   // fog
  if (code >= 51 && code <= 65) return ['#0984e3', '#74b9ff'];   // rain
  if (code >= 71 && code <= 77) return ['#74b9ff', '#dfe6e9'];   // snow
  if (code >= 80 && code <= 82) return ['#0984e3', '#636e72'];   // showers
  if (code >= 95) return ['#2d3436', '#636e72'];                  // storm
  return ['#0984e3', '#74b9ff'];
};

export default function WeatherCard({ weather, loading, error }) {
  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#0984e3" />
        <Text style={styles.loadingText}>Fetching weather…</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorEmoji}>⚠️</Text>
        <Text style={styles.errorText}>{error}</Text>
      </View>
    );
  }

  if (!weather) return null;

  const { temperature, windspeed, weathercode } = weather;
  const { emoji, label } = getWeatherInfo(weathercode);
  const gradientColors = getGradientColors(weathercode);

  return (
    <LinearGradient
      colors={gradientColors}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.card}
    >
      {/* Location */}
      <View style={styles.locationRow}>
        <Text style={styles.locationPin}>📍</Text>
        <Text style={styles.locationText}>New York, NY</Text>
      </View>

      {/* Main temperature */}
      <View style={styles.mainRow}>
        <Text style={styles.weatherEmoji}>{emoji}</Text>
        <Text style={styles.temperature}>{Math.round(temperature)}°F</Text>
      </View>

      {/* Condition label */}
      <Text style={styles.conditionLabel}>{label}</Text>

      {/* Details row */}
      <View style={styles.detailsRow}>
        <View style={styles.detailItem}>
          <Text style={styles.detailEmoji}>💨</Text>
          <Text style={styles.detailValue}>{Math.round(windspeed)} mph</Text>
          <Text style={styles.detailLabel}>Wind</Text>
        </View>
        <View style={styles.detailDivider} />
        <View style={styles.detailItem}>
          <Text style={styles.detailEmoji}>🌡️</Text>
          <Text style={styles.detailValue}>{Math.round((temperature - 32) * 5 / 9)}°C</Text>
          <Text style={styles.detailLabel}>Celsius</Text>
        </View>
        <View style={styles.detailDivider} />
        <View style={styles.detailItem}>
          <Text style={styles.detailEmoji}>🕐</Text>
          <Text style={styles.detailValue}>Now</Text>
          <Text style={styles.detailLabel}>Updated</Text>
        </View>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 20,
    padding: 24,
    marginHorizontal: 16,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.2,
    shadowRadius: 16,
    elevation: 10,
  },
  loadingContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 48,
    marginHorizontal: 16,
    backgroundColor: '#f0f4ff',
    borderRadius: 20,
    marginBottom: 8,
  },
  loadingText: {
    marginTop: 12,
    color: '#636e72',
    fontSize: 15,
    fontWeight: '500',
  },
  errorContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 40,
    marginHorizontal: 16,
    backgroundColor: '#fff5f5',
    borderRadius: 20,
    marginBottom: 8,
  },
  errorEmoji: {
    fontSize: 36,
    marginBottom: 8,
  },
  errorText: {
    color: '#e17055',
    fontSize: 14,
    textAlign: 'center',
    paddingHorizontal: 16,
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  locationPin: {
    fontSize: 14,
    marginRight: 4,
  },
  locationText: {
    color: 'rgba(255,255,255,0.9)',
    fontSize: 16,
    fontWeight: '600',
    letterSpacing: 0.3,
  },
  mainRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  weatherEmoji: {
    fontSize: 56,
    marginRight: 16,
  },
  temperature: {
    fontSize: 72,
    fontWeight: '700',
    color: '#fff',
    letterSpacing: -2,
    lineHeight: 80,
  },
  conditionLabel: {
    color: 'rgba(255,255,255,0.85)',
    fontSize: 20,
    fontWeight: '500',
    marginBottom: 24,
    marginLeft: 4,
  },
  detailsRow: {
    flexDirection: 'row',
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 14,
    paddingVertical: 14,
    paddingHorizontal: 8,
  },
  detailItem: {
    flex: 1,
    alignItems: 'center',
  },
  detailDivider: {
    width: 1,
    backgroundColor: 'rgba(255,255,255,0.35)',
    marginVertical: 4,
  },
  detailEmoji: {
    fontSize: 20,
    marginBottom: 4,
  },
  detailValue: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },
  detailLabel: {
    color: 'rgba(255,255,255,0.75)',
    fontSize: 12,
    marginTop: 2,
    fontWeight: '500',
  },
});
