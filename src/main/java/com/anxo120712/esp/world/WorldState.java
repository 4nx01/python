package com.anxo120712.esp.world;

import com.anxo120712.esp.data.*;
import net.minecraft.util.math.BlockPos;
import java.util.*;

/**
 * Manages the state of the world (blocks, entities, player position)
 */
public class WorldState {
    private final Map<String, Block> blocks = new HashMap<>();
    private final Map<Integer, Entity> entities = new HashMap<>();
    public Position playerPos = new Position(0, 64, 0);
    public float playerYaw = 0;
    public float playerPitch = 0;

    public void addBlock(BlockPos blockPos, BlockType type, Map<String, Object> metadata) {
        Position pos = new Position(blockPos);
        String key = blockPos.getX() + "," + blockPos.getY() + "," + blockPos.getZ();
        blocks.put(key, new Block(pos, type, metadata));
    }

    public void addBlock(BlockPos blockPos, BlockType type) {
        addBlock(blockPos, type, new HashMap<>());
    }

    public Block getBlock(String key) {
        return blocks.get(key);
    }

    public List<Block> getBlocksByType(BlockType type, double radius) {
        List<Block> result = new ArrayList<>();
        for (Block block : blocks.values()) {
            if (block.blockType == type && block.distanceTo(playerPos) <= radius) {
                result.add(block);
            }
        }
        return result;
    }

    public void addEntity(int entityId, String type, double x, double y, double z, float yaw, float pitch) {
        entities.put(entityId, new Entity(entityId, type, new Position(x, y, z), yaw, pitch));
    }

    public Entity getEntity(int entityId) {
        return entities.get(entityId);
    }

    public List<Entity> getEntitiesByType(String type, double radius) {
        List<Entity> result = new ArrayList<>();
        for (Entity entity : entities.values()) {
            if (entity.entityType.equals(type) && entity.distanceTo(playerPos) <= radius) {
                result.add(entity);
            }
        }
        return result;
    }

    public void updatePlayer(Position pos, float yaw, float pitch) {
        this.playerPos = pos;
        this.playerYaw = yaw;
        this.playerPitch = pitch;
    }

    public void clear() {
        blocks.clear();
        entities.clear();
    }
}
