"""
Anomaly Detection Engine - Detects shulkers, player activity, chest clusters, suspicious entities
"""

import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from minecraft_client.world import WorldState, BlockType
from minecraft_client.network import Position

logger = logging.getLogger(__name__)

class AnomalyType(Enum):
    """Anomaly classification"""
    SHULKER_BOX = "shulker_box"
    PLAYER_ACTIVITY = "player_activity"
    CHEST_CLUSTER = "chest_cluster"
    SUSPICIOUS_ENTITY = "suspicious_entity"

@dataclass
class Anomaly:
    """Detected anomaly"""
    anomaly_type: AnomalyType
    priority: int  # 1-10
    position: Position
    description: str
    color: Tuple[int, int, int]
    details: Dict = field(default_factory=dict)
    timestamp: float = 0.0

    def __repr__(self):
        return f"[{self.anomaly_type.value.upper()}] P{self.priority}: {self.description} @ ({self.position.x:.0f}, {self.position.y:.0f}, {self.position.z:.0f})"

class AnomalyDetector:
    """Advanced anomaly detection engine"""
    
    def __init__(self, world: WorldState):
        self.world = world
        self.anomalies: Dict[str, Anomaly] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.scan_count = 0

    def scan(self, radius: float = 256) -> List[Anomaly]:
        """Perform complete anomaly scan"""
        self.scan_count += 1
        detected = []
        
        detected.extend(self._detect_shulker_boxes(radius))
        detected.extend(self._detect_player_activity(radius))
        detected.extend(self._detect_chest_clusters(radius))
        detected.extend(self._detect_suspicious_entities(radius))
        
        # Sort by priority (descending)
        detected.sort(key=lambda a: a.priority, reverse=True)
        return detected

    def _detect_shulker_boxes(self, radius: float) -> List[Anomaly]:
        """Detect shulker boxes (highest priority)"""
        result = []
        shulker_blocks = self.world.get_blocks_by_type(BlockType.SHULKER_BOX, radius)
        
        for block in shulker_blocks:
            anomaly = Anomaly(
                anomaly_type=AnomalyType.SHULKER_BOX,
                priority=9,
                position=block.pos,
                description=f"Shulker box detected",
                color=(255, 50, 50),  # Red
                details={"block_type": "shulker_box", "color": block.metadata.get("color", "unknown")}
            )
            result.append(anomaly)
        
        return result

    def _detect_player_activity(self, radius: float) -> List[Anomaly]:
        """Detect work blocks indicating player activity"""
        result = []
        work_blocks = [
            BlockType.FURNACE, BlockType.BLAST_FURNACE, BlockType.SMOKER,
            BlockType.HOPPER, BlockType.DROPPER, BlockType.DISPENSER,
            BlockType.CRAFTING_TABLE, BlockType.ANVIL, BlockType.ENCHANTING_TABLE
        ]
        
        activity_blocks = []
        for block_type in work_blocks:
            activity_blocks.extend(self.world.get_blocks_by_type(block_type, radius))
        
        # Cluster work blocks (2+ = activity hotspot)
        if len(activity_blocks) >= 2:
            # Find cluster center
            center_x = sum(b.pos.x for b in activity_blocks) / len(activity_blocks)
            center_y = sum(b.pos.y for b in activity_blocks) / len(activity_blocks)
            center_z = sum(b.pos.z for b in activity_blocks) / len(activity_blocks)
            center = Position(center_x, center_y, center_z)
            
            anomaly = Anomaly(
                anomaly_type=AnomalyType.PLAYER_ACTIVITY,
                priority=7,
                position=center,
                description=f"Player activity detected: {len(activity_blocks)} work blocks found",
                color=(255, 150, 0),  # Orange
                details={
                    "work_block_count": len(activity_blocks),
                    "blocks": [b.block_type.value for b in activity_blocks]
                }
            )
            result.append(anomaly)
        
        return result

    def _detect_chest_clusters(self, radius: float) -> List[Anomaly]:
        """Detect storage clusters (8+ chests = base location)"""
        result = []
        chest_blocks = self.world.get_blocks_by_type(BlockType.CHEST, radius)
        barrel_blocks = self.world.get_blocks_by_type(BlockType.BARREL, radius)
        all_storage = chest_blocks + barrel_blocks
        
        if len(all_storage) >= 8:
            # Calculate cluster center
            center_x = sum(b.pos.x for b in all_storage) / len(all_storage)
            center_y = sum(b.pos.y for b in all_storage) / len(all_storage)
            center_z = sum(b.pos.z for b in all_storage) / len(all_storage)
            center = Position(center_x, center_y, center_z)
            
            # Check if all storage is within 32 blocks (cluster)
            max_dist = max(b.distance_to(center) for b in all_storage)
            
            if max_dist <= 32:
                anomaly = Anomaly(
                    anomaly_type=AnomalyType.CHEST_CLUSTER,
                    priority=6,
                    position=center,
                    description=f"Base detected: {len(all_storage)} storage containers",
                    color=(255, 255, 0),  # Yellow
                    details={
                        "container_count": len(all_storage),
                        "chest_count": len(chest_blocks),
                        "barrel_count": len(barrel_blocks),
                        "cluster_radius": max_dist
                    }
                )
                result.append(anomaly)
        
        return result

    def _detect_suspicious_entities(self, radius: float) -> List[Anomaly]:
        """Detect suspicious entity placements"""
        result = []
        suspicious_types = ["armor_stand", "item_frame", "painting"]
        suspicious_entities = []
        
        for entity_type in suspicious_types:
            suspicious_entities.extend(self.world.get_entities_by_type(entity_type, radius))
        
        if len(suspicious_entities) >= 3:
            # Calculate center
            center_x = sum(e.pos.x for e in suspicious_entities) / len(suspicious_entities)
            center_y = sum(e.pos.y for e in suspicious_entities) / len(suspicious_entities)
            center_z = sum(e.pos.z for e in suspicious_entities) / len(suspicious_entities)
            center = Position(center_x, center_y, center_z)
            
            anomaly = Anomaly(
                anomaly_type=AnomalyType.SUSPICIOUS_ENTITY,
                priority=5,
                position=center,
                description=f"Suspicious entities detected: {len(suspicious_entities)} found",
                color=(100, 200, 0),  # Light Green
                details={
                    "entity_count": len(suspicious_entities),
                    "types": list(set(e.entity_type for e in suspicious_entities))
                }
            )
            result.append(anomaly)
        
        return result

    def get_high_priority_anomalies(self, min_priority: int = 8) -> List[Anomaly]:
        """Get anomalies above priority threshold"""
        detected = self.scan()
        return [a for a in detected if a.priority >= min_priority]

    def get_nearby_anomalies(self, radius: float = 100) -> List[Anomaly]:
        """Get anomalies within specific radius"""
        detected = self.scan(radius)
        return detected

    def get_anomalies_by_type(self, anomaly_type: AnomalyType) -> List[Anomaly]:
        """Get all anomalies of specific type"""
        detected = self.scan()
        return [a for a in detected if a.anomaly_type == anomaly_type]
