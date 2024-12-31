from PySide6.QtWidgets import QMainWindow, QApplication, QWidget
from PySide6.QtGui import QPainter, QPainterPath, QPen, QColor, QFont, QIcon, QFontDatabase
from PySide6.QtCore import Qt, QPointF, QRectF, QPoint
from ..view_model.ir_map_vm import IRMapVM
import numpy as np
import os
from enum import Enum
import time

class PATH(Enum):
    ICON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets/icon/icon.ico')
    FONT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets/fonts/Gemunu_Libre/static/GemunuLibre-SemiBold.ttf')

class IRMap(QMainWindow):
    
    def set_window_geometry(self):
        self.window_x = self.screen_geometry.width() * self.config['geometry']['x']
        self.window_y = self.screen_geometry.height() * self.config['geometry']['y']
        self.ajust_size_values()
        self.setGeometry(self.window_x, self.window_y, self.window_size, self.window_size)
    
    def __init__(self, vm: IRMapVM):
        super().__init__()
          
        self.vm = vm
        self.vm.track_updated.connect(self._on_track_ready)
        self.vm.config_updated.connect(self._on_config_ready)
        self.vm.telemetry_updated.connect(self._on_telemetry_ready)
        self.vm.ir_connected.connect(self._on_ir_connected)
        self.vm.ir_disconnected.connect(self._on_ir_disconnected)
        self.vm.is_overlay_movable_changed.connect(self._on_is_overlay_movable_changed)

        self.track_dict = self.vm.track_dict.copy()
        self.config = self.vm.config.copy()
        self.telemetry = self.vm.telemetry.copy()
        self.draw_points = self.rescale_track(self.track_dict['points'])
        self.static_path = self.create_static_path()
        self.is_overlay_movable = self.vm.is_overlay_movable
        self.drag_pos = QPoint()

        self.setWindowTitle("S.T.D.N.iRMap")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.set_window_geometry()
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        try:
            self.setWindowIcon(QIcon(PATH.ICON_PATH.value))
        except Exception as e:
            print(f"Error setting window icon: {e}")
            
        try:
            font_id = QFontDatabase.addApplicationFont(PATH.FONT_PATH.value)
            self.font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        except Exception as e:
            print(f"Error loading font: {e}")
            self.font_family = "Arial"
            
        self.font_family = QFont(self.font_family)
        
    def _on_track_ready(self, track_dict: dict):
        self.track_dict = track_dict.copy()
        self.draw_points = self.rescale_track(self.track_dict['points'])
        self.static_path = self.create_static_path()

    def _on_config_ready(self, key1: str, key2: str, value: object):
        self.config[key1][key2] = value
        if key2 in ['window_size', 'opacity', 'track_width', 'track_outline_width', 'car_size', 'car_outline_width']:
            self.ajust_size_values()
        self.update()

    def _on_telemetry_ready(self, telemetry: dict):
        self.telemetry = telemetry.copy()
        self.update()
        
    def _on_ir_connected(self, track_dict: dict):
        self.track_dict = track_dict.copy()
        self.draw_points = self.rescale_track(self.track_dict['points'])
        self.static_path = self.create_static_path()
        self.show()
        
    def _on_ir_disconnected(self):
        self.hide()
        
    def _on_is_overlay_movable_changed(self, is_overlay_movable: bool):
        if is_overlay_movable:
            self.central_widget.setStyleSheet("background-color: rgba(255, 255, 255, 150);")
            self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        else:
            self.central_widget.setStyleSheet("background-color: transparent;")
            self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowTransparentForInput)
        
        self.is_overlay_movable = is_overlay_movable
        self.show()
        
    def ajust_size_values(self):
        self.window_size = self.screen_geometry.height() * self.config['geometry']['window_size']
        self.resize(self.window_size, self.window_size)
        self.setWindowOpacity(self.config['geometry']['opacity'])
        self.track_width = self.config['number']['track_width'] * self.window_size / 1000
        self.track_outline_width = self.config['number']['track_outline_width'] * self.window_size / 1000
        self.car_size = self.config['number']['car_size'] * self.window_size / 1000
        self.car_outline_width = self.car_size * self.config['number']['car_outline_width'] / 50

    def rescale_track(self, points: np.ndarray): 
        if len(points) == 0 or self.window_size == 0:
            return points
        
        min_x = np.min(points[:, 0])
        max_x = np.max(points[:, 0])
        min_y = np.min(points[:, 1])
        max_y = np.max(points[:, 1]) 
        track_width = max_x - min_x
        track_height = max_y - min_y
        
        scale_x = self.width() / track_width if track_width > 0 else 1
        scale_y = self.height() / track_height if track_height > 0 else 1
        scale = min(scale_x, scale_y) * 0.9
        
        offset_x = (self.width() - track_width * scale) / 2 - min_x * scale
        offset_y = (self.height() - track_height * scale) / 2 - min_y * scale
        
        points[:, 0] = points[:, 0] * scale + offset_x
        points[:, 1] = points[:, 1] * scale + offset_y
        
        return points
    
    def create_static_path(self):
        # print(len(self.draw_points))
        if len(self.draw_points) < 2:
            return QPainterPath()
        
        path = QPainterPath()
        start_x = self.draw_points[0, 0]
        start_y = self.draw_points[0, 1]
        path.moveTo(start_x, start_y)
            
        for i in range(1, len(self.draw_points)):
            x = self.draw_points[i, 0]
            y = self.draw_points[i, 1]
            path.lineTo(x, y)
        
        return path
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.transparent)
        if len(self.draw_points) > 1:
            
            # draw the track
            
            outline_pen = QPen(self.config['color']['outline_color'], self.track_width + self.track_outline_width * 2)
            painter.setPen(outline_pen)
            painter.drawPath(self.static_path)
                
            painter.setPen(QPen(self.config['color']['track_color'], self.track_width))
            painter.drawPath(self.static_path)
            
            # # draw the s/f line
            painter.save()
            first_point = self.draw_points[0]
            last_point = self.draw_points[-1]
            angle = np.arctan2(last_point[1] - first_point[1], last_point[0] - first_point[0]) * 180 / np.pi
            rect_x = first_point[0]
            rect_y = first_point[1]
            
            painter.translate(rect_x, rect_y)
            painter.rotate(angle)
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.config['color']['sf_color'])
            sf_height = self.track_width + self.track_outline_width * 2
            painter.drawRect(-self.track_width / 3, -sf_height / 2, self.track_width / 3 * 2, sf_height)
            
            painter.restore()
            
            # draw cars
            for driver in self.telemetry['drivers']:
                painter.save()
                car_idx = driver['CarIdx']
                car_class_position = self.telemetry['other_class_posts'][car_idx]
                car_number = driver['CarNumber']
                car_class_color = driver['CarClassColor']
                closest_point = np.argmin(
                    np.abs(self.draw_points[:, 2] - self.telemetry['other_ld_pcts'][car_idx])
                )
                car_position = self.draw_points[closest_point, :2]
                car_x = car_position[0]
                car_y = car_position[1]
                
                if car_idx == self.telemetry['player_idx']:
                    painter.setPen(QPen(self.config['color']['player_outline_color'], self.car_outline_width))
                    painter.setBrush(self.config['color']['player_color'])
                    car_size = self.car_size * self.config['number']['player_scale']
                else:
                    painter.setPen(Qt.NoPen)
                    if driver['CarClassID'] == self.telemetry['player_class']:
                        if car_class_position == self.telemetry['player_class_pos'] - 1 and self.telemetry['player_class_pos'] -1 > 0:
                            painter.setPen(QPen(self.config['color']['next_outline_color'], self.car_outline_width))
                        if car_class_position == self.telemetry['player_class_pos'] + 1 and self.telemetry['player_class_pos'] > 0:
                            painter.setPen(QPen(self.config['color']['prev_outline_color'], self.car_outline_width))
                        painter.setOpacity(self.config['number']['other_car_opacity'])
                    else:
                        painter.setOpacity(self.config['number']['other_class_opacity']*self.config['number']['other_car_opacity'])
                    if car_class_color == QColor(255, 255, 255):
                        car_class_color = self.config['color']['other_color']
                    painter.setBrush(car_class_color)
                    car_size = self.car_size

                if self.telemetry['other_trk_surfs'][car_idx] == 1 or self.telemetry['other_trk_surfs'][car_idx] == 2:
                    painter.setOpacity(0.4)
                if self.telemetry['other_trk_surfs'][car_idx] == -1:
                    painter.setOpacity(0.0)
                    
                painter.drawEllipse(QPointF(car_x, car_y), car_size, car_size)
                
                painter.setPen(QColor(self.config['color']['number_color']))
                self.font_family.setPointSizeF(car_size * 0.8)
                painter.setFont(self.font_family)
                s = car_size * 2
                text_rect = QRectF(
                    car_x - s / 2, 
                    car_y - s / 2, 
                    s, 
                    s
                )
                if self.config['bool']['show_position']:
                    car_number = str(car_class_position) if car_class_position > 0 else '-'
                painter.drawText(text_rect, Qt.AlignCenter, str(car_number))
                
                painter.restore()

    def resizeEvent(self, event):
        if len(self.track_dict['points']) > 0:  
            self.draw_points = self.rescale_track(self.track_dict['points'])
            self.static_path = self.create_static_path()
        event.accept()
        
    def mousePressEvent(self, event):
        if self.is_overlay_movable and event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if self.is_overlay_movable and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if self.is_overlay_movable and event.button() == Qt.LeftButton:
            self.drag_pos = None
            x = round(self.x() / self.screen_geometry.width(), 4)
            y = round(self.y() / self.screen_geometry.height(), 4)
            self.vm.set_config('geometry', 'x', x)
            self.vm.set_config('geometry', 'y', y)
            event.accept()

