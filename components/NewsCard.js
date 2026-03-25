import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Linking,
  Alert,
} from 'react-native';

const categoryColors = {
  Technology: { bg: '#e8f4fd', text: '#0984e3', dot: '#0984e3' },
  Science:    { bg: '#e8fdf4', text: '#00b894', dot: '#00b894' },
  World:      { bg: '#fdf3e8', text: '#e17055', dot: '#e17055' },
  Business:   { bg: '#f3e8fd', text: '#a29bfe', dot: '#6c5ce7' },
  Health:     { bg: '#fde8e8', text: '#d63031', dot: '#d63031' },
  Sports:     { bg: '#e8fde8', text: '#27ae60', dot: '#27ae60' },
};

export default function NewsCard({ article, index }) {
  const [pressed, setPressed] = useState(false);
  const colors = categoryColors[article.category] || categoryColors.World;

  const handlePress = () => {
    if (article.url) {
      Linking.openURL(article.url).catch(() =>
        Alert.alert('Cannot Open Link', 'This link is not available.')
      );
    }
  };

  return (
    <TouchableOpacity
      activeOpacity={0.75}
      onPressIn={() => setPressed(true)}
      onPressOut={() => setPressed(false)}
      onPress={handlePress}
      style={[styles.card, pressed && styles.cardPressed]}
    >
      {/* Left accent bar */}
      <View style={[styles.accentBar, { backgroundColor: colors.dot }]} />

      <View style={styles.content}>
        {/* Top row: category badge + time */}
        <View style={styles.metaRow}>
          <View style={[styles.categoryBadge, { backgroundColor: colors.bg }]}>
            <View style={[styles.categoryDot, { backgroundColor: colors.dot }]} />
            <Text style={[styles.categoryText, { color: colors.text }]}>
              {article.category}
            </Text>
          </View>
          <Text style={styles.timeText}>{article.time}</Text>
        </View>

        {/* Headline */}
        <Text style={styles.headline} numberOfLines={2}>
          {article.title}
        </Text>

        {/* Source row */}
        <View style={styles.sourceRow}>
          <Text style={styles.sourceEmoji}>{article.sourceEmoji}</Text>
          <Text style={styles.sourceName}>{article.source}</Text>
          <Text style={styles.readMore}>Read more →</Text>
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    borderRadius: 16,
    marginHorizontal: 16,
    marginBottom: 12,
    flexDirection: 'row',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.07,
    shadowRadius: 8,
    elevation: 3,
    overflow: 'hidden',
  },
  cardPressed: {
    transform: [{ scale: 0.985 }],
    shadowOpacity: 0.04,
    elevation: 1,
  },
  accentBar: {
    width: 4,
    borderTopLeftRadius: 16,
    borderBottomLeftRadius: 16,
  },
  content: {
    flex: 1,
    padding: 14,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  categoryBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 20,
  },
  categoryDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginRight: 5,
  },
  categoryText: {
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 0.4,
    textTransform: 'uppercase',
  },
  timeText: {
    fontSize: 12,
    color: '#b2bec3',
    fontWeight: '500',
  },
  headline: {
    fontSize: 15,
    fontWeight: '700',
    color: '#2d3436',
    lineHeight: 21,
    marginBottom: 10,
    letterSpacing: 0.1,
  },
  sourceRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sourceEmoji: {
    fontSize: 13,
    marginRight: 5,
  },
  sourceName: {
    fontSize: 12,
    color: '#636e72',
    fontWeight: '600',
    flex: 1,
  },
  readMore: {
    fontSize: 12,
    color: '#0984e3',
    fontWeight: '600',
  },
});
