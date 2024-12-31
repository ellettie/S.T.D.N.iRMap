from PySide6.QtCore import QObject, Signal, QThread
import irsdk
import time
import math

class State:
    ir_connected = False


class IRManagerWorker(QObject):
    
    state_updated = Signal(bool)
    ir_connected = Signal(dict)
    ir_disconnected = Signal()
    telemetry_updated = Signal(dict)
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.state = State()
        self.ir = irsdk.IRSDK()
        self.running = True
        self.init_telemetry()

    def run(self):
        while self.running:
            self.check_iracing()
            self.update_telemetry()
            time.sleep(0.016)  # 約60FPSの更新間隔

    def check_iracing(self):
        if self.state.ir_connected and not (self.ir.is_initialized and self.ir.is_connected):
            self.state.ir_connected = False
            self.state_updated.emit(self.state.ir_connected)
            self.ir.shutdown()
            print('irsdk disconnected')
            self.ir_disconnected.emit()
            self.telemetry['track_name'] = ''
        elif not self.state.ir_connected and self.ir.startup() and self.ir.is_initialized:
            self.state.ir_connected = True
            self.state_updated.emit(self.state.ir_connected)
            self.telemetry['track_name'] = self.ir['WeekendInfo']['TrackName']
            print('irsdk connected')
            self.ir_connected.emit(self.telemetry)

    def update_telemetry(self):
        if self.state.ir_connected:
            self.ir.freeze_var_buffer_latest()
            telemetry = {
                'track_name': self.ir['WeekendInfo']['TrackName'],
                'session_state': self.ir['SessionState'],
                'drivers': self.ir['DriverInfo']['Drivers'],
                'player_idx': self.ir['PlayerCarIdx'],
                'player_class': self.ir['PlayerCarClass'],
                'player_class_pos': self.ir['PlayerCarClassPosition'],
                'player_ld_pct': self.ir['LapDistPct'],
                'player_trk_surf': self.ir['PlayerTrackSurface'],
                'other_class_posts': self.ir['CarIdxClassPosition'],
                'other_ld_pcts': self.ir['CarIdxLapDistPct'],
                'other_trk_surfs': self.ir['CarIdxTrackSurface'],
                'yaw_north': -self.ir['YawNorth'] + math.pi/2,
                'vel_x': self.ir['VelocityX'],
                'vel_y': self.ir['VelocityY'],
                'vel_z': self.ir['VelocityZ'],
                'current_lap': self.ir['Lap'],
                'session_time': self.ir['SessionTime'],
                'is_on_track': self.ir['IsOnTrack'],
                'player_inc_cnt': self.ir['PlayerCarDriverIncidentCount'],
            }
            self.telemetry = telemetry
            # print(telemetry)
            self.telemetry_updated.emit(telemetry)

    def init_telemetry(self):
        self.telemetry = {
            'track_name': '',
            'session_state': 0,
            'drivers': [],
            'player_idx': 0,
            'player_class': 0,
            'player_class_pos': 0,
            'player_ld_pct': 0,
            'player_trk_surf': 0,
            'other_class_posts': [],
            'other_ld_pcts': [],
            'other_trk_surfs': [],
            'yaw_north': 0,
            'vel_x': 0,
            'vel_y': 0,
            'vel_z': 0,
            'current_lap': 0,
            'session_time': 0,
            'is_on_track': False,
            'player_inc_cnt': 0,
        }

    def stop(self):
        self.running = False
        self.finished.emit()


class IRManager(QObject):
    ir_connected = Signal()
    ir_disconnected = Signal()
    telemetry_updated = Signal(dict)

    def __init__(self):
        super().__init__()
        self.worker = IRManagerWorker()
        self.thread = QThread()
        
        self.state = State()
        self.telemetry = self.worker.telemetry.copy()

        # スレッドの初期化
        self.worker.moveToThread(self.thread)

        # シグナルとスロットの接続
        self.thread.started.connect(self.worker.run)
        self.worker.ir_connected.connect(self._on_ir_connected)
        self.worker.ir_disconnected.connect(self._on_ir_disconnected)
        self.worker.telemetry_updated.connect(self._on_telemetry_updated)
        self.worker.state_updated.connect(self._on_state_updated)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # スレッド開始
        self.thread.start()

    def _on_telemetry_updated(self, telemetry):
        self.telemetry = telemetry.copy()
        self.telemetry_updated.emit(telemetry)

    def _on_state_updated(self, state):
        self.state.ir_connected = state
        
    def _on_ir_disconnected(self):
        self.ir_disconnected.emit()
        
    def _on_ir_connected(self, telemetry):
        self.telemetry = telemetry.copy()
        self.ir_connected.emit()

    def stop(self):
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()
