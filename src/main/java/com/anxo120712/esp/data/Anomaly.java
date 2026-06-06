package com.anxo120712.esp.data;

import java.util.HashMap;
import java.util.Map;

/**
 * Represents a detected anomaly
 */
public class Anomaly implements Comparable<Anomaly> {
    public final AnomalyType type;
    public final int priority;
    public final Position position;
    public final String description;
    public final Map<String, Object> details;

    public Anomaly(AnomalyType type, int priority, Position position, String description) {
        this.type = type;
        this.priority = priority;
        this.position = position;
        this.description = description;
        this.details = new HashMap<>();
    }

    public Anomaly(AnomalyType type, int priority, Position position, String description, Map<String, Object> details) {
        this.type = type;
        this.priority = priority;
        this.position = position;
        this.description = description;
        this.details = details;
    }

    @Override
    public int compareTo(Anomaly other) {
        return Integer.compare(other.priority, this.priority);
    }

    @Override
    public String toString() {
        return String.format("[%s] P%d: %s @ %s", type.displayName, priority, description, position);
    }
}
