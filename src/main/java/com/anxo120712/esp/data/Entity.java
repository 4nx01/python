package com.anxo120712.esp.data;

/**
 * Represents an entity in the world
 */
public class Entity {
    public final int entityId;
    public final String entityType;
    public final Position pos;
    public final float yaw;
    public final float pitch;

    public Entity(int entityId, String entityType, Position pos, float yaw, float pitch) {
        this.entityId = entityId;
        this.entityType = entityType;
        this.pos = pos;
        this.yaw = yaw;
        this.pitch = pitch;
    }

    public Entity(int entityId, String entityType, Position pos) {
        this(entityId, entityType, pos, 0, 0);
    }

    public double distanceTo(Position other) {
        return pos.distanceTo(other);
    }

    @Override
    public String toString() {
        return String.format("%s#%d at %s", entityType, entityId, pos);
    }
}
