import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  SafeAreaView,
  Platform,
  StatusBar as RNStatusBar,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { LinearGradient } from 'expo-linear-gradient';
import WeatherCard from './components/WeatherCard';
import NewsCard from './components/NewsCard';

// ---------------------------------------------------------------------------
// Mock news data (realistic headlines — replace with a live API if desired)
// ---------------------------------------------------------------------------
const MOCK_NEWS = [
  {
    id: '1',
    title: 'Scientists Discover New Earth-Like Exoplanet Just 40 Light-Years Away',
    source: 'NASA Science',
    sourceEmoji: '🚀',
    category: 'Science',
    time: '12 min ago',
    url: 'https://science.nasa.gov',
  },
  {
    id: '2',
    title: 'Apple Announces Major iOS 18 Update With AI Features Built Into Every App',
    source: 'The Verge',
    sourceEmoji: '📱',
    category: 'Technology',
    time: '34 min ago',
    url: 'https://theverge.com',
  },
  {
    id: '3',
    title: 'Global Markets Rally as Inflation Data Comes in Below Expectations',
    source: 'Financial Times',
    sourceEmoji: '📈',
    category: 'Business',
    time: '1 hr ago',
    url: 'https://ft.com',
  },
  {
    id: '4',
    title: 'Study Finds Mediterranean Diet Reduces Risk of Heart Disease by 30%',
    source: 'Harvard Health',
    sourceEmoji: '🫀',
    category: 'Health',
    time: '2 hrs ago',
    url: 'https://health.harvard.edu',
  },
  {
    id: '5',
    title: 'Record-Breaking Athlete Shatters 100m World Record at World Championships',
    source: 'ESPN',
    sourceEmoji: '🏅',
    category: 'Sports',
    time: '3 hrs ago',
    url: 'https://espn.com',
  },
  {
    id: '6',
    title: 'UN Climate Summit Reaches Historic Agreement on Carbon Emissions',
    source: 'Reuters',
    sourceEmoji: '🌍',
    category: 'World',
    time: '4 hrs ago',
    url: 'https://reuters.com',
  },
];

// ---------------------------------------------------------------------------
// Open-Meteo API  (free, no key required)
// Coordinates: New York City
// ---------------------------------------------------------------------------
const WEATHER_URL =
  'https://api.open-meteo.com/v1/forecast' +
  '?latitude=40.7128&longitude=-74.0060' +
  '&current=temperature_2m,weathercode,windspeed_10m' +
  '&temperature_unit=fahrenheit' +
  '&wind_speed_unit=mph';

export default function App() {
  const [weather, setWeather]         = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(true);
  const [weatherError, setWeatherError]     = useState(null);
  const [refreshing, setRefreshing]         = useState(false);

  // Format the current date nicely
  const today = new Date();
  const dateString = today.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });

  const fetchWeather = useCallback(async () => {
    try {
      setWeatherError(null);
      const response = await fetch(WEATHER_URL);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      const current = data.current;
      setWeather({
        temperature: current.temperature_2m,
        weathercode: current.weathercode,
        windspeed:   current.windspeed_10m,
      });
    } catch (err) {
      console.warn('Weather fetch failed:', err.message);
      setWeatherError('Could not load weather. Check your connection.');
    } finally {
      setWeatherLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWeather();
  }, [fetchWeather]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    setWeatherLoading(true);
    await fetchWeather();
    // Simulate a brief news refresh pause for UX polish
    await new Promise((r) => setTimeout(r, 600));
    setRefreshing(false);
  }, [fetchWeather]);

  return (
    <View style={styles.root}>
      <StatusBar style="light" />

      {/* ── Header gradient ── */}
      <LinearGradient
        colors={['#1a1a2e', '#16213e']}
        style={styles.header}
      >
        <SafeAreaView>
          <View style={styles.headerContent}>
            <View>
              <Text style={styles.headerTitle}>Weather & News</Text>
              <Text style={styles.headerDate}>{dateString}</Text>
            </View>
            <Text style={styles.headerEmoji}>⛅</Text>
          </View>
        </SafeAreaView>
      </LinearGradient>

      {/* ── Scrollable body ── */}
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor="#0984e3"
            title="Refreshing…"
            titleColor="#636e72"
          />
        }
      >
        {/* ── Weather section ── */}
        <SectionHeader emoji="🌤️" title="Current Weather" />
        <WeatherCard
          weather={weather}
          loading={weatherLoading}
          error={weatherError}
        />

        {/* ── News section ── */}
        <SectionHeader emoji="📰" title="Top Headlines" subtitle="Tap a card to read more" />
        {MOCK_NEWS.map((article, i) => (
          <NewsCard key={article.id} article={article} index={i} />
        ))}

        {/* Bottom padding */}
        <View style={styles.bottomPad} />
      </ScrollView>
    </View>
  );
}

// ---------------------------------------------------------------------------
// Reusable section header
// ---------------------------------------------------------------------------
function SectionHeader({ emoji, title, subtitle }) {
  return (
    <View style={styles.sectionHeader}>
      <View style={styles.sectionTitleRow}>
        <Text style={styles.sectionEmoji}>{emoji}</Text>
        <Text style={styles.sectionTitle}>{title}</Text>
      </View>
      {subtitle ? (
        <Text style={styles.sectionSubtitle}>{subtitle}</Text>
      ) : null}
    </View>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------
const STATUSBAR_HEIGHT =
  Platform.OS === 'android' ? RNStatusBar.currentHeight ?? 0 : 0;

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#f0f4f8',
  },

  // Header
  header: {
    paddingTop: STATUSBAR_HEIGHT,
    paddingBottom: 0,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '800',
    color: '#fff',
    letterSpacing: -0.5,
  },
  headerDate: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.6)',
    marginTop: 2,
    fontWeight: '500',
  },
  headerEmoji: {
    fontSize: 40,
  },

  // Scroll
  scroll: {
    flex: 1,
  },
  scrollContent: {
    paddingTop: 24,
  },
  bottomPad: {
    height: 40,
  },

  // Section headers
  sectionHeader: {
    paddingHorizontal: 20,
    marginBottom: 12,
    marginTop: 8,
  },
  sectionTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sectionEmoji: {
    fontSize: 20,
    marginRight: 8,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#2d3436',
    letterSpacing: -0.3,
  },
  sectionSubtitle: {
    fontSize: 13,
    color: '#b2bec3',
    marginTop: 3,
    marginLeft: 30,
    fontWeight: '500',
  },
});
