````markdown
# Minecraft 1.21.10 ESP Client

A Python-based Minecraft client with real-time chest ESP and advanced anomaly detection for Fabric servers.

## Features

### 🎯 Chest ESP
- **Real-time detection** of all nearby chests
- **Visual ESP lines** drawn from player to each chest
- **Distance-based coloring**:
  - 🟢 Green (< 32 blocks)
  - 🟡 Yellow (32-64 blocks)
  - 🟠 Orange (> 64 blocks)
- **Box rendering** around chest locations
- **Distance labels** showing exact distance

### 🔍 Anomaly Detection Engine

Advanced multi-layer anomaly detection with priority system:

| Anomaly Type | Priority | Color | Description |
|---|---|---|---|
| **Shulker Box** | 9 | 🔴 Red | All 16 color variants |
| **Player Activity** | 7 | 🟠 Orange | Work blocks (furnaces, hoppers, etc) |
| **Chest Cluster** | 6 | 🟡 Yellow | 8+ containers = base location |
| **Suspicious Entity** | 5 | 🟢 Green | Armor stands, item frames |

### 🗺️ Chunk Marking
- Real-time chunk boundary visualization
- Grid overlay showing loaded chunks
- Automatic cleanup of distant chunks

### 📊 World Tracking
- Full player position tracking
- Entity tracking (players, armor stands, etc)
- Block state management
- Chunk loading/unloading

## Installation

### Prerequisites
- Python 3.8+
- Minecraft server 1.21.10 with Fabric

### Setup

```bash
# Clone repository
cd minecraft_client

# Install dependencies
pip install -r requirements.txt

# Configure
edit config.py  # Set SERVER_HOST, SERVER_PORT, USERNAME
```

## Configuration

Edit `config.py` to customize:

```python
# Server settings
SERVER_HOST = "localhost"
SERVER_PORT = 25565
USERNAME = "Player"

# ESP settings
ESP_ENABLED = True
ESP_RENDER_DISTANCE = 128  # blocks
ESP_UPDATE_FREQUENCY = 20  # ticks

# Anomaly detection
ANOMALY_ENABLED = True
ANOMALY_SCAN_RADIUS = 256  # blocks
ANOMALY_UPDATE_FREQUENCY = 40  # ticks

# Detection priorities (1-10)
ANOMALIES = {
    "shulker_box": {"priority": 9, ...},
    "player_activity": {"priority": 7, ...},
    "chest_cluster": {"priority": 6, ...},
    "suspicious_entity": {"priority": 5, ...},
}
```

## Usage

### Run Client

```bash
python main.py
```

### Output Example

```
ESP RENDERING REPORT
============================================================

Player Position: (1024.5, 64.0, 2048.3)

[CHESTS] 23 found:
  📦 1025, 64, 2050 (5m)
  📦 1030, 64, 2052 (12m)
  📦 1020, 64, 2048 (8m)

[ANOMALIES] 3 detected:
  █████████ Shulker box: Shulker box detected at (1024, 64, 2048)...
  ███████ Player activity: Player activity detected: 4 work blocks...
  ██████ Chest cluster: Base detected: 12 chests at (1030, 64, 2055)...

[RENDER QUEUE] 156 commands
  Lines: 45
  Boxes: 38
  Text: 73
```

## Architecture

```
minecraft_client/
├── config.py              # Configuration
├── network.py             # Minecraft protocol (1.21.10)
├── world.py              # World state tracking
├── anomaly_detector.py   # Detection engine
├── esp.py                # Rendering system
├── main.py               # Application loop
└── __init__.py           # Package init
```

### Components

**network.py** - Minecraft Protocol Handler
- Handles connection to Fabric server
- Packet parsing and encoding
- Protocol version 767 (1.21.10)

**world.py** - World State Management
- Tracks player position and rotation
- Maintains block and entity data
- Chunk loading/unloading
- Position queries

**anomaly_detector.py** - Anomaly Detection
- Multi-threaded scanning
- Cluster detection
- Priority-based classification
- Temporal tracking

**esp.py** - ESP Rendering
- Line rendering to targets
- Box outlines around anomalies
- Distance-based coloring
- Text labels
- Console output

**main.py** - Application Loop
- 20 TPS game loop
- Tick-based processing
- Packet reading
- Status reporting

## Detection Algorithm

### Shulker Box Detection (Priority 9)
- Scans for all shulker box blocks
- All 16 color variants detected
- Highest priority target

### Player Activity Detection (Priority 7)
- Detects work blocks:
  - Furnaces, blast furnaces, smokers
  - Hoppers, dispensers, droppers
  - Crafting tables, anvils
  - Enchanting tables, cauldrons
- Clusters 2+ work blocks = activity hotspot
- Indicates base location

### Chest Cluster Detection (Priority 6)
- Identifies chest groupings
- 8+ chests within 32 block radius = base
- Calculates cluster center
- High-value target indicator

### Suspicious Entity Detection (Priority 5)
- Detects unusual entity placements
- Armor stands, item frames, paintings
- Often indicate base decoration/traps

## Performance

- **Render Distance**: 256 blocks (configurable)
- **Scan Frequency**: 40 ticks (2 sec, configurable)
- **ESP Update**: 20 ticks (1 sec, configurable)
- **Max Tracked**: 1000 anomalies
- **Chunk Cache**: TTL 300 seconds

## Protocol Support

- **Version**: 1.21.10
- **Protocol**: 767
- **Server Type**: Fabric
- **Connection**: TCP socket

## Logging

Logs to both console and `minecraft_client.log`:
- `DEBUG` - Detailed packet info
- `INFO` - Major events
- `WARNING` - Important detections
- `ERROR` - Connection/parsing errors

## Troubleshooting

### Connection Failed
```
Check SERVER_HOST and SERVER_PORT
Ensure server is running and accepting connections
Verify Fabric is installed
```

### No Blocks Detected
```
Check USERNAME matches connected player
Verify player is loaded into world
Check render distance in config
```

### High CPU Usage
```
Reduce ANOMALY_UPDATE_FREQUENCY
Reduce ESP_RENDER_DISTANCE
Enable CHUNK_CACHE_TTL
```

## Advanced Usage

### Custom Detection
```python
from anomaly_detector import AnomalyDetector
from world import WorldState, BlockType

detector = AnomalyDetector(world)

# Custom scan
anomalies = detector.scan(radius=512)

# Filter by priority
high_priority = detector.get_high_priority_anomalies(min_priority=8)

# Get nearby only
nearby = detector.get_nearby_anomalies(radius=100)
```

### Custom Rendering
```python
from esp import ESPRenderer

renderer = ESPRenderer(world, detector)
commands = renderer.render(max_distance=256)

for cmd in commands:
    if cmd.command_type == "line":
        # Custom rendering logic
        pass
```

## Limitations

- Console-based rendering (no graphical overlay yet)
- Single-threaded packet processing
- No authentication handling
- Limited block state support

## Future Features

- [ ] OpenGL-based 3D overlay
- [ ] Player tracking with distance lines
- [ ] Portal/nether detection
- [ ] Base mapping export
- [ ] Web dashboard
- [ ] Multi-threaded scanning
- [ ] Extended encryption support

## License

MIT License

## Author

Anomaly Detection Team
````
