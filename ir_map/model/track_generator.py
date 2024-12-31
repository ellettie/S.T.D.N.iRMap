from PySide6.QtCore import QObject, Signal
import numpy as np
import math
import time

class TrackGenerator(QObject):
    TARGET_LENGTH = 2000
    
    track_updated = Signal(dict)
    
    def __init__(self):
        super().__init__()
        
        self.point_store = np.empty((0, 4), dtype=float)
        
        self.init_vars()
        
    def generate(self, track_dict: dict, telemetry: dict, is_irsdk_connected: bool):
        if is_irsdk_connected:
            # print('generator called')
            self._check_is_lap_changed(telemetry)
            self._check_is_invalid_lap(telemetry)
            
            if telemetry['player_ld_pct'] > 0.5 and not self.is_lap_changed:
                if not self.is_invalid_lap and track_dict['updatable']:
                    if (len(self.point_store) < track_dict['length'] \
                    or track_dict['length'] == 0):
                        track_dict['points'] = self.point_store.copy()
                        track_dict['length'] = len(track_dict['points'])
                        track_dict['points'] = self.resample_points(track_dict['points'])
                        self.track_updated.emit(track_dict)
                        print(f'track updated: {track_dict["length"]}')

                self.point_store = np.empty((0, 4), dtype=float)
                self.prev_inc_cnt = telemetry['player_inc_cnt']
                self.is_invalid_lap = False
                self.is_lap_changed = True
                print(f'start generating: {telemetry["current_lap"]}')
                
            delta_time = telemetry['session_time'] - self.prev_session_time
            self.prev_session_time = telemetry['session_time']
            self.prev_lap = telemetry['current_lap']
            
            if telemetry['is_on_track'] and track_dict['updatable'] and len(self.point_store) < 100000:
                w_vel_x = telemetry['vel_x'] * math.cos(telemetry['yaw_north']) - telemetry['vel_y'] * math.sin(telemetry['yaw_north'])
                w_vel_y = telemetry['vel_x'] * math.sin(telemetry['yaw_north']) + telemetry['vel_y'] * math.cos(telemetry['yaw_north'])
                
                dx = w_vel_x * delta_time
                dy = w_vel_y * delta_time
                
                new_x = self.point_store[-1, 0] + dx if len(self.point_store) > 0 else 0
                new_y = self.point_store[-1, 1] - dy if len(self.point_store) > 0 else 0
                
                self.point_store = np.append(self.point_store, [[new_x, new_y, telemetry['player_ld_pct'], 1]], axis=0)
    
    def _check_is_lap_changed(self, telemetry: dict):
        if (telemetry['current_lap'] > self.prev_lap or telemetry['current_lap'] == 0) and telemetry['player_ld_pct'] <= 0.5 and self.is_lap_changed:
            self.is_lap_changed = False
            print(f'lap changed: {telemetry["current_lap"]}')
    
    def _check_is_invalid_lap(self, telemetry: dict):
        if not self.is_invalid_lap:
            if telemetry['session_state'] == 1 \
            or telemetry['player_trk_surf'] != 3 \
            or telemetry['player_inc_cnt'] > self.prev_inc_cnt:
                self.is_invalid_lap = True
                print(f'invalid lap: {telemetry["current_lap"]}')

    def resample_points(self, points: np.ndarray):
        if len(points) == 0:
            return points
        
        points = points[points[:, 2].argsort()]
        
        ld_pcts = points[:, 2]
        x_coords = points[:, 0]
        y_coords = points[:, 1]
        sec_num = points[:, 3]
        
        target_ld_pct = np.linspace(0.0, 1.0, self.TARGET_LENGTH)
        
        indices = np.abs(ld_pcts[:, None] - target_ld_pct).argmin(axis=0)
        
        indices = np.clip(indices, 0, len(ld_pcts) - 1)
        
        points = np.column_stack((x_coords[indices], y_coords[indices], target_ld_pct, sec_num[indices]))
        _, unique_indices = np.unique(points[:, 2], return_index=True)
        points = points[unique_indices]
        
        points = np.vstack((points, points[-1]))
        
        return points
                
    def init_vars(self):
        self.prev_lap = 0
        self.prev_inc_cnt = 0
        self.prev_session_time = 0
        self.is_lap_changed = True
        self.is_invalid_lap = True
