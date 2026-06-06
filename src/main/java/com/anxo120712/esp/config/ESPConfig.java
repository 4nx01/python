package com.anxo120712.esp.config;

import java.util.HashMap;
import java.util.Map;

/**
 * Configuration for ESP features
 */
public class ESPConfig {
    public static final double ESP_RENDER_DISTANCE = 128.0;
    public static final double SPAWNER_RENDER_DISTANCE = 256.0;
    public static final double ANOMALY_SCAN_RADIUS = 256.0;

    private static final Map<String, Boolean> features = new HashMap<>();

    static {
        features.put("chest_esp", true);
        features.put("spawner_esp", true);
        features.put("anomaly_detection", true);
        features.put("shulker_detection", true);
        features.put("player_activity", true);
        features.put("chest_clusters", true);
        features.put("suspicious_entities", true);
        features.put("chunk_marking", true);
    }

    public static boolean isEnabled(String feature) {
        return features.getOrDefault(feature, false);
    }

    public static void setEnabled(String feature, boolean enabled) {
        features.put(feature, enabled);
    }

    public static void toggleFeature(String feature) {
        features.put(feature, !features.getOrDefault(feature, false));
    }

    public static Map<String, Boolean> getAllFeatures() {
        return new HashMap<>(features);
    }
}
