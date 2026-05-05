"""
Configuration for Minecraft ESP Client (1.21.10)
"""

# ============ SERVER SETTINGS ============
SERVER_HOST = "localhost"
SERVER_PORT = 25565
USERNAME = "Player"
PROTOCOL_VERSION = 767  # 1.21.10

# ============ ESP SETTINGS ============
ESP_ENABLED = True
ESP_RENDER_DISTANCE = 128  # blocks
ESP_LINE_WIDTH = 2
ESP_UPDATE_FREQUENCY = 20  # ticks

# ESP Colors (RGB)
COLORS = {
    "chest": (100, 255, 100),        # Green
    "shulker": (255, 50, 50),         # Red
    "distance_near": (0, 255, 0),     # Green (< 32 blocks)
    "distance_mid": (255, 255, 0),    # Yellow (32-64 blocks)
    "distance_far": (255, 100, 0),    # Orange (> 64 blocks)
}

# ============ ANOMALY DETECTION ============
ANOMALY_ENABLED = True
ANOMALY_SCAN_RADIUS = 256  # blocks from player
ANOMALY_UPDATE_FREQUENCY = 40  # ticks

# Anomaly Detection Priorities (1-10, higher = more important)
ANOMALIES = {
    "shulker_box": {
        "priority": 9,
        "color": (255, 50, 50),      # Red
        "enabled": True,
    },
    "player_activity": {
        "priority": 7,
        "color": (255, 150, 0),      # Orange
        "enabled": True,
        "work_blocks": [
            "furnace", "blast_furnace", "smoker",
            "hopper", "dropper", "dispenser",
            "crafting_table", "anvil", "cauldron",
            "enchanting_table"
        ]
    },
    "chest_cluster": {
        "priority": 6,
        "color": (255, 255, 0),      # Yellow
        "enabled": True,
        "cluster_threshold": 8,      # containers within radius
        "cluster_radius": 32,        # blocks
    },
    "suspicious_entity": {
        "priority": 5,
        "color": (100, 200, 0),      # Light Green
        "enabled": True,
        "entities": [
            "armor_stand",
            "item_frame",
            "painting",
        ]
    },
}

# ============ CHUNK MARKING ============
CHUNK_MARKING_ENABLED = True
CHUNK_GRID_COLOR = (100, 100, 100)  # Dark Gray
CHUNK_GRID_WIDTH = 1
CHUNK_CLEANUP_DISTANCE = 512  # blocks

# ============ LOGGING ============
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "minecraft_client.log"
CONSOLE_OUTPUT = True

# ============ PERFORMANCE ============
MAX_TRACKED_ANOMALIES = 1000
MAX_ESP_TARGETS = 500
CACHE_CHUNK_DATA = True
CHUNK_CACHE_TTL = 300  # seconds
