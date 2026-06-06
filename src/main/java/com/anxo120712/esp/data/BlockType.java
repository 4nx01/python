package com.anxo120712.esp.data;

/**
 * Block type enumeration
 */
public enum BlockType {
    CHEST("minecraft:chest"),
    SHULKER_BOX("minecraft:shulker_box"),
    FURNACE("minecraft:furnace"),
    CRAFTING_TABLE("minecraft:crafting_table"),
    ANVIL("minecraft:anvil"),
    HOPPER("minecraft:hopper"),
    SPAWNER("minecraft:spawner"),
    AIR("minecraft:air");

    public final String id;

    BlockType(String id) {
        this.id = id;
    }

    public static BlockType fromString(String id) {
        for (BlockType type : values()) {
            if (type.id.equals(id)) {
                return type;
            }
        }
        return AIR;
    }
}
