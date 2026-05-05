"""
Main Application Loop - Minecraft ESP Client
"""

import asyncio
import logging
import time
from minecraft_client.config import *
from minecraft_client.network import MinecraftClient, Position
from minecraft_client.world import WorldState, BlockType
from minecraft_client.anomaly_detector import AnomalyDetector
from minecraft_client.esp import ESPRenderer

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler() if CONSOLE_OUTPUT else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

class MinecraftESPClient:
    """Main ESP Client Application"""
    
    def __init__(self):
        self.client = MinecraftClient(SERVER_HOST, SERVER_PORT, USERNAME)
        self.world = WorldState()
        self.detector = AnomalyDetector(self.world)
        self.renderer = ESPRenderer(self.world, self.detector)
        self.running = False
        self.ticks = 0
        self.logger = logging.getLogger(self.__class__.__name__)

    async def run(self):
        """Main game loop (20 TPS)"""
        self.running = True
        self.logger.info("Starting Minecraft ESP Client...")
        
        # Connect to server
        if not await self.client.connect():
            self.logger.error("Failed to connect to server")
            return
        
        try:
            tick_duration = 1.0 / 20  # 20 TPS
            last_render = 0
            
            while self.running:
                start_tick = time.time()
                self.ticks += 1
                
                # Update player from client
                self.world.update_player(
                    self.client.player_pos.x,
                    self.client.player_pos.y,
                    self.client.player_pos.z,
                    self.client.player_yaw,
                    self.client.player_pitch
                )
                
                # Receive packets
                packet = await self.client.receive_packets()
                if packet:
                    await self._process_packet(packet)
                
                # Periodic rendering (every 20 ticks = 1 second)
                if self.ticks % 20 == 0:
                    self.renderer.render(ESP_RENDER_DISTANCE)
                    if CONSOLE_OUTPUT:
                        self.renderer.print_report()
                
                # Cleanup distant chunks every 40 ticks
                if self.ticks % 40 == 0:
                    self.world.cleanup_distant_chunks(CHUNK_CLEANUP_DISTANCE)
                
                # Maintain 20 TPS
                elapsed = time.time() - start_tick
                sleep_time = tick_duration - elapsed
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
        
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}", exc_info=True)
        finally:
            self.stop()

    async def _process_packet(self, packet: bytearray):
        """Process incoming packet from server"""
        # This is a mock implementation
        # Real implementation would parse Minecraft protocol packets
        pass

    def stop(self):
        """Stop the client"""
        self.running = False
        self.client.disconnect()
        self.logger.info(f"Client stopped after {self.ticks} ticks")

    def mock_world(self):
        """Populate world with test data for development"""
        self.logger.info("Populating mock world...")
        
        # Add some chests
        self.world.add_block(1000, 64, 2000, BlockType.CHEST)
        self.world.add_block(1002, 64, 2000, BlockType.CHEST)
        self.world.add_block(1004, 64, 2000, BlockType.CHEST)
        self.world.add_block(1006, 64, 2000, BlockType.CHEST)
        
        # Add work blocks (player activity)
        self.world.add_block(1010, 64, 2010, BlockType.FURNACE)
        self.world.add_block(1011, 64, 2010, BlockType.CRAFTING_TABLE)
        self.world.add_block(1012, 64, 2010, BlockType.ANVIL)
        
        # Add shulker boxes (highest priority)
        self.world.add_block(1005, 65, 2005, BlockType.SHULKER_BOX, {"color": "purple"})
        self.world.add_block(1006, 65, 2005, BlockType.SHULKER_BOX, {"color": "purple"})
        
        # Add entities
        self.world.add_entity(1, "armor_stand", 1020, 64, 2020, 0, 0)
        self.world.add_entity(2, "armor_stand", 1021, 64, 2020, 0, 0)
        self.world.add_entity(3, "item_frame", 1022, 64, 2020, 0, 0)
        
        # Set player position
        self.world.update_player(1024, 64, 2024, 0, 0)
        
        self.logger.info("Mock world populated")

async def main():
    """Entry point"""
    client = MinecraftESPClient()
    
    # Use mock world for testing (remove for real server)
    client.mock_world()
    
    await client.run()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Minecraft 1.21.10 ESP Client (Fabric)")
    print("Real-time Chest ESP & Anomaly Detection")
    print("="*60 + "\n")
    
    asyncio.run(main())
