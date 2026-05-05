"""
World State Management - Tracks blocks, entities, and chunks
"""

import logging
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from minecraft_client.network import Position

logger = logging.getLogger(__name__)

class BlockType(Enum):
    """Block type identifiers"""
    # Storage
    CHEST = "chest"
    SHULKER_BOX = "shulker_box"
    BARREL = "barrel"
    FURNACE = "furnace"
    BLAST_FURNACE = "blast_furnace"
    SMOKER = "smoker"
    HOPPER = "hopper"
    DROPPER = "dropper"
    DISPENSER = "dispenser"
    # Work blocks
    CRAFTING_TABLE = "crafting_table"
    ANVIL = "anvil"
    CAULDRON = "cauldron"
    ENCHANTING_TABLE = "enchanting_table"
    # Other
    AIR = "air"
    STONE = "stone"
    DIRT = "dirt"

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
    rotation: Tuple[float, float]  # (yaw, pitch)
    metadata: Dict = field(default_factory=dict)

    def distance_to(self, other_pos: Position) -> float:
        return self.pos.distance_to(other_pos)

class Chunk:
    """Chunk data container"""
    def __init__(self, x: int, z: int):
        self.x = x
        self.z = z
        self.blocks: Dict[Tuple[int, int, int], Block] = {}
        self.loaded = True

    def get_blocks_in_radius(self, center: Position, radius: float) -> List[Block]:
        """Get all blocks within radius of center point"""
        result = []
        for block in self.blocks.values():
            if block.distance_to(center) <= radius:
                result.append(block)
        return result

class WorldState:
    """Manages world state - blocks, entities, chunks"""
    
    def __init__(self):
        self.chunks: Dict[Tuple[int, int], Chunk] = {}
        self.blocks: Dict[Tuple[int, int, int], Block] = {}
        self.entities: Dict[int, Entity] = {}
        self.player_pos = Position(0, 64, 0)
        self.player_yaw = 0.0
        self.player_pitch = 0.0
        self.logger = logging.getLogger(self.__class__.__name__)

    def chunk_key(self, x: int, z: int) -> Tuple[int, int]:
        """Get chunk key"""
        return (x >> 4, z >> 4)

    def add_block(self, x: int, y: int, z: int, block_type: BlockType, metadata: Dict = None):
        """Add block to world"""
        pos = Position(x, y, z)
        block = Block(pos, block_type, metadata or {})
        self.blocks[(x, y, z)] = block
        
        chunk_x, chunk_z = self.chunk_key(x, z)
        chunk_key = (chunk_x, chunk_z)
        if chunk_key not in self.chunks:
            self.chunks[chunk_key] = Chunk(chunk_x, chunk_z)
        self.chunks[chunk_key].blocks[(x, y, z)] = block

    def remove_block(self, x: int, y: int, z: int):
        """Remove block from world"""
        if (x, y, z) in self.blocks:
            del self.blocks[(x, y, z)]
            chunk_x, chunk_z = self.chunk_key(x, z)
            chunk_key = (chunk_x, chunk_z)
            if chunk_key in self.chunks and (x, y, z) in self.chunks[chunk_key].blocks:
                del self.chunks[chunk_key].blocks[(x, y, z)]

    def get_block(self, x: int, y: int, z: int) -> Optional[Block]:
        """Get block at position"""
        return self.blocks.get((x, y, z))

    def get_blocks_by_type(self, block_type: BlockType, radius: float = 256) -> List[Block]:
        """Get all blocks of specific type within radius"""
        result = []
        for block in self.blocks.values():
            if block.block_type == block_type and block.distance_to(self.player_pos) <= radius:
                result.append(block)
        return result

    def get_blocks_in_radius(self, center: Position, radius: float) -> List[Block]:
        """Get all blocks within radius of center point"""
        result = []
        for block in self.blocks.values():
            if block.distance_to(center) <= radius:
                result.append(block)
        return result

    def add_entity(self, entity_id: int, entity_type: str, x: float, y: float, z: float, yaw: float = 0, pitch: float = 0):
        """Add entity to world"""
        pos = Position(x, y, z)
        entity = Entity(entity_id, entity_type, pos, (yaw, pitch))
        self.entities[entity_id] = entity

    def remove_entity(self, entity_id: int):
        """Remove entity from world"""
        if entity_id in self.entities:
            del self.entities[entity_id]

    def update_entity_position(self, entity_id: int, x: float, y: float, z: float, yaw: float = 0, pitch: float = 0):
        """Update entity position"""
        if entity_id in self.entities:
            self.entities[entity_id].pos = Position(x, y, z)
            self.entities[entity_id].rotation = (yaw, pitch)

    def get_entities_by_type(self, entity_type: str, radius: float = 256) -> List[Entity]:
        """Get all entities of specific type within radius"""
        result = []
        for entity in self.entities.values():
            if entity.entity_type == entity_type and entity.distance_to(self.player_pos) <= radius:
                result.append(entity)
        return result

    def get_entities_in_radius(self, center: Position, radius: float) -> List[Entity]:
        """Get all entities within radius of center point"""
        result = []
        for entity in self.entities.values():
            if entity.distance_to(center) <= radius:
                result.append(entity)
        return result

    def load_chunk(self, x: int, z: int) -> Chunk:
        """Load or get chunk"""
        chunk_key = (x, z)
        if chunk_key not in self.chunks:
            self.chunks[chunk_key] = Chunk(x, z)
        return self.chunks[chunk_key]

    def unload_chunk(self, x: int, z: int):
        """Unload chunk"""
        chunk_key = (x, z)
        if chunk_key in self.chunks:
            chunk = self.chunks[chunk_key]
            # Remove blocks from global list
            for block_pos in chunk.blocks:
                if block_pos in self.blocks:
                    del self.blocks[block_pos]
            del self.chunks[chunk_key]

    def get_loaded_chunks(self) -> List[Chunk]:
        """Get all loaded chunks"""
        return list(self.chunks.values())

    def cleanup_distant_chunks(self, max_distance: float = 512):
        """Remove chunks beyond max distance from player"""
        chunks_to_remove = []
        for chunk_key, chunk in self.chunks.items():
            chunk_center_x = chunk.x * 16 + 8
            chunk_center_z = chunk.z * 16 + 8
            dist = ((chunk_center_x - self.player_pos.x)**2 + (chunk_center_z - self.player_pos.z)**2)**0.5
            if dist > max_distance:
                chunks_to_remove.append(chunk_key)
        
        for chunk_key in chunks_to_remove:
            self.unload_chunk(chunk_key[0], chunk_key[1])

    def update_player(self, x: float, y: float, z: float, yaw: float = 0, pitch: float = 0):
        """Update player position and rotation"""
        self.player_pos = Position(x, y, z)
        self.player_yaw = yaw
        self.player_pitch = pitch
