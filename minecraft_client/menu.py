"""
Interactive Menu System with Global Keybinds
Keybinds: P (Chest ESP), O (Anomaly Detection), L (Chunk Marking), RIGHT SHIFT (Full Menu)
"""

import logging
import json
import os
from typing import Dict, Callable
from threading import Thread
from pynput import keyboard

logger = logging.getLogger(__name__)

class FeatureConfig:
    """Manages feature toggles and persistence"""
    
    def __init__(self, config_file: str = "minecraft_client/menu_config.json"):
        self.config_file = config_file
        self.features: Dict[str, bool] = {
            "chest_esp": True,
            "anomaly_detection": True,
            "shulker_detection": True,
            "player_activity": True,
            "chest_clusters": True,
            "suspicious_entity": True,
            "chunk_marking": True,
            "auto_report": True,
        }
        self.load_config()

    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    saved = json.load(f)
                    self.features.update(saved)
                logger.info(f"Loaded menu config from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        else:
            self.save_config()

    def save_config(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.features, f, indent=2)
            logger.info(f"Saved menu config to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def toggle(self, feature: str) -> bool:
        """Toggle a feature on/off"""
        if feature in self.features:
            self.features[feature] = not self.features[feature]
            self.save_config()
            return self.features[feature]
        return False

    def set(self, feature: str, value: bool):
        """Set a feature state"""
        if feature in self.features:
            self.features[feature] = value
            self.save_config()

    def get(self, feature: str) -> bool:
        """Get feature state"""
        return self.features.get(feature, False)

    def enable_all(self):
        """Enable all features"""
        for key in self.features:
            self.features[key] = True
        self.save_config()

    def disable_all(self):
        """Disable all features"""
        for key in self.features:
            self.features[key] = False
        self.save_config()

    def get_status(self) -> str:
        """Get formatted status"""
        status = []
        for i, (name, enabled) in enumerate(self.features.items(), 1):
            icon = "🟢" if enabled else "🔴"
            display_name = name.replace('_', ' ').title()
            status.append(f"[{i}] {display_name:<25} {icon} {'ON' if enabled else 'OFF'}")
        return "\n".join(status)

class MenuSystem:
    """Global keybind menu system"""
    
    def __init__(self, features: FeatureConfig):
        self.features = features
        self.menu_open = False
        self.listener = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.callbacks: Dict[str, Callable] = {}

    def register_callback(self, feature: str, callback: Callable):
        """Register callback when feature is toggled"""
        self.callbacks[feature] = callback

    def start_keybind_listener(self):
        """Start listening for global keybinds"""
        def on_press(key):
            try:
                if key == keyboard.Key.right_shift:
                    self.toggle_menu()
                elif key == keyboard.Key.f:
                    # P key
                    if hasattr(key, 'char') and key.char == 'p':
                        self._handle_feature_toggle("chest_esp")
                elif key == keyboard.Key.o:
                    # O key
                    self._handle_feature_toggle("anomaly_detection")
                elif key == keyboard.Key.l:
                    # L key
                    self._handle_feature_toggle("chunk_marking")
            except AttributeError:
                pass

        def on_release(key):
            pass

        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.listener.start()
        self.logger.info("Keybind listener started")

    def _handle_feature_toggle(self, feature: str):
        """Handle feature toggle"""
        state = self.features.toggle(feature)
        status = "ON" if state else "OFF"
        print(f"\n✓ {feature.replace('_', ' ').title()} turned {status}")
        
        if feature in self.callbacks:
            self.callbacks[feature](state)

    def toggle_menu(self):
        """Toggle menu visibility"""
        self.menu_open = not self.menu_open
        if self.menu_open:
            self.show_menu()
        else:
            print("\nMenu closed.\n")

    def show_menu(self):
        """Display interactive menu"""
        while self.menu_open:
            print("\n" + "="*60)
            print("MINECRAFT ESP CLIENT - FEATURE MENU")
            print("="*60)
            print(self.features.get_status())
            print("\n[A] Enable All        [D] Disable All")
            print("[Q] Close Menu")
            print("="*60)
            
            try:
                choice = input("\n> Enter choice: ").strip().lower()
                
                if choice == 'q':
                    self.menu_open = False
                    print("\nMenu closed.\n")
                    break
                
                elif choice == 'a':
                    self.features.enable_all()
                    print("\n✓ All features ENABLED")
                    for feature, callback in self.callbacks.items():
                        callback(True)
                
                elif choice == 'd':
                    self.features.disable_all()
                    print("\n✓ All features DISABLED")
                    for feature, callback in self.callbacks.items():
                        callback(False)
                
                elif choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                    feature_list = list(self.features.features.keys())
                    idx = int(choice) - 1
                    if 0 <= idx < len(feature_list):
                        feature = feature_list[idx]
                        self._handle_feature_toggle(feature)
                
                else:
                    print("\n✗ Invalid choice. Try again.")
            
            except KeyboardInterrupt:
                self.menu_open = False
                print("\n\nMenu closed.\n")
                break
            except Exception as e:
                self.logger.error(f"Menu error: {e}")
                break

    def stop(self):
        """Stop keybind listener"""
        if self.listener:
            self.listener.stop()
            self.logger.info("Keybind listener stopped")

class KeybindHandler:
    """Handles keybind input with pynput"""
    
    def __init__(self):
        self.shift_pressed = False
        self.right_pressed = False
        self.logger = logging.getLogger(self.__class__.__name__)
        self.callbacks = {}

    def register_callback(self, key_combo: str, callback: Callable):
        """Register callback for key combination
        
        Examples:
            'p' -> P key
            'o' -> O key
            'l' -> L key
            'shift+right' -> SHIFT+RIGHT
        """
        self.callbacks[key_combo.lower()] = callback

    def start(self):
        """Start listening to keyboard"""
        def on_press(key):
            try:
                # Check for individual keys
                if hasattr(key, 'char'):
                    if key.char == 'p' and 'p' in self.callbacks:
                        self.callbacks['p']()
                    elif key.char == 'o' and 'o' in self.callbacks:
                        self.callbacks['o']()
                    elif key.char == 'l' and 'l' in self.callbacks:
                        self.callbacks['l']()
                
                # Check for RIGHT SHIFT
                if key == keyboard.Key.shift_r:
                    if 'shift+right' in self.callbacks:
                        self.callbacks['shift+right']()
            
            except AttributeError:
                pass

        def on_release(key):
            pass

        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
        self.logger.info("Keybind handler started")
        self.logger.info("Available keybinds: P, O, L, SHIFT+RIGHT")
        return listener
