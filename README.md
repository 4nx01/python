# Minecraft ESP - Fabric Mod Edition

A real-time ESP (wallhack) mod for Minecraft Fabric that detects chests, spawners, and player activity.

## Features

- **Chest ESP**: Highlights nearby chests
- **Spawner Detection**: Detects mob spawners with spawn type information
- **Anomaly Detection**: Identifies suspicious player activity and base locations
- **Shulker Box Detection**: Finds shulker boxes in the world
- **Player Activity Tracking**: Identifies work areas (furnaces, crafting tables, anvils)
- **Chest Cluster Detection**: Finds potential bases with multiple chests
- **Chunk Marking**: Marks chunks with items of interest

## Building

Requirements:
- Java 21 or higher
- Gradle

```bash
# Clone the repository
git clone <repo-url>
cd python
git checkout fabric-mod

# Build the mod
./gradlew build

# The compiled JAR will be in: build/libs/
```

## Installation

1. Install [Fabric Loader](https://fabricmc.net/use/)
2. Copy the compiled `.jar` file to your `mods` folder
3. Launch Minecraft with the Fabric profile
4. The mod will be loaded automatically

## Configuration

Features can be toggled in-game using keybinds:
- **P**: Toggle Chest ESP
- **U**: Toggle Spawner ESP
- **O**: Toggle Anomaly Detection
- **L**: Toggle Chunk Marking
- **RIGHT SHIFT**: Open/Close Menu

## Development

This mod was converted from the original Python ESP client to Java/Fabric.

### Project Structure

```
src/main/java/com/anxo120712/esp/
├── data/           # Data classes (Position, Block, Entity, Anomaly)
├── world/          # World state management
├── detection/      # Anomaly detection logic
├── config/         # Configuration management
└── MinecraftESPMod.java  # Main mod entry point
```

## License

MIT License
