from PySide6.QtWidgets import QApplication
from .model import Model, IRManager
from .view_model import IRMapVM
from .view import IRMap, ConfigUI
import os

def main():
    app = QApplication([])
    ir_manager = IRManager()
    model = Model(ir_manager)
    model.load_config()
    
    vm = IRMapVM(model)
    
    ui = ConfigUI(vm)
    view = IRMap(vm)
    
    ui.show()
    
    app.aboutToQuit.connect(model.save_config)
    app.aboutToQuit.connect(model.save_track)
    app.exec()

if __name__ == "__main__":
    main()
