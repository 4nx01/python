package com.anxo120712.esp.data;

/**
 * Types of anomalies that can be detected
 */
public enum AnomalyType {
    SHULKER_BOX("Shulker Box", 0xFF3232),
    PLAYER_ACTIVITY("Player Activity", 0xFF9600),
    CHEST_CLUSTER("Chest Cluster", 0xFFFF00),
    SUSPICIOUS_ENTITY("Suspicious Entity", 0xFF00FF),
    SPAWNER("Spawner", 0xFF00FF);

    public final String displayName;
    public final int color;

    AnomalyType(String displayName, int color) {
        this.displayName = displayName;
        this.color = color;
    }

    public int getR() {
        return (color >> 16) & 0xFF;
    }

    public int getG() {
        return (color >> 8) & 0xFF;
    }

    public int getB() {
        return color & 0xFF;
    }
}
