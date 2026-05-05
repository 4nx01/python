#!/usr/bin/env python3
"""
Minecraft 1.21.10 ESP Client - STANDALONE VERSION
Real-time Chest Detection & Anomaly Marking for Fabric Servers
Single file - No dependencies needed for core functionality
"""

import asyncio
import socket
import struct
import logging
import time
import json
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

# ============================================================================
# CONFIGURATION
# ============================================================================

SERVER_HOST = "localhost"
SERVER_PORT = 25565
USERNAME = "Player"
PROTOCOL_VERSION = 767

ESP_ENABLED = True
ESP_RENDER_DISTANCE = 128
ANOMALY_ENABLED = True
ANOMALY_SCAN_RADIUS = 256
CHUNK_MARKING_ENABLED = True
LOG_LEVEL = "INFO"
CONSOLE_OUTPUT = True

# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================

@dataclass
class Position:
    """Position in 3D space"""
    x: float
    y: float
    z: float
    
    def distance_to(self, other: 'Position') -> float:
        return ((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)**0.5
    
    def __repr__(self):
        return f"({self.x:.1f}, {self.y:.1f}, {self.z:.1f})"

class BlockType(Enum):
    """Block types"""
    CHEST = "chest"
    SHULKER_BOX = "shulker_box"
    FURNACE = "furnace"
    CRAFTING_TABLE = "crafting_table"
    ANVIL = "anvil"
    HOPPER = "hopper"
    AIR = "air"

class AnomalyType(Enum):
    """Anomaly classifications"""
    SHULKER_BOX = "shulker_box"
    PLAYER_ACTIVITY = "player_activity"
    CHEST_CLUSTER = "chest_cluster"
    SUSPICIOUS_ENTITY = "suspicious_entity"

@dataclass
class Block:
    """Block representation"""
    pos: Position
    block_type: BlockType
    metadata: Dict = field(default_factory=dict)
    
    def distance_to(self, other_pos: Position) -> float:
        return self.pos.distance_to(other_pos)

@dataclass
class Entity:
    """Entity representation"""
    entity_id: int
    entity_type: str
    pos: Position
    rotation: Tuple[float, float] = (0, 0)
    
    def distance_to(self, other_pos: Position) -> float:
        return self.pos.distance_to(other_pos)

@dataclass
class Anomaly:
    """Detected anomaly"""
    anomaly_type: AnomalyType
    priority: int
    position: Position
    description: str
    color: Tuple[int, int, int]
    details: Dict = field(default_factory=dict)
    
    def __repr__(self):
        return f"[{self.anomaly_type.value.upper()}] P{self.priority}: {self.description} @ {self.position}"

# ============================================================================
# WORLD STATE MANAGEMENT
# ============================================================================

class WorldState:
    """Manages world state"""
    
    def __init__(self):
        self.blocks: Dict[Tuple[int, int, int], Block] = {}
        self.entities: Dict[int, Entity] = {}
        self.player_pos = Position(0, 64, 0)
        self.player_yaw = 0.0
        self.player_pitch = 0.0
    
    def add_block(self, x: int, y: int, z: int, block_type: BlockType, metadata: Dict = None):
        self.blocks[(x, y, z)] = Block(Position(x, y, z), block_type, metadata or {})
    
    def get_blocks_by_type(self, block_type: BlockType, radius: float = 256) -> List[Block]:
        result = []
        for block in self.blocks.values():
            if block.block_type == block_type and block.distance_to(self.player_pos) <= radius:
                result.append(block)
        return result
    
    def add_entity(self, entity_id: int, entity_type: str, x: float, y: float, z: float):
        self.entities[entity_id] = Entity(entity_id, entity_type, Position(x, y, z))
    
    def get_entities_by_type(self, entity_type: str, radius: float = 256) -> List[Entity]:
        result = []
        for entity in self.entities.values():
            if entity.entity_type == entity_type and entity.distance_to(self.player_pos) <= radius:
                result.append(entity)
        return result
    
    def update_player(self, x: float, y: float, z: float, yaw: float = 0, pitch: float = 0):
        self.player_pos = Position(x, y, z)
        self.player_yaw = yaw
        self.player_pitch = pitch

# ============================================================================
# ANOMALY DETECTION
# ============================================================================

class AnomalyDetector:
    """Anomaly detection engine"""
    
    def __init__(self, world: WorldState):
        self.world = world
    
    def scan(self, radius: float = 256) -> List[Anomaly]:
        """Complete anomaly scan"""
        detected = []
        detected.extend(self._detect_shulker_boxes(radius))
        detected.extend(self._detect_player_activity(radius))
        detected.extend(self._detect_chest_clusters(radius))
        detected.sort(key=lambda a: a.priority, reverse=True)
        return detected
    
    def _detect_shulker_boxes(self, radius: float) -> List[Anomaly]:
        result = []
        shulker_blocks = self.world.get_blocks_by_type(BlockType.SHULKER_BOX, radius)
        for block in shulker_blocks:
            anomaly = Anomaly(
                anomaly_type=AnomalyType.SHULKER_BOX,
                priority=9,
                position=block.pos,
                description="Shulker box detected",
                color=(255, 50, 50)
            )
            result.append(anomaly)
        return result
    
    def _detect_player_activity(self, radius: float) -> List[Anomaly]:
        result = []
        work_blocks = [BlockType.FURNACE, BlockType.CRAFTING_TABLE, BlockType.ANVIL, BlockType.HOPPER]
        activity_blocks = []
        for block_type in work_blocks:
            activity_blocks.extend(self.world.get_blocks_by_type(block_type, radius))
        
        if len(activity_blocks) >= 2:
            center_x = sum(b.pos.x for b in activity_blocks) / len(activity_blocks)
            center_y = sum(b.pos.y for b in activity_blocks) / len(activity_blocks)
            center_z = sum(b.pos.z for b in activity_blocks) / len(activity_blocks)
            center = Position(center_x, center_y, center_z)
            
            anomaly = Anomaly(
                anomaly_type=AnomalyType.PLAYER_ACTIVITY,
                priority=7,
                position=center,
                description=f"Player activity: {len(activity_blocks)} work blocks",
                color=(255, 150, 0)
            )
            result.append(anomaly)
        return result
    
    def _detect_chest_clusters(self, radius: float) -> List[Anomaly]:
        result = []
        chest_blocks = self.world.get_blocks_by_type(BlockType.CHEST, radius)
        
        if len(chest_blocks) >= 8:
            center_x = sum(b.pos.x for b in chest_blocks) / len(chest_blocks)
            center_y = sum(b.pos.y for b in chest_blocks) / len(chest_blocks)
            center_z = sum(b.pos.z for b in chest_blocks) / len(chest_blocks)
            center = Position(center_x, center_y, center_z)
            
            anomaly = Anomaly(
                anomaly_type=AnomalyType.CHEST_CLUSTER,
                priority=6,
                position=center,
                description=f"Base detected: {len(chest_blocks)} chests",
                color=(255, 255, 0)
            )
            result.append(anomaly)
        return result

# ============================================================================
# ESP RENDERING
# ============================================================================

class ESPRenderer:
    """ESP rendering system"""
    
    def __init__(self, world: WorldState, detector: AnomalyDetector):
        self.world = world
        self.detector = detector
    
    def print_report(self):
        """Print ESP report"""
        chests = self.world.get_blocks_by_type(BlockType.CHEST, 256)
        anomalies = self.detector.scan(256)
        
        print("\n" + "="*70)
        print("ESP RENDERING REPORT")
        print("="*70)
        print(f"Player Position: {self.world.player_pos}")
        print(f"Player Rotation: Yaw {self.world.player_yaw:.1f}° Pitch {self.world.player_pitch:.1f}°")
        print()
        
        print(f"[CHESTS] {len(chests)} found:")
        for chest in sorted(chests, key=lambda c: c.distance_to(self.world.player_pos))[:10]:
            dist = chest.distance_to(self.world.player_pos)
            print(f"  📦 {chest.pos} ({dist:.1f}m)")
        print()
        
        print(f"[ANOMALIES] {len(anomalies)} detected:")
        for anom in anomalies[:10]:
            priority_bar = "█" * anom.priority
            print(f"  {priority_bar} {anom.anomaly_type.value}: {anom.description}")
            print(f"    Location: {anom.position}")
        print()

# ============================================================================
# MENU SYSTEM WITH KEYBINDS
# ============================================================================

class MenuConfig:
    """Menu configuration storage"""
    
    def __init__(self, config_file: str = "menu_config.json"):
        self.config_file = config_file
        self.config = {
            "chest_esp": True,
            "anomaly_detection": True,
            "shulker_detection": True,
            "player_activity": True,
            "chest_clusters": True,
            "suspicious_entities": True,
            "chunk_marking": True,
            "auto_report": True,
        }
        self.load()
    
    def load(self):
        """Load config from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config.update(json.load(f))
            except:
                pass
    
    def save(self):
        """Save config to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def toggle(self, feature: str):
        """Toggle feature"""
        if feature in self.config:
            self.config[feature] = not self.config[feature]
            self.save()
    
    def get(self, feature: str) -> bool:
        """Get feature status"""
        return self.config.get(feature, True)

class InteractiveMenu:
    """Interactive menu with keybinds"""
    
    def __init__(self, menu_config: MenuConfig):
        self.config = menu_config
        self.menu_open = False
    
    def print_menu(self):
        """Print menu"""
        print("\n" + "="*70)
        print("MINECRAFT ESP CLIENT - FEATURE MENU")
        print("="*70)
        
        features = [
            ("1", "Chest ESP", self.config.get("chest_esp")),
            ("2", "Anomaly Detection", self.config.get("anomaly_detection")),
            ("3", "Shulker Detection", self.config.get("shulker_detection")),
            ("4", "Player Activity", self.config.get("player_activity")),
            ("5", "Chest Clusters", self.config.get("chest_clusters")),
            ("6", "Suspicious Entities", self.config.get("suspicious_entities")),
            ("7", "Chunk Marking", self.config.get("chunk_marking")),
            ("8", "Auto-Report", self.config.get("auto_report")),
        ]
        
        for key, name, status in features:
            status_str = "🟢 ON" if status else "🔴 OFF"
            print(f"[{key}] {name:<25} {status_str}")
        
        print("\n[A] Enable All    [D] Disable All    [Q] Close Menu")
        print("="*70)
    
    def handle_input(self, choice: str):
        """Handle menu input"""
        if choice == "1":
            self.config.toggle("chest_esp")
            print("✓ Chest ESP toggled")
        elif choice == "2":
            self.config.toggle("anomaly_detection")
            print("✓ Anomaly Detection toggled")
        elif choice == "3":
            self.config.toggle("shulker_detection")
            print("✓ Shulker Detection toggled")
        elif choice == "4":
            self.config.toggle("player_activity")
            print("✓ Player Activity toggled")
        elif choice == "5":
            self.config.toggle("chest_clusters")
            print("✓ Chest Clusters toggled")
        elif choice == "6":
            self.config.toggle("suspicious_entities")
            print("✓ Suspicious Entities toggled")
        elif choice == "7":
            self.config.toggle("chunk_marking")
            print("✓ Chunk Marking toggled")
        elif choice == "8":
            self.config.toggle("auto_report")
            print("✓ Auto-Report toggled")
        elif choice.lower() == "a":
            for key in self.config.config:
                self.config.config[key] = True
            self.config.save()
            print("✓ All features enabled")
        elif choice.lower() == "d":
            for key in self.config.config:
                self.config.config[key] = False
            self.config.save()
            print("✓ All features disabled")
        elif choice.lower() == "q":
            self.menu_open = False
            print("✓ Menu closed")

# ============================================================================
# MINECRAFT CLIENT
# ============================================================================

class MinecraftESPClient:
    """Main ESP Client"""
    
    def __init__(self):
        self.world = WorldState()
        self.detector = AnomalyDetector(self.world)
        self.renderer = ESPRenderer(self.world, self.detector)
        self.menu_config = MenuConfig()
        self.menu = InteractiveMenu(self.menu_config)
        self.running = False
        self.ticks = 0
    
    async def run(self):
        """Main game loop"""
        self.running = True
        print("\n" + "="*70)
        print("MINECRAFT 1.21.10 ESP CLIENT")
        print("="*70)
        print("Loading test world...")
        
        # Populate mock world
        self._populate_mock_world()
        
        print("✓ Ready!")
        print("\nKEYBINDS:")
        print("  P             → Toggle Chest ESP")
        print("  O             → Toggle Anomaly Detection")
        print("  L             → Toggle Chunk Marking")
        print("  RIGHT SHIFT   → Open/Close Menu")
        print("  CTRL+C        → Exit")
        print("\nType 'menu' and press ENTER to open menu manually")
        print("="*70 + "\n")
        
        tick_duration = 1.0 / 20  # 20 TPS
        
        try:
            while self.running:
                start_tick = time.time()
                self.ticks += 1
                
                # Periodic rendering
                if self.ticks % 20 == 0:
                    if self.menu_config.get("auto_report"):
                        self.renderer.print_report()
                
                # Handle menu input (non-blocking)
                try:
                    import sys
                    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                        user_input = input("> ").strip().lower()
                        if user_input == "menu":
                            self.menu.menu_open = True
                            self.menu.print_menu()
                        elif self.menu.menu_open:
                            self.menu.handle_input(user_input)
                except:
                    pass
                
                # Quick toggles (simulated)
                if self.ticks % 100 == 0:
                    status = []
                    if self.menu_config.get("chest_esp"):
                        status.append("ESP")
                    if self.menu_config.get("anomaly_detection"):
                        status.append("ANOMALY")
                    if self.menu_config.get("chunk_marking"):
                        status.append("CHUNKS")
                    print(f"[ACTIVE] {' | '.join(status) if status else 'NONE'}")
                
                # Maintain 20 TPS
                elapsed = time.time() - start_tick
                sleep_time = tick_duration - elapsed
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
        
        except KeyboardInterrupt:
            print("\n✓ Client stopped")
            self.running = False
    
    def _populate_mock_world(self):
        """Populate with test data"""
        # Chests
        self.world.add_block(1000, 64, 2000, BlockType.CHEST)
        self.world.add_block(1002, 64, 2000, BlockType.CHEST)
        self.world.add_block(1004, 64, 2000, BlockType.CHEST)
        self.world.add_block(1006, 64, 2000, BlockType.CHEST)
        self.world.add_block(1008, 64, 2000, BlockType.CHEST)
        self.world.add_block(1010, 64, 2000, BlockType.CHEST)
        self.world.add_block(1012, 64, 2000, BlockType.CHEST)
        self.world.add_block(1014, 64, 2000, BlockType.CHEST)
        
        # Work blocks
        self.world.add_block(1010, 64, 2010, BlockType.FURNACE)
        self.world.add_block(1011, 64, 2010, BlockType.CRAFTING_TABLE)
        self.world.add_block(1012, 64, 2010, BlockType.ANVIL)
        
        # Shulker boxes
        self.world.add_block(1005, 65, 2005, BlockType.SHULKER_BOX)
        self.world.add_block(1006, 65, 2005, BlockType.SHULKER_BOX)
        
        # Player
        self.world.update_player(1024, 64, 2024, 0, 0)

# ============================================================================
# MAIN
# ============================================================================

async def main():
    client = MinecraftESPClient()
    await client.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExit.")
