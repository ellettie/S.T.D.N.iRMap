from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMainWindow, QApplication, QDoubleSpinBox, QColorDialog, QMessageBox, QCheckBox
from PySide6.QtGui import QIcon, QColor
from PySide6.QtCore import Qt, Signal
from ..view_model.ir_map_vm import IRMapVM
import os
from enum import Enum

class PATH(Enum):
    ICON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets/icon/icon.ico')

class SpinBoxWidget(QWidget):
    def __init__(self, label, value, min_value, max_value, step, decimals):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.label = QLabel(label)
        self.layout.addWidget(self.label)
        self.spinBox = QDoubleSpinBox()
        self.spinBox.setRange(min_value, max_value)
        self.spinBox.setSingleStep(step)
        self.spinBox.setDecimals(decimals)
        self.spinBox.setValue(value)
        self.layout.addWidget(self.spinBox)
        
    def setText(self, text):
        self.label.setText(text)
        
class ColorWidget(QWidget):
    
    color_changed = Signal(QColor)
    
    def __init__(self, label, color):
        super().__init__()
        self.color_dialog = QColorDialog()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.label = QLabel(label)
        self.layout.addWidget(self.label)
        self.colorButton = QPushButton()
        self.set_color(color)
        self.colorButton.clicked.connect(self.open_color_dialog)
        self.layout.addWidget(self.colorButton)
        
    def setText(self, text):
        self.label.setText(text)
        
    def set_color(self, color):
        self.colorButton.setStyleSheet(f'background-color: {color.name()};')
        
    def open_color_dialog(self):
        selected_color = self.color_dialog.getColor()
        if selected_color.isValid():
            self.color_changed.emit(selected_color)
            
class CheckBoxWidget(QWidget):
    def __init__(self, label, value):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.label = QLabel(label)
        self.layout.addWidget(self.label)
        self.checkBox = QCheckBox()
        self.checkBox.setChecked(value)
        self.layout.addWidget(self.checkBox)
        
    def setText(self, text):
        self.label.setText(text)
        
class ConfigUI(QMainWindow):
    
    labels = {'ja' : {'Language' : 'English', 'Set Movable' : '位置を変更', 'Set Fixed' : '位置を固定',
                      'Opacity' : '不透明度', 'Window Size' : 'ウィンドウサイズ', 'Delete Track' : 'トラックを削除',
                      'Set Updatable' : '更新可能にする', 'Set Unupdatable' : '更新不可にする', 'Open Advanced' : '詳細設定を開く',
                      'Close Advanced' : '詳細設定を閉じる', 'Track Width' : 'コースの太さ', 'Track Outline Width' : 'コースの輪郭線の太さ',
                      'Car Outline Width' : '車の輪郭線の太さ', 'Car Size' : '車の大きさ', 'Player Scale' : '自車の大きさ',
                      'Track Color' : 'コースの色', 'Track Outline Color' : 'コースの輪郭線の色', 'Player Color' : '自車の色',
                      'Player Outline Color' : '自車の輪郭線の色', 'Other Color' : '他車の色', 'Next Outline Color' : '前の車の色',
                      'Prev Outline Color' : '後ろの車の色', 'Other Car Opacity' : '他車の不透明度', 'Other Class Opacity' : '他クラスの不透明度',
                      'Number Color' : '数字の色', 'Show Position' : '順位で表示'},
              'en' : {'Language' : '日本語', 'Set Movable' : 'Move Position', 'Set Fixed' : 'Fix Position',
                      'Opacity' : 'Opacity', 'Window Size' : 'Window Size', 'Delete Track' : 'Delete Track',
                      'Set Updatable' : 'Set Updatable', 'Set Unupdatable' : 'Set Unupdatable', 'Open Advanced' : 'Open Advanced',
                      'Close Advanced' : 'Close Advanced', 'Track Width' : 'Track Width', 'Track Outline Width' : 'Track Outline Width',
                      'Car Outline Width' : 'Car Outline Width', 'Car Size' : 'Car Size', 'Player Scale' : 'Player Scale',
                      'Track Color' : 'Track Color', 'Track Outline Color' : 'Track Outline Color', 'Player Color' : 'Player Car Color',
                      'Player Outline Color' : 'Player Outline Color', 'Other Color' : 'Other Car Color', 'Next Outline Color' : 'Next Car Color',
                      'Prev Outline Color' : 'Prev Car Color', 'Other Car Opacity' : 'Other Car Opacity', 'Other Class Opacity' : 'Other Class Opacity',
                      'Number Color' : 'Number Color', 'Show Position' : 'Show Position'},
              }
    
    def __init__(self, vm: IRMapVM):
        super().__init__()
 
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        
        self.is_advanced_open = False
        
        self.vm = vm
        self.vm.config_updated.connect(self._on_config_updated)
        self.vm.track_updated.connect(self._on_track_updated)
        self.vm.telemetry_updated.connect(self._on_telemetry_updated)
        self.vm.ir_connected.connect(self._on_ir_connected)
        self.vm.ir_disconnected.connect(self._on_ir_disconnected)
        
        self.config = self.vm.config.copy()
        self.track_dict = self.vm.track_dict.copy()
        self.telemetry = self.vm.telemetry.copy()
        self.is_overlay_movable = self.vm.is_overlay_movable

        self.setWindowTitle('S.T.D.N.iRMap - Config')
        
        self.aspect_ratio = 0.6
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)       
        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)
        width = 450
        height = int(width * self.aspect_ratio)
        self.resize(width, height)
        self.setMinimumSize(width, height)
        
        self.set_widgets()
        
        try:
            self.setWindowIcon(QIcon(PATH.ICON_PATH.value))
        except Exception as e:
            print(f"Error setting window icon: {e}")
        
        self.widgets['Language'].clicked.connect(lambda: self.lang_button_slot())
        self.widgets['Set Movable'].clicked.connect(lambda: self.move_button_slot())
        self.widgets['Opacity'].spinBox.valueChanged.connect(lambda value: self.vm.set_config('geometry', 'opacity', round(value, 2)))
        self.widgets['Window Size'].spinBox.valueChanged.connect(lambda value: self.vm.set_config('geometry', 'window_size', round(value, 2)))
        self.widgets['Open Advanced'].clicked.connect(lambda: self.advanced_button_slot())
        self.change_updatable_button.clicked.connect(lambda: self.updatable_button_slot())
        self.delete_track_button.clicked.connect(lambda: self.delete_track_slot())

    def _on_config_updated(self, key1: str, key2: str, value: object):
        self.config[key1][key2] = value
        self.set_labels()

    def _on_track_updated(self, track_dict: dict):
        self.track_dict = track_dict.copy()
        self.set_labels()
        
    def _on_telemetry_updated(self, telemetry: dict):
        self.telemetry = telemetry.copy()
        
    def _on_ir_connected(self, track_dict: dict):
        self.track_dict = track_dict.copy()
        self.widgets['Track Name'].setText(self.telemetry['track_name'])
        self.set_labels()
        
    def _on_ir_disconnected(self):
        self.widgets['Track Name'].setText('')
        
    def set_widgets(self):
        self.widgets = {
            'Language': QPushButton(self.labels[self.config['ui']['language']]['Language']),
            'Set Movable': QPushButton(self.labels[self.config['ui']['language']]['Set Movable']),
            'Opacity': SpinBoxWidget(self.labels[self.config['ui']['language']]['Opacity'], self.config['geometry']['opacity'], 0.0, 1.0, 0.01, 2),
            'Window Size': SpinBoxWidget(self.labels[self.config['ui']['language']]['Window Size'], self.config['geometry']['window_size'], 0.1, 1.0, 0.01, 2),
            'Open Advanced': QPushButton(self.labels[self.config['ui']['language']]['Open Advanced']),
            'Advanced': QWidget(),
            'Bottom Buttons': QWidget(),
            'Track Name': QLabel(self.telemetry['track_name']),
        }
        
        self.set_bottom_widget()
        
        for widget in self.widgets.values():
            self.main_layout.addWidget(widget)
            
    def set_bottom_widget(self):
        self.bottom_buttons_layout = QHBoxLayout()
        self.widgets['Bottom Buttons'].setLayout(self.bottom_buttons_layout)
        
        self.delete_track_button = QPushButton(self.labels[self.config['ui']['language']]['Delete Track'])
        self.change_updatable_button = QPushButton(self.labels[self.config['ui']['language']]['Set Updatable'] if not self.track_dict['updatable'] else self.labels[self.config['ui']['language']]['Set Unupdatable'])
        self.bottom_buttons_layout.addWidget(self.delete_track_button)
        self.bottom_buttons_layout.addWidget(self.change_updatable_button)

    def set_advanced_widget(self):
        self.advanced_widgets = {
            'Track Width': SpinBoxWidget(self.labels[self.config['ui']['language']]['Track Width'], self.config['number']['track_width'], 1, 50, 1, 0),
            'Track Outline Width': SpinBoxWidget(self.labels[self.config['ui']['language']]['Track Outline Width'], self.config['number']['track_outline_width'], 1, 20, 1, 0),
            'Car Size': SpinBoxWidget(self.labels[self.config['ui']['language']]['Car Size'], self.config['number']['car_size'], 1, 40, 1, 0),
            'Player Scale': SpinBoxWidget(self.labels[self.config['ui']['language']]['Player Scale'], self.config['number']['player_scale'], 0.1, 2.0, 0.1, 2),
            'Car Outline Width': SpinBoxWidget(self.labels[self.config['ui']['language']]['Car Outline Width'], self.config['number']['car_outline_width'], 1, 20, 1, 0),
            'Other Car Opacity': SpinBoxWidget(self.labels[self.config['ui']['language']]['Other Car Opacity'], self.config['number']['other_car_opacity'], 0.1, 1.0, 0.1, 2),
            'Other Class Opacity': SpinBoxWidget(self.labels[self.config['ui']['language']]['Other Class Opacity'], self.config['number']['other_class_opacity'], 0.1, 1.0, 0.1, 2),
            'Show Position': CheckBoxWidget(self.labels[self.config['ui']['language']]['Show Position'], self.config['bool']['show_position']),
            'Track Color': ColorWidget(self.labels[self.config['ui']['language']]['Track Color'], self.config['color']['track_color']),
            'Track Outline Color': ColorWidget(self.labels[self.config['ui']['language']]['Track Outline Color'], self.config['color']['outline_color']),
            'Player Color': ColorWidget(self.labels[self.config['ui']['language']]['Player Color'], self.config['color']['player_color']),
            'Player Outline Color': ColorWidget(self.labels[self.config['ui']['language']]['Player Outline Color'], self.config['color']['player_outline_color']),
            'Other Color': ColorWidget(self.labels[self.config['ui']['language']]['Other Color'], self.config['color']['other_color']),
            'Next Outline Color': ColorWidget(self.labels[self.config['ui']['language']]['Next Outline Color'], self.config['color']['next_outline_color']),
            'Prev Outline Color': ColorWidget(self.labels[self.config['ui']['language']]['Prev Outline Color'], self.config['color']['prev_outline_color']),
            'Number Color': ColorWidget(self.labels[self.config['ui']['language']]['Number Color'], self.config['color']['number_color']),
        }
        
        self.advanced_widgets_left = QVBoxLayout()
        self.advanced_widgets_right = QVBoxLayout()
        self.advanced_layout.addLayout(self.advanced_widgets_left)
        self.advanced_layout.addLayout(self.advanced_widgets_right)
        
        for key, widget in self.advanced_widgets.items():
            if key in ['Track Width', 'Track Outline Width', 'Car Outline Width', 'Car Size', 'Player Scale', 'Other Car Opacity', 'Other Class Opacity', 'Show Position']:
                self.advanced_widgets_left.addWidget(widget)
            else:
                self.advanced_widgets_right.addWidget(widget)
            
        self.advanced_widgets['Track Width'].spinBox.valueChanged.connect(lambda value: self.vm.set_config('number', 'track_width', int(value)))
        self.advanced_widgets['Track Outline Width'].spinBox.valueChanged.connect(lambda value: self.vm.set_config('number', 'track_outline_width', int(value)))
        self.advanced_widgets['Car Outline Width'].spinBox.valueChanged.connect(lambda value: self.vm.set_config('number', 'car_outline_width', int(value)))
        self.advanced_widgets['Car Size'].spinBox.valueChanged.connect(lambda value: self.vm.set_config('number', 'car_size', int(value)))
        self.advanced_widgets['Player Scale'].spinBox.valueChanged.connect(lambda value: self.vm.set_config('number', 'player_scale', round(value, 2)))
        self.advanced_widgets['Other Car Opacity'].spinBox.valueChanged.connect(lambda value: self.vm.set_config('number', 'other_car_opacity', round(value, 2)))
        self.advanced_widgets['Other Class Opacity'].spinBox.valueChanged.connect(lambda value: self.vm.set_config('number', 'other_class_opacity', round(value, 2)))
        self.advanced_widgets['Show Position'].checkBox.stateChanged.connect(lambda state: self.vm.set_config('bool', 'show_position', state))
        self.advanced_widgets['Track Color'].color_changed.connect(lambda color: self.vm.set_config('color', 'track_color', color))
        self.advanced_widgets['Track Outline Color'].color_changed.connect(lambda color: self.vm.set_config('color', 'outline_color', color))
        self.advanced_widgets['Player Color'].color_changed.connect(lambda color: self.vm.set_config('color', 'player_color', color))
        self.advanced_widgets['Player Outline Color'].color_changed.connect(lambda color: self.vm.set_config('color', 'player_outline_color', color))
        self.advanced_widgets['Other Color'].color_changed.connect(lambda color: self.vm.set_config('color', 'other_color', color))
        self.advanced_widgets['Next Outline Color'].color_changed.connect(lambda color: self.vm.set_config('color', 'next_outline_color', color))
        self.advanced_widgets['Prev Outline Color'].color_changed.connect(lambda color: self.vm.set_config('color', 'prev_outline_color', color))
        self.advanced_widgets['Number Color'].color_changed.connect(lambda color: self.vm.set_config('color', 'number_color', color))

    def lang_button_slot(self): 
        self.vm.set_config('ui', 'language', 'en' if self.config['ui']['language'] == 'ja' else 'ja')
        
    def move_button_slot(self):
        if not self.is_overlay_movable:
            self.widgets['Set Movable'].setText(self.labels[self.config['ui']['language']]['Set Fixed'])
            self.vm.set_is_overlay_movable(True)
        else:
            self.widgets['Set Movable'].setText(self.labels[self.config['ui']['language']]['Set Movable'])
            self.vm.set_is_overlay_movable(False)
        self.is_overlay_movable = not self.is_overlay_movable

    def updatable_button_slot(self):
        if self.track_dict['length'] == 0:
            return      
        if self.track_dict['updatable']:
            self.vm.set_track_updatable(False)
        else:
            self.vm.set_track_updatable(True)
            
    def delete_track_slot(self):
        if self.telemetry['track_name'] == '':
            return
        message = {'ja' : 'トラックを削除しますか？', 'en' : 'Delete track?'}
        response = self.open_msg_box(QMessageBox.Question, 'Delete Track', message[self.config['ui']['language']])
        if response == QMessageBox.Yes:
            self.vm.delete_track()
        
    def advanced_button_slot(self):
        if self.is_advanced_open:
            self.close_advanced_widget()
            self.widgets['Open Advanced'].setText(self.labels[self.config['ui']['language']]['Open Advanced'])
            self.aspect_ratio = 0.6
            width = self.width()
            height = int(width * self.aspect_ratio)
            self.resize(width, height)
        else:
            self.open_advanced_widget()
            self.widgets['Open Advanced'].setText(self.labels[self.config['ui']['language']]['Close Advanced'])
            self.aspect_ratio = 1.4
            width = self.width()
            height = int(width * self.aspect_ratio)
            self.resize(width, height)
        self.is_advanced_open = not self.is_advanced_open
        
    def open_msg_box(self, level, title, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(level)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        return msg_box.exec()
        
    def open_advanced_widget(self):
        if not hasattr(self, 'advanced_layout'):    
            self.advanced_layout = QHBoxLayout()
            self.widgets['Advanced'].setLayout(self.advanced_layout)
            self.set_advanced_widget()
        self.widgets['Advanced'].show()

    def close_advanced_widget(self):
        self.widgets['Advanced'].hide()

    def set_labels(self):
        self.widgets['Language'].setText(self.labels[self.config['ui']['language']]['Language'])
        self.widgets['Set Movable'].setText(self.labels[self.config['ui']['language']]['Set Movable'] if not self.is_overlay_movable else self.labels[self.config['ui']['language']]['Set Fixed'])
        self.widgets['Opacity'].setText(self.labels[self.config['ui']['language']]['Opacity'])
        self.widgets['Window Size'].setText(self.labels[self.config['ui']['language']]['Window Size'])
        self.delete_track_button.setText(self.labels[self.config['ui']['language']]['Delete Track'])
        self.change_updatable_button.setText(self.labels[self.config['ui']['language']]['Set Updatable'] if not self.track_dict['updatable'] else self.labels[self.config['ui']['language']]['Set Unupdatable'])
        self.widgets['Open Advanced'].setText(self.labels[self.config['ui']['language']]['Open Advanced'] if not self.is_advanced_open else self.labels[self.config['ui']['language']]['Close Advanced'])
        
        if hasattr(self, 'advanced_widgets'):
            self.advanced_widgets['Track Width'].setText(self.labels[self.config['ui']['language']]['Track Width'])
            self.advanced_widgets['Track Outline Width'].setText(self.labels[self.config['ui']['language']]['Track Outline Width'])
            self.advanced_widgets['Car Outline Width'].setText(self.labels[self.config['ui']['language']]['Car Outline Width'])
            self.advanced_widgets['Car Size'].setText(self.labels[self.config['ui']['language']]['Car Size'])
            self.advanced_widgets['Player Scale'].setText(self.labels[self.config['ui']['language']]['Player Scale'])
            self.advanced_widgets['Other Car Opacity'].setText(self.labels[self.config['ui']['language']]['Other Car Opacity'])
            self.advanced_widgets['Other Class Opacity'].setText(self.labels[self.config['ui']['language']]['Other Class Opacity'])
            self.advanced_widgets['Show Position'].setText(self.labels[self.config['ui']['language']]['Show Position'])

            self.advanced_widgets['Track Color'].setText(self.labels[self.config['ui']['language']]['Track Color'])
            self.advanced_widgets['Track Color'].set_color(self.config['color']['track_color'])
            self.advanced_widgets['Track Outline Color'].setText(self.labels[self.config['ui']['language']]['Track Outline Color'])
            self.advanced_widgets['Track Outline Color'].set_color(self.config['color']['outline_color'])
            self.advanced_widgets['Player Color'].setText(self.labels[self.config['ui']['language']]['Player Color'])
            self.advanced_widgets['Player Color'].set_color(self.config['color']['player_color'])
            self.advanced_widgets['Player Outline Color'].setText(self.labels[self.config['ui']['language']]['Player Outline Color'])
            self.advanced_widgets['Player Outline Color'].set_color(self.config['color']['player_outline_color'])
            self.advanced_widgets['Other Color'].setText(self.labels[self.config['ui']['language']]['Other Color'])
            self.advanced_widgets['Other Color'].set_color(self.config['color']['other_color'])
            self.advanced_widgets['Next Outline Color'].setText(self.labels[self.config['ui']['language']]['Next Outline Color'])
            self.advanced_widgets['Next Outline Color'].set_color(self.config['color']['next_outline_color'])
            self.advanced_widgets['Prev Outline Color'].setText(self.labels[self.config['ui']['language']]['Prev Outline Color'])
            self.advanced_widgets['Prev Outline Color'].set_color(self.config['color']['prev_outline_color'])
            self.advanced_widgets['Number Color'].setText(self.labels[self.config['ui']['language']]['Number Color'])
            self.advanced_widgets['Number Color'].set_color(self.config['color']['number_color'])
        

    def closeEvent(self, event):
        self.vm.model.ir_manager.stop()
        QApplication.quit()
        event.accept()
        
    def resizeEvent(self, event):
        if hasattr(self, 'aspect_ratio'):
            width = self.width()
            height = int(width * self.aspect_ratio)
            self.resize(width, height)
            
    def mousePressEvent(self, event):
        self.widgets['Opacity'].spinBox.clearFocus()
        self.widgets['Window Size'].spinBox.clearFocus()
        if hasattr(self, 'advanced_widgets'):
            self.advanced_widgets['Track Width'].spinBox.clearFocus()
            self.advanced_widgets['Track Outline Width'].spinBox.clearFocus()
            self.advanced_widgets['Car Outline Width'].spinBox.clearFocus()
            self.advanced_widgets['Car Size'].spinBox.clearFocus()
            self.advanced_widgets['Player Scale'].spinBox.clearFocus()
            self.advanced_widgets['Other Car Opacity'].spinBox.clearFocus()
            self.advanced_widgets['Other Class Opacity'].spinBox.clearFocus()

        super().mousePressEvent(event)
        
        
        
        
        
if __name__ == "__main__":
    app = QApplication([])
    config_ui = ConfigUI()
    config_ui.show()
    app.exec()
