from app_module.qt_modules import *
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib import use as mpl_use, cm
import matplotlib as mpl
from datetime import datetime as dt, timedelta
from app_module.warehouse_essential.warehouse import (Warehouse,
                                                      VehicleUnit,
                                                      StorageUnit)
from app_module.support_diaglog import CommonButton
import pandas as pd


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, width = 5, height = 4, dpi = 300):
        fig = Figure(figsize = (width, height), dpi = dpi)
        super().__init__(fig)
        self.axes = fig.add_subplot(111)
        # Loading heatmap color bar
        cbar = fig.colorbar(cm.ScalarMappable(mpl.colors.Normalize(vmin = 0, vmax = 100, clip = True), cmap = 'jet'), ax = self.axes)
        cbar.set_ticks([0, 25, 50, 75, 100])
        cbar.set_ticklabels( ["0% (Empty)", "25%", "50%", "75%", "100% (Full)"])
        cbar.ax.get_yaxis().labelpad = 15
        cbar.ax.set_ylabel("LOAD PERCENTAGE", rotation = 270)
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        self.axes.spines[:].set_visible(False)
        
    def clear(self):
        """
        Clear the plotting on the current canvas
        """
        # Prepare for new plot coming
        self.axes.clear()
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        self.axes.spines[:].set_visible(False)

class WarehouseMonitorScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        # Setup label
        screen_title = QLabel("WAREHOUSE HEATMAP MONITOR")
        screen_title.setFont(BOLD_FONT)
        # and plot
        mpl_use("QtAgg")
        self._canvas = MplCanvas(width = 8, height = 6, dpi = 100)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(screen_title, alignment = Qt.AlignCenter)
        main_layout.addWidget(self._canvas)
        self.setLayout(main_layout)

    @property
    def ax(self):
        return self._canvas.axes
    
    def clear_drawing(self):
        self._canvas.clear()

class OperationInfoView(QHBoxLayout):
    def __init__(self, operation) -> None:
        super().__init__()
        self._start = dt.now()
        _working_time = timedelta(days = 0, hours = 0, minutes = 0, seconds = 0)

        _emp_info = QLabel(operation.__str__())
        time_msg = "Current time: " + dt.now().strftime("%A, %Y-%m-%d, %I:%M %p") + "\n" + "Working time: " + _working_time.__str__()
        self._clock_label = QLabel(time_msg)
        self._clock_label.setAlignment(Qt.AlignRight)
        self.addWidget(_emp_info)
        self.addWidget(self._clock_label)
    
    def update(self):
        _working_time = dt.now() - self._start
        _working_time = _working_time.__str__().split(".")[0]
        time_msg = "Current time: " + dt.now().strftime("%A, %Y-%m-%d, %I:%M %p") + "\n" + "Working time: " + _working_time
        self._clock_label.setText(time_msg)

class AnnoucementView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Announcement when there is any event happens during the operation
        """
        super().__init__(parent)
        main_layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        widget_label = QLabel("Event Annoucement")
        widget_label.setFont(BOLD_FONT)
        header_layout.addWidget(widget_label, stretch = 7)
        clear_btn = QPushButton("Clear", icon = QIcon(ICON_PATH + "eraser.png"))
        clear_btn.clicked.connect(self.clear)
        header_layout.addWidget(clear_btn, stretch = 2)
        self._announcement = QTextEdit()
        self._announcement.setReadOnly(True) # Do not allow modification
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self._announcement)
        self.setLayout(main_layout)
    
    def add_event(self, event_str : str, severity = 0):
        time_msg = "At " + dt.now().strftime("%I:%M %p, %Y-%m-%d")
        if severity == 1: # warnig
            self._announcement.setTextBackgroundColor(QColor("#EED202"))
            self._announcement.setTextColor(QColor("#000000"))
        elif severity == 2: # error
            self._announcement.setTextBackgroundColor(QColor("#EED202"))
            self._announcement.setTextColor(QColor("#FF0000"))
        else:
            self._announcement.setTextBackgroundColor(QColor("#FFFFFF"))
            self._announcement.setTextColor(QColor("#000000"))
        self._announcement.append(event_str)        
        self._announcement.append(time_msg)
        self._announcement.append("----------")

    
    def clear(self):
        self._announcement.clear()

class WarehouseInfoView(QTabWidget):
    def __init__(self, parent : QWidget | None = None):
        """
        Widget contains two tabs: Storage Units and Vehicles
        """
        super().__init__()
        self.setParent(parent)
        self._storage_widget = QListWidget()
        self._storage_widget.itemDoubleClicked.connect(self.show_storage_detail)            
        self._vehicle_widget = QListWidget()
        self._vehicle_widget.itemDoubleClicked.connect(self.show_vehicle_detail)
        self.addTab(self._storage_widget, "Storage Unit")
        self.addTab(self._vehicle_widget, "Vehicle")
        
    def update_storage(self):
        # accessing the warehouse object of the parent widget
        warehouse_obj : Warehouse = self.parent().__dict__.get("warehouse_obj")
        storage_list = pd.Series(warehouse_obj.storage.unit_list.index).apply(lambda x : f"Storage Unit ID#{x}").to_list()
        self._storage_widget.clear()
        self._storage_widget.addItems(storage_list)

    def update_vehicle(self):
        # accessing the warehouse object of the parent widget
        warehouse_obj : Warehouse = self.parent().__dict__.get("warehouse_obj")
        vehicle_list = pd.Series(warehouse_obj.vehicles.unit_list.index).apply(lambda x : f"Vehicle ID#{x}").to_list()
        self._vehicle_widget.clear()
        self._vehicle_widget.addItems(vehicle_list)

    def show_storage_detail(self) -> None:
        # accessing the warehouse object of the parent widget
        warehouse_obj = self.parent().__dict__.get("warehouse_obj")
        if not self._storage_widget.currentItem() == None:
            _id = self._storage_widget.currentItem().text().split("ID#")[-1]
            win_name = "Storage Details"
            unit = warehouse_obj.storage.unit_list["unit"][_id]
            detailed_window = self.DetailDialog(unit, win_name)
            detailed_window.exec()

    def show_vehicle_detail(self) -> None:
        # accessing the warehouse object of the parent widget
        warehouse_obj = self.parent().__dict__.get("warehouse_obj")
        if not self._vehicle_widget.currentItem() == None:
            _id = self._vehicle_widget.currentItem().text().split("ID#")[-1]
            win_name = "Vehicle Details"
            # Unit
            warehouse_obj : Warehouse = self.parent().__dict__.get("warehouse_obj")
            unit = warehouse_obj.vehicles.unit_list["unit"][_id]
            detailed_window = self.DetailDialog(unit, win_name)
            detailed_window.exec()

    def update(self):
        self.update_storage()
        self.update_vehicle()

    class DetailDialog(QDialog):
        """
        This dialog contain the information of a selected storage unit (shelf) or vehicle
        """
        def __init__(self, object : StorageUnit | VehicleUnit, win_title = "Detail"):
            super().__init__()
            self.setModal(True)
            self.setWindowTitle(win_title)                
            if isinstance(object, StorageUnit):
                self.setWindowIcon(QIcon(ICON_PATH+ "store-market-stall.png"))
            elif isinstance(object, VehicleUnit):
                self.setWindowIcon(QIcon(ICON_PATH + "truck.png"))
            self._monitor_obj = object # point toward the monitored object
            # self._update_view()

            main_layout = QVBoxLayout()
            # Data View layout
            self._info_layout = QFormLayout()
            self._info_dict = self._monitor_obj.unit_info(formal = True)
            for key, value in self._info_dict.items():
                self._info_layout.addRow(str(key), QLabel(str(value)))
            # print("UpdateDone")
            # Buttons
            buttons = CommonButton(self, "Done", "Cancel", 0)
            buttons.ok_btn = self.accept
            buttons.cancel_btn = self.reject
            main_layout.addLayout(self._info_layout)
            main_layout.addWidget(buttons)

            # Set main layout
            self.setLayout(main_layout)

            # Timer
            self._timer = QTimer()
            self._timer.start(1000)
            self._timer.timeout.connect(self._update_view)
        
        def _done_pressed(self):
            self.accept()

        def _cancel_pressed(self):
            self.reject()

        def _update_view(self):
            self._info_dict = self._monitor_obj.unit_info(formal = True)
            while self._info_layout.rowCount() > 0:
                self._info_layout.removeRow(0)
            for key, value in self._info_dict.items():
                self._info_layout.addRow(str(key), QLabel(str(value)))