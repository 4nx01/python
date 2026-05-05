"""
Minecraft Protocol Handler for 1.21.10 (Protocol 767)
"""

import socket
import struct
import asyncio
import logging
from typing import Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Position:
    x: float
    y: float
    z: float

    def distance_to(self, other: 'Position') -> float:
        return ((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)**0.5

class MinecraftClient:
    """Minecraft Protocol 767 (1.21.10) client"""
    
    def __init__(self, host: str, port: int, username: str):
        self.host = host
        self.port = port
        self.username = username
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.player_pos = Position(0, 64, 0)
        self.player_yaw = 0.0
        self.player_pitch = 0.0
        self.logger = logging.getLogger(self.__class__.__name__)

    async def connect(self) -> bool:
        """Establish connection to server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setblocking(False)
            loop = asyncio.get_event_loop()
            
            await loop.sock_connect(self.socket, (self.host, self.port))
            self.connected = True
            self.logger.info(f"Connected to {self.host}:{self.port}")
            
            # Send handshake
            await self._send_handshake()
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False

    async def _send_handshake(self):
        """Send handshake packet to server"""
        try:
            # Handshake packet
            packet = bytearray()
            packet.append(0x00)  # Packet ID
            self._write_varint(packet, 767)  # Protocol version
            self._write_string(packet, self.host)
            packet.extend(struct.pack('>H', self.port))
            packet.append(0x02)  # Login state
            
            await self._send_packet(packet)
            
            # Login start
            login_packet = bytearray()
            login_packet.append(0x00)  # Packet ID
            self._write_string(login_packet, self.username)
            
            await self._send_packet(login_packet)
            self.logger.info("Handshake and login sent")
        except Exception as e:
            self.logger.error(f"Handshake failed: {e}")

    async def _send_packet(self, data: bytearray):
        """Send packet to server"""
        if not self.socket:
            return
        
        try:
            # Add length prefix
            length = len(data)
            packet = bytearray()
            self._write_varint(packet, length)
            packet.extend(data)
            
            loop = asyncio.get_event_loop()
            await loop.sock_sendall(self.socket, packet)
        except Exception as e:
            self.logger.error(f"Packet send failed: {e}")

    async def receive_packets(self) -> Optional[bytearray]:
        """Receive packet from server"""
        if not self.socket:
            return None
        
        try:
            loop = asyncio.get_event_loop()
            data = await loop.sock_recv(self.socket, 4096)
            return bytearray(data) if data else None
        except BlockingIOError:
            return None
        except Exception as e:
            self.logger.error(f"Packet receive failed: {e}")
            return None

    def update_player_position(self, x: float, y: float, z: float, yaw: float = 0, pitch: float = 0):
        """Update player position and rotation"""
        self.player_pos = Position(x, y, z)
        self.player_yaw = yaw
        self.player_pitch = pitch

    @staticmethod
    def _write_varint(buffer: bytearray, value: int):
        """Write variable-length integer"""
        while (value & 0xFFFFFF80) != 0:
            buffer.append((value & 0x7F) | 0x80)
            value >>= 7
        buffer.append(value & 0x7F)

    @staticmethod
    def _write_string(buffer: bytearray, string: str):
        """Write string with length prefix"""
        encoded = string.encode('utf-8')
        MinecraftClient._write_varint(buffer, len(encoded))
        buffer.extend(encoded)

    @staticmethod
    def _read_varint(data: bytearray, offset: int) -> Tuple[int, int]:
        """Read variable-length integer, return (value, new_offset)"""
        result = 0
        shift = 0
        while True:
            if offset >= len(data):
                return 0, offset
            byte = data[offset]
            offset += 1
            result |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:
                break
            shift += 7
        return result, offset

    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            self.socket.close()
        self.connected = False
        self.logger.info("Disconnected")
