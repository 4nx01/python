package com.anxo120712.esp.data;

import java.util.HashMap;
import java.util.Map;

/**
 * Represents a block in the world
 */
public class Block {
    public final Position pos;
    public final BlockType blockType;
    public final Map<String, Object> metadata;

    public Block(Position pos, BlockType blockType) {
        this.pos = pos;
        this.blockType = blockType;
        this.metadata = new HashMap<>();
    }

    public Block(Position pos, BlockType blockType, Map<String, Object> metadata) {
        this.pos = pos;
        this.blockType = blockType;
        this.metadata = metadata;
    }

    public double distanceTo(Position other) {
        return pos.distanceTo(other);
    }

    @Override
    public String toString() {
        return String.format("%s at %s", blockType, pos);
    }
}
