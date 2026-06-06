package com.anxo120712.esp;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Main mod entry point for Minecraft ESP Fabric mod
 */
public class MinecraftESPMod implements ClientModInitializer {
    public static final String MOD_ID = "minecraft-esp-fabric";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    @Override
    public void onInitializeClient() {
        LOGGER.info("Minecraft ESP Fabric Mod initialized!");
        
        // Register client tick event
        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            // ESP logic will go here
        });
    }
}
