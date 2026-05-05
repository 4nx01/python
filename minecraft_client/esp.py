"""
ESP Rendering System - Draws lines to chests and marks anomalies
"""

import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
from minecraft_client.world import WorldState, BlockType
from minecraft_client.anomaly_detector import AnomalyDetector, Anomaly
from minecraft_client.network import Position

logger = logging.getLogger(__name__)

class RenderCommand(Enum):
    """Render command types"""
    LINE = "line"
    BOX = "box"
    TEXT = "text"
    GRID = "grid"

@dataclass
class RenderOp:
    """Render operation"""
    command_type: RenderCommand
    start: Position
    end: Position
    color: Tuple[int, int, int]
    label: str = ""
    width: int = 1

class ESPRenderer:
    """ESP rendering system - console-based visualization"""
    
    def __init__(self, world: WorldState, detector: AnomalyDetector):
        self.world = world
        self.detector = detector
        self.render_queue: List[RenderOp] = []
        self.logger = logging.getLogger(self.__class__.__name__)

    def render(self, max_distance: float = 256, include_grid: bool = True) -> List[RenderOp]:
        """Generate render commands for current frame"""
        self.render_queue = []
        
        # Render chest ESP
        self._render_chest_esp(max_distance)
        
        # Render anomalies
        self._render_anomalies(max_distance)
        
        # Render chunk grid
        if include_grid:
            self._render_chunk_grid(max_distance)
        
        return self.render_queue

    def _render_chest_esp(self, max_distance: float):
        """Draw ESP lines to chests"""
        chests = self.world.get_blocks_by_type(BlockType.CHEST, max_distance)
        
        for chest in chests:
            distance = chest.distance_to(self.world.player_pos)
            
            # Color by distance
            if distance < 32:
                color = (0, 255, 0)  # Green
            elif distance < 64:
                color = (255, 255, 0)  # Yellow
            else:
                color = (255, 100, 0)  # Orange
            
            op = RenderOp(
                command_type=RenderCommand.LINE,
                start=self.world.player_pos,
                end=chest.pos,
                color=color,
                label=f"Chest {distance:.1f}m",
                width=2
            )
            self.render_queue.append(op)
            
            # Box around chest
            op_box = RenderOp(
                command_type=RenderCommand.BOX,
                start=Position(chest.pos.x - 0.5, chest.pos.y - 0.5, chest.pos.z - 0.5),
                end=Position(chest.pos.x + 0.5, chest.pos.y + 0.5, chest.pos.z + 0.5),
                color=color,
                label=f"Chest",
                width=1
            )
            self.render_queue.append(op_box)

    def _render_anomalies(self, max_distance: float):
        """Render anomaly markers and boxes"""
        anomalies = self.detector.scan(max_distance)
        
        for anomaly in anomalies:
            # Draw line from player to anomaly
            op_line = RenderOp(
                command_type=RenderCommand.LINE,
                start=self.world.player_pos,
                end=anomaly.position,
                color=anomaly.color,
                label=f"P{anomaly.priority}",
                width=3
            )
            self.render_queue.append(op_line)
            
            # Draw box around anomaly
            op_box = RenderOp(
                command_type=RenderCommand.BOX,
                start=Position(anomaly.position.x - 1, anomaly.position.y - 1, anomaly.position.z - 1),
                end=Position(anomaly.position.x + 1, anomaly.position.y + 1, anomaly.position.z + 1),
                color=anomaly.color,
                label=anomaly.anomaly_type.value,
                width=2
            )
            self.render_queue.append(op_box)
            
            # Draw text label
            op_text = RenderOp(
                command_type=RenderCommand.TEXT,
                start=anomaly.position,
                end=Position(0, 0, 0),
                color=anomaly.color,
                label=anomaly.description,
                width=1
            )
            self.render_queue.append(op_text)

    def _render_chunk_grid(self, max_distance: float):
        """Render chunk boundary grid"""
        player_chunk_x = int(self.world.player_pos.x) >> 4
        player_chunk_z = int(self.world.player_pos.z) >> 4
        
        # Show chunks within render distance
        chunk_radius = int(max_distance / 16) + 1
        
        for dx in range(-chunk_radius, chunk_radius):
            for dz in range(-chunk_radius, chunk_radius):
                chunk_x = player_chunk_x + dx
                chunk_z = player_chunk_z + dz
                
                # Chunk corner coordinates
                x1 = chunk_x * 16
                z1 = chunk_z * 16
                x2 = x1 + 16
                z2 = z1 + 16
                
                # Draw chunk boundaries (simplified)
                op = RenderOp(
                    command_type=RenderCommand.GRID,
                    start=Position(x1, self.world.player_pos.y, z1),
                    end=Position(x2, self.world.player_pos.y, z2),
                    color=(100, 100, 100),
                    label="chunk",
                    width=1
                )
                self.render_queue.append(op)

    def print_report(self):
        """Print ESP report to console"""
        chests = self.world.get_blocks_by_type(BlockType.CHEST, 256)
        anomalies = self.detector.scan(256)
        
        print("\n" + "="*60)
        print("ESP RENDERING REPORT")
        print("="*60)
        print(f"Player Position: ({self.world.player_pos.x:.1f}, {self.world.player_pos.y:.1f}, {self.world.player_pos.z:.1f})")
        print(f"Player Rotation: Yaw {self.world.player_yaw:.1f}° Pitch {self.world.player_pitch:.1f}°")
        print()
        
        print(f"[CHESTS] {len(chests)} found:")
        for chest in sorted(chests, key=lambda c: c.distance_to(self.world.player_pos))[:10]:
            dist = chest.distance_to(self.world.player_pos)
            print(f"  📦 {chest.pos.x:.0f}, {chest.pos.y:.0f}, {chest.pos.z:.0f} ({dist:.1f}m)")
        if len(chests) > 10:
            print(f"  ... and {len(chests) - 10} more")
        print()
        
        print(f"[ANOMALIES] {len(anomalies)} detected:")
        for anom in anomalies[:10]:
            priority_bar = "█" * anom.priority
            print(f"  {priority_bar} {anom.anomaly_type.value}: {anom.description}")
            print(f"    Location: ({anom.position.x:.0f}, {anom.position.y:.0f}, {anom.position.z:.0f})")
            if anom.details:
                for key, value in list(anom.details.items())[:2]:
                    print(f"    {key}: {value}")
        if len(anomalies) > 10:
            print(f"  ... and {len(anomalies) - 10} more")
        print()
        
        print(f"[RENDER QUEUE] {len(self.render_queue)} commands")
        commands = {}
        for op in self.render_queue:
            cmd_type = op.command_type.value
            commands[cmd_type] = commands.get(cmd_type, 0) + 1
        for cmd_type, count in commands.items():
            print(f"  {cmd_type}: {count}")
        print()
