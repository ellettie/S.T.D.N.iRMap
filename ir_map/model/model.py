from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QFontDatabase
from .ir_manager import IRManager
from .track_generator import TrackGenerator
import numpy as np
import json
import os
import pickle
from enum import Enum

class PATH(Enum):
    CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
    TRACKS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'tracks')
    
class Model(QObject):
    
    track_updated = Signal(dict)
    config_updated = Signal(str, str, object)
    telemetry_updated = Signal(dict)
    ir_connected = Signal(dict)
    ir_disconnected = Signal()
    

    def __init__(self, ir_manager: IRManager):
        
        super().__init__()
        self.ir_manager = ir_manager
        
        self.ir_manager.ir_connected.connect(self._on_ir_connected)
        self.ir_manager.ir_disconnected.connect(self._on_ir_disconnected)
        self.ir_manager.telemetry_updated.connect(self.update_telemetry)    

        self.telemetry = self.ir_manager.telemetry.copy()
        self.init_track()
        
        self.config = self.load_config()
        
        self.track_generator = TrackGenerator()
        self.track_generator.track_updated.connect(self.update_track)
    
    def _on_ir_connected(self):
        self.load_track()
        self.telemetry['track_name'] = self.ir_manager.telemetry['track_name']
        self.update_telemetry(self.telemetry)
        self.ir_connected.emit(self.track_dict)
        
    def _on_ir_disconnected(self):
        self.save_track()
        self.track_generator.init_vars()
        self.track_dict = {'length': 0, 'updatable': True, 'points' : np.empty((0, 4), dtype=float)}
        self.track_updated.emit(self.track_dict)
        self.ir_disconnected.emit()
        
    def update_track(self, track_dict: dict):
        self.track_dict = track_dict.copy()
        self.track_updated.emit(track_dict)
        
    def update_telemetry(self, telemetry: dict):
        self.telemetry = telemetry.copy()
        self.track_generator.generate(self.track_dict, telemetry, self.ir_manager.state.ir_connected)
        self.telemetry_updated.emit(telemetry)
        
    def set_config(self, key1: str, key2: str, value: object):
        self.config[key1][key2] = value
        self.config_updated.emit(key1, key2, value)
        
    def set_track_updatable(self, updatable: bool):
        self.track_dict['updatable'] = updatable
        self.track_generator.is_invalid_lap = True
        self.track_updated.emit(self.track_dict)
        
    def delete_track(self):
        self.track_dict = {'length': 0, 'updatable': True, 'points' : np.empty((0, 4), dtype=float)}
        track_name = self.ir_manager.telemetry['track_name'].replace(' ', '_')
        track_path = os.path.join(PATH.TRACKS_PATH.value, f'{track_name}.pkl')
        if os.path.exists(track_path):
            try:
                os.remove(track_path)
            except Exception as e:
                print(f"Error deleting track: {e}")
        self.track_generator.is_invalid_lap = True
        self.track_updated.emit(self.track_dict)

    def init_track(self):
        self.track_dict = {'length': 0, 'updatable': True, 'points' : np.empty((0, 4), dtype=float)}
        
    def load_config(self):
        try:
            with open(PATH.CONFIG_PATH.value, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = {}

    def save_config(self):
        with open(PATH.CONFIG_PATH.value, 'w') as f:
            json.dump(self.config, f, indent=4)
            
    def load_track(self):
        track_name = self.ir_manager.telemetry['track_name'].replace(' ', '_')
        track_path = os.path.join(PATH.TRACKS_PATH.value, f'{track_name}.pkl')
        try:
            with open(track_path, 'rb') as f:
                self.track_dict = pickle.load(f)
                self.track_dict['points'] = np.array(self.track_dict['points'])
        except Exception as e:
            print(f"Error loading track: {e}")
            self.init_track()

    def save_track(self):
        if len(self.track_dict['points']) > 0:
            self.track_dict['points'] = self.track_dict['points'].tolist()
            if not os.path.exists(PATH.TRACKS_PATH.value):
                os.makedirs(PATH.TRACKS_PATH.value)
            track_name = self.ir_manager.telemetry['track_name'].replace(' ', '_')
            track_path = os.path.join(PATH.TRACKS_PATH.value, f'{track_name}.pkl')
            with open(track_path, 'wb') as f:
                pickle.dump(self.track_dict, f)

