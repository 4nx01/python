package com.anxo120712.esp.detection;

import com.anxo120712.esp.data.*;
import com.anxo120712.esp.world.WorldState;
import java.util.*;

/**
 * Detects anomalies in the game world
 */
public class AnomalyDetector {
    private final WorldState world;

    public AnomalyDetector(WorldState world) {
        this.world = world;
    }

    public List<Anomaly> scan(double radius) {
        List<Anomaly> detected = new ArrayList<>();
        detected.addAll(detectSpawners(radius));
        detected.addAll(detectShulkerBoxes(radius));
        detected.addAll(detectPlayerActivity(radius));
        detected.addAll(detectChestClusters(radius));
        detected.sort(Comparator.reverseOrder());
        return detected;
    }

    private List<Anomaly> detectSpawners(double radius) {
        List<Anomaly> result = new ArrayList<>();
        List<Block> spawnerBlocks = world.getBlocksByType(BlockType.SPAWNER, radius);
        for (Block block : spawnerBlocks) {
            String mobType = (String) block.metadata.getOrDefault("spawn_type", "UNKNOWN");
            Anomaly anomaly = new Anomaly(
                AnomalyType.SPAWNER,
                10,
                block.pos,
                "Spawner detected: " + mobType
            );
            anomaly.details.put("mob_type", mobType);
            result.add(anomaly);
        }
        return result;
    }

    private List<Anomaly> detectShulkerBoxes(double radius) {
        List<Anomaly> result = new ArrayList<>();
        List<Block> shulkerBlocks = world.getBlocksByType(BlockType.SHULKER_BOX, radius);
        for (Block block : shulkerBlocks) {
            Anomaly anomaly = new Anomaly(
                AnomalyType.SHULKER_BOX,
                9,
                block.pos,
                "Shulker box detected"
            );
            result.add(anomaly);
        }
        return result;
    }

    private List<Anomaly> detectPlayerActivity(double radius) {
        List<Anomaly> result = new ArrayList<>();
        List<Block> activityBlocks = new ArrayList<>();
        
        activityBlocks.addAll(world.getBlocksByType(BlockType.FURNACE, radius));
        activityBlocks.addAll(world.getBlocksByType(BlockType.CRAFTING_TABLE, radius));
        activityBlocks.addAll(world.getBlocksByType(BlockType.ANVIL, radius));
        activityBlocks.addAll(world.getBlocksByType(BlockType.HOPPER, radius));
        
        if (activityBlocks.size() >= 2) {
            double centerX = activityBlocks.stream().mapToDouble(b -> b.pos.x).average().orElse(0);
            double centerY = activityBlocks.stream().mapToDouble(b -> b.pos.y).average().orElse(0);
            double centerZ = activityBlocks.stream().mapToDouble(b -> b.pos.z).average().orElse(0);
            
            Anomaly anomaly = new Anomaly(
                AnomalyType.PLAYER_ACTIVITY,
                7,
                new Position(centerX, centerY, centerZ),
                "Player activity: " + activityBlocks.size() + " work blocks"
            );
            result.add(anomaly);
        }
        return result;
    }

    private List<Anomaly> detectChestClusters(double radius) {
        List<Anomaly> result = new ArrayList<>();
        List<Block> chestBlocks = world.getBlocksByType(BlockType.CHEST, radius);
        
        if (chestBlocks.size() >= 8) {
            double centerX = chestBlocks.stream().mapToDouble(b -> b.pos.x).average().orElse(0);
            double centerY = chestBlocks.stream().mapToDouble(b -> b.pos.y).average().orElse(0);
            double centerZ = chestBlocks.stream().mapToDouble(b -> b.pos.z).average().orElse(0);
            
            Anomaly anomaly = new Anomaly(
                AnomalyType.CHEST_CLUSTER,
                6,
                new Position(centerX, centerY, centerZ),
                "Base detected: " + chestBlocks.size() + " chests"
            );
            result.add(anomaly);
        }
        return result;
    }
}
