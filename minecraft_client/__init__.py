"""
Minecraft 1.21.10 ESP Client
Real-time chest detection and anomaly marking for Fabric servers
"""

__version__ = "1.0.0"
__author__ = "4nx01"

from minecraft_client.config import *
from minecraft_client.network import MinecraftClient
from minecraft_client.world import WorldState
from minecraft_client.anomaly_detector import AnomalyDetector
from minecraft_client.esp import ESPRenderer

__all__ = [
    "MinecraftClient",
    "WorldState",
    "AnomalyDetector",
    "ESPRenderer",
]
