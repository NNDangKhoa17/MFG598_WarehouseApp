from app_module.all_modules import *

class MainWindow(QMainWindow):    
    def __init__(self):
        super().__init__()
        self.setCentralWidget(None)
        self._main_func = None
        self.login_page()
        self.create_tools()

    def login_page(self):        
        login = Login() 
        login.setWindowModality(Qt.ApplicationModal)
        if login.exec() == QDialog.Accepted:            
            operation = ops.Operation()
            operation + login._operator
            if operation.operator.position == "manager":
                widget_group = ManagerMode(operation)
            elif operation.operator.position == "technician":
                widget_group = TechnicianMode(operation)
            else:
                widget_group = TechnicianMode(operation)
            self._main_func = widget_group
            self.setCentralWidget(widget_group)
            self.showFullScreen()            
            login.accept()

    def create_tools(self):
        # Toolbar region
        tool_bar = QToolBar(self)
        tool_bar.setIconSize(QSize(16, 16))
        self.addToolBar(tool_bar)
        # Menu region on toolbar
        menu = self.menuBar()
        # Menu category "File"
        file_menu = menu.addMenu("File")
        load_btn = QAction(QIcon(ICON_PATH + "inbox-download.png"), "&Load", self)
        load_btn.setShortcut("Ctrl+O")
        save_btn = QAction(QIcon(ICON_PATH + "disk.png"), "&Save", self)
        save_btn.setShortcut("Ctrl+S")
        logout_btn = QAction(QIcon(ICON_PATH + "door-open-out.png"), "&Log out", self)
        logout_btn.setShortcut("Ctrl+F4")
        exit_btn = QAction(QIcon(ICON_PATH + "cross.png"), "&Exit", self)
        exit_btn.setShortcut("Alt+F4")
        # file_menu.addAction(load_btn)
        file_menu.addAction(load_btn)
        file_menu.addAction(save_btn)
        file_menu.addAction(logout_btn)
        file_menu.addAction(exit_btn)
        load_btn.triggered.connect(self.load_menu_trigger)
        save_btn.triggered.connect(self.save_menu_trigger)
        logout_btn.triggered.connect(self.logout)
        exit_btn.triggered.connect(QCoreApplication.quit)
        # Menu category ""
        info_menu = menu.addMenu("Infomation")
        warehouse_info = QAction(QIcon(ICON_PATH + "information-balloon.png"),"&Warehouse Summary", self)
        warehouse_info.setShortcut("F1")
        warehouse_info.triggered.connect(self.show_summary)
        show_heatmap = QAction("&Toogle Heatmap", self)
        show_heatmap.setCheckable(True)
        show_heatmap.setChecked(True)
        show_heatmap.toggled.connect(self.toggle_heatmap)
        show_vehicle_path = QAction("&Toogle Vehicle Path", self)
        show_vehicle_path.setCheckable(True)
        show_vehicle_path.setChecked(True)
        show_vehicle_path.toggled.connect(self.toggle_path)
        info_menu.addAction(warehouse_info)
        info_menu.addAction(show_heatmap)
        info_menu.addAction(show_vehicle_path)

    def save_operation(self):
        self._main_func._operation.operator_logout()
        self._main_func.to_close.emit()
    def load_menu_trigger(self):
        self._main_func.to_load.emit()
    def save_menu_trigger(self):
        self._main_func.to_save.emit()
    def show_summary(self):
        self._main_func.warehouse_summary.emit()
    def toggle_heatmap(self):
        self._main_func.toggle_heatmap.emit()
    def toggle_path(self):
        self._main_func.toggle_path.emit()
    def logout(self):
        try:
            self.save_operation()
        except:
            pass
        del self._main_func._operation
        self._main_func = None
        self.setCentralWidget(None)
        self.hide()
        self.login_page()
    def closeEvent(self, event):
        try:
            self.save_operation()
        except:
            event.accept()
     
# Main program
if __name__ == '__main__':
    app = QApplication(argv) 
    window = MainWindow()
    window.show()
    
    exit(app.exec())