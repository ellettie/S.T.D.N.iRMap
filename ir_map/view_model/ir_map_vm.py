from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor
from ..model import Model
import os

class IRMapVM(QObject):
    
    track_updated = Signal(dict)
    config_updated = Signal(str, str, object)
    telemetry_updated = Signal(dict)
    ir_connected = Signal(dict)
    ir_disconnected = Signal() 
    is_overlay_movable_changed = Signal(bool)

    def __init__(self, model: Model):
        super().__init__()
        self.model = model
        
        self.model.track_updated.connect(self._on_track_updated)
        self.model.config_updated.connect(self._on_config_updated)
        self.model.telemetry_updated.connect(self._on_telemetry_updated)
        self.model.ir_connected.connect(self._on_ir_connected)
        self.model.ir_disconnected.connect(self._on_ir_disconnected)


        self.track_dict = self.model.track_dict.copy()
        self.init_config(self.model.config)
        self.telemetry = self.model.telemetry.copy()
        
        self.is_overlay_movable = False
        
    def _on_track_updated(self, track_dict: dict):
        self.track_dict = track_dict.copy()
        self.track_updated.emit(track_dict)
        
    def _on_config_updated(self, key1: str, key2: str, value: object):
        if key1 == 'color':
            value = QColor(value)
        if key1 == 'bool':
            value = bool(value)
        self.config[key1][key2] = value
        self.config_updated.emit(key1, key2, value)
        
    def _on_telemetry_updated(self, telemetry: dict):
        self.telemetry = telemetry.copy()
        for driver in self.telemetry['drivers']:
            driver['CarClassColor'] = QColor(hex(driver['CarClassColor']).replace('0x', '#'))
        self.telemetry_updated.emit(telemetry)
        
    def _on_ir_connected(self, track_dict: dict):
        self.track_dict = track_dict.copy()
        self.ir_connected.emit(track_dict)
        
    def _on_ir_disconnected(self):
        self.ir_disconnected.emit()

    def set_config(self, key1: str, key2: str, value: object):
        if key1 == 'color':
            value = value.name()
        if key1 == 'bool':
            value = bool(value)
        self.model.set_config(key1, key2, value)
        
    def set_track_updatable(self, updatable: bool):
        self.model.set_track_updatable(updatable)
        
    def set_is_overlay_movable(self, is_overlay_movable: bool):
        self.is_overlay_movable = is_overlay_movable
        self.is_overlay_movable_changed.emit(is_overlay_movable)
        
    def delete_track(self):
        print('delete_track')
        self.model.delete_track()
        
    def init_config(self, config: dict):
        self.config = config.copy()
        self.config['color'] = {key: QColor(value) for key, value in config['color'].items()}
