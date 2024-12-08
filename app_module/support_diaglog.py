from app_module.qt_modules import *
import app_module.warehouse_essential.geometry as geometry
from app_module.warehouse_essential.warehouse import (Warehouse,
                                                    StorageUnit,
                                                    VehicleUnit, 
                                                    DEFAULT_WAREHOUSE_PATH)

import csv
import pandas as pd

DEFAULT_DATA_PATH = ".//Metadata//"

class CommonButton(QWidget):
    def __init__(self, parent: QWidget | None = None, ok_label = "OK", cancel_label = "Cancel", orientation = 0):
        super().__init__(parent)
        self._ok = QPushButton(ok_label)
        self._cancel = QPushButton(cancel_label)
        if orientation == 0:
            main_layout = QHBoxLayout()
        else:
            main_layout = QVBoxLayout()
        main_layout.addWidget(self._ok)
        main_layout.addWidget(self._cancel)
        self.setLayout(main_layout)
    def get_ok_btn(self):
        return self._ok
    def set_ok_btn(self, callable):
        self._ok.clicked.connect(callable)
    def get_cancel_btn(self):
        return self._cancel
    def set_cancel_btn(self, callable):
        self._cancel.clicked.connect(callable)
    # property
    ok_btn = property(fget = get_ok_btn, fset = set_ok_btn)
    cancel_btn = property(fget = get_cancel_btn, fset = set_cancel_btn)

class ManualSaveForm(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Save a Warehouse")
        self.setWindowIcon(QIcon(ICON_PATH + "disk.png"))
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        self._file_name = QLineEdit()
        form_layout.addRow("File name", self._file_name)
        main_layout.addLayout(form_layout)
        # Button
        buttons = CommonButton(self, "Save", "Cancel", 0)
        buttons.ok_btn = self.save_file
        buttons.cancel_btn = self.reject
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)
        self._out = None
    out = property(fget = lambda self: self._out)

    def save_file(self):
        file_name = self._file_name.text()
        if not file_name.endswith(".json"):
            file_name = file_name.rstrip() + ".json"
        self._out = file_name
        self.accept()

class LoadFileForm(QFileDialog):
    def __init__(self):
        super().__init__()
        try:
            self.setDirectory(DEFAULT_WAREHOUSE_PATH)
        except:
            pass

class SetLayoutForm(QDialog):
    """
    Layout Form for adding a a new Storage
    """
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Setup a Warehouse Layout")
        self.setWindowIcon(QIcon(ICON_PATH + "layers.png"))
        self._length = QLineEdit()
        self._length.setValidator(QDoubleValidator(bottom = 0))
        self._width = QLineEdit()
        self._width.setValidator(QDoubleValidator(bottom = 0))
        main_layout = QVBoxLayout()
        # Input parameters
        input_layout = QFormLayout()
        input_layout.addRow("Length", self._length)
        input_layout.addRow("Width", self._width)
        # Buttons
        buttons = CommonButton(self, "Set", orientation = 1)
        buttons.ok_btn = self._set_clicked
        buttons.cancel_btn = self._cancel_clicked
        # Main layout
        main_layout.addLayout(input_layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)
        self._output = None
    
    def get_output(self):
        return self._output
    out = property(fget = get_output)

    def _set_clicked(self):
        try:
            self._length = float(self._length.text())
            self._width = float(self._width.text())
            self._output = geometry.Rectangle.from_dict({"dimension": (self._length, self._width), "buffer": 0,"ref_pt": (0, 0), "ref_pt_type": "corner"})
        except:
            QMessageBox.critical(self, "Setup error", "Invalid data type!!! Fail to setup a warehouse layout")
            self.reject()
        else:
            self.accept()

    def _cancel_clicked(self):
        self.reject()

class AddStorageFrom(QDialog):
    """
    Form to add a New Storage Unit
    """
    def __init__(self, parent = None):
        super().__init__(parent = parent)
        self.setWindowTitle("Adding a Storage Unit")
        self.setWindowIcon(QIcon(ICON_PATH + "store--plus.png"))
        main_layout = QVBoxLayout()
        # Input parameters
        form = QFormLayout()
        self._id = QLineEdit()
        self._side = QLineEdit()
        self._side.setValidator(QDoubleValidator(bottom = 0))
        self._cap = QLineEdit()
        self._cap.setValidator(QDoubleValidator(bottom = 0))
        self._category = QLineEdit()
        form.addRow("ID", self._id)
        form.addRow("Side", self._side)
        form.addRow("Capacity", self._cap)
        form.addRow("Category", self._category)
        main_layout.addLayout(form)
        main_layout.addWidget(QLabel("Center Location"))
        self._x = QLineEdit()
        self._x.setValidator(QDoubleValidator())
        self._y = QLineEdit()
        self._y.setValidator(QDoubleValidator())
        centroid_ = QHBoxLayout()
        centroid_.addWidget(QLabel("(x, y) = "), stretch = 7, alignment = Qt.AlignCenter)
        centroid_.addWidget(QLabel("("), stretch = 1)
        centroid_.addWidget(self._x, stretch = 3)
        centroid_.addWidget(QLabel(","), stretch = 1)
        centroid_.addWidget(self._y, stretch = 3)
        centroid_.addWidget(QLabel(")"), stretch = 1)
        main_layout.addLayout(centroid_)
        # Button
        buttons = CommonButton(self, "Set", orientation = 1)
        buttons.ok_btn = self._done_pressed
        buttons.cancel_btn = self._cancel_pressed
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)
        self._output = None

    def get_output(self):
        return self._output
    out = property(fget = get_output)
    
    def _done_pressed(self):
        try:
            new_id = self._id.text()
            side = float(self._side.text())
            cap = float(self._cap.text())
            category = self._category.text()
            x = float(self._x.text())
            y = float(self._y.text())
            info_dict = {"id" : new_id, "cap": cap, "geo": {"type": "Square", "dimension": [side, side], "ref_pt_type": "center", "buffer": 0, "ref_pt": [x, y]}, "load": 0, "type": category}
            self._output = StorageUnit.load_unit(info_dict)
            self.accept()
        except:
            self.reject()
    
    def _cancel_pressed(self):
        self.reject()

class RemoveStorageFrom(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._output = None
        self.setWindowTitle("Remove a Storage Unit")
        self.setWindowIcon(QIcon(ICON_PATH + "store--minus.png"))
        warehouse_obj : Warehouse = self.parent().__dict__.get("warehouse_obj", None)
        if warehouse_obj == None:
            QMessageBox.warning(self, "Warehouse Warning", "Invalid Warehouse object!!!") # Fail-safe
        try:
            storage_list = warehouse_obj.storage.unit_list.index.to_list()
        except:
            storage_list = []
        # Else (continue create a storage list)
        # Input parameters
        form = QFormLayout()
        self._id = QComboBox()
        self._id.addItems(storage_list)
        form.addRow("ID", self._id)
        # Button
        buttons = CommonButton(self, "Done")
        buttons.ok_btn = self._done_pressed
        buttons.cancel_btn = self._cancel_pressed
        if storage_list == []:
            QMessageBox.warning(self, "Vehicle Warning","Empty or Invalid Vehicle list!!!")
            buttons.ok_btn.setDisabled(True) # Disable invalid operation
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(form)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)

    def get_output(self):
        return self._output
    out = property(fget = get_output)
    
    def _done_pressed(self):
        self._output = self._id.currentText()
        self.accept()
    def _cancel_pressed(self):
        self.reject()

class AddVehicleFrom(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent = parent)
        self.setWindowTitle("Adding a Vehicle")
        self.setWindowIcon(QIcon(ICON_PATH + "truck--plus.png"))
        # Input parameters
        form = QFormLayout()
        self._id = QLineEdit()
        self._length = QLineEdit()
        self._length.setValidator(QDoubleValidator(bottom = 0))
        self._width = QLineEdit()
        self._width.setValidator(QDoubleValidator(bottom = 0))
        self._battery = QLineEdit()
        self._battery.setValidator(QIntValidator(bottom = 0, top = 100))
        form.addRow("ID", self._id)
        form.addRow("Length", self._length)
        form.addRow("Width", self._width)
        form.addRow("Battery", self._battery)
        self._x = QLineEdit()
        self._x.setValidator(QDoubleValidator())
        self._y = QLineEdit()
        self._y.setValidator(QDoubleValidator())
        centroid_ = QHBoxLayout()
        centroid_.addWidget(QLabel("(x, y) = "), stretch = 7, alignment = Qt.AlignCenter)
        centroid_.addWidget(QLabel("("), stretch = 1)
        centroid_.addWidget(self._x, stretch = 3)
        centroid_.addWidget(QLabel(","), stretch = 1)
        centroid_.addWidget(self._y, stretch = 3)
        centroid_.addWidget(QLabel(")"), stretch = 1)
        # Buttons
        buttons = CommonButton(self, "Done")
        buttons.ok_btn = self._done_pressed
        buttons.cancel_btn = self._cancel_pressed
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(form)
        main_layout.addWidget(QLabel("Docking location"))
        main_layout.addLayout(centroid_)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)
        self._output = None

    def get_output(self):
        return self._output
    out = property(fget = get_output)
    
    def _done_pressed(self):
        id_ = self._id.text()
        length = float(self._length.text())
        width = float(self._width.text())
        battery = int(self._battery.text())
        x = float(self._x.text())
        y = float(self._y.text())
        vec_obj = VehicleUnit(id_, dock_loc = (x, y), size = (length, width), battery_cap = battery)
        self.accept()
        self._output = vec_obj
    
    def _cancel_pressed(self):
        self.reject()

class RemoveVehicleFrom(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Remove a Vehicle")
        self.setWindowIcon(QIcon(ICON_PATH + "truck--minus.png"))
        warehouse_obj : Warehouse = self.parent().__dict__.get("warehouse_obj", None)
        if warehouse_obj == None:
            QMessageBox.warning(self, "Warehouse Warning", "Invalid Warehouse object!!!") # Fail-safe
        try:
            vehicle_list = warehouse_obj.vehicles.unit_list.index.to_list()
        except:
            vehicle_list = []
        # Else (continue create a vehicle list)
        # Input parameters
        form = QFormLayout()
        self._id = QComboBox()
        self._id.addItems(vehicle_list)
        form.addRow("ID", self._id)
        # Buttons
        buttons = CommonButton()
        buttons.ok_btn = self._done_pressed
        buttons.cancel_btn = self._cancel_pressed
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(form)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)
        self._output = None
        if vehicle_list == []:
            QMessageBox.warning(self, "Vehicle Warning","Empty or Invalid Vehicle list!!!")
            buttons.ok_btn.setDisabled(True) # Disable invalid operation
            

    def get_output(self):
        return self._output
    out = property(fget = get_output)
    
    def _done_pressed(self):
        self._output = self._id.currentText()
        self.accept()

    def _cancel_pressed(self):
        self.reject()

class AddVehiclePath(QDialog):
    def __init__(self, id_list) -> None:
        super().__init__()
        self.setWindowTitle("Add Vehicle Path")
        self.setWindowIcon(QIcon(ICON_PATH + "road.png"))
        # Input parameter
        form_layout = QFormLayout()
        self._id_list = QComboBox()
        self._id_list.addItems(id_list)
        self._path_file = QLineEdit()
        form_layout.addRow("Vehicle ID", self._id_list)
        form_layout.addRow("Path File", self._path_file)
        btn_layout = QHBoxLayout()
        browse_btn = QPushButton("Browse a Path File")
        browse_btn.clicked.connect(self._browse)
        # buttons (common)
        buttons = CommonButton(self, "Load")
        buttons.ok_btn = self._load
        buttons.cancel_btn = self._cancel
        btn_layout.addWidget(buttons)
        # Main layout
        main_layout =  QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(browse_btn)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        buttons.ok_btn.setDefault(True)
        self._out = None

    def get_result(self):
        return self._out
    out = property(fget = get_result)        

    def _browse(self):
        file_diag = QFileDialog()
        file_diag.setDirectory(DEFAULT_DATA_PATH)
        name = file_diag.getOpenFileName()
        if not name == "":
            self._path_file.setText(name[0])

    def _load(self):
        if self._path_file.text() == "":
            self.reject()
        else:
            self._out = self._id_list.currentText(), self._path_file.text()
            self.accept()
    def _cancel(self):
        self.reject()


class StorageLoadForm(QDialog):
    """
    Dialog contains form for managing the storage
    """
    def __init__(self, parent: QWidget | None = None, storage_list : list = []) -> None:
        super().__init__(parent)
        self.setWindowTitle("Load/Unload Storage")
        self.setWindowIcon(QIcon(ICON_PATH + "baggage-cart-box.png"))
        self._row_list = []
        self._storage_list = storage_list
        self._form_layout = QVBoxLayout()
        self.add_row()
        btn_layout = QGridLayout()
        add_row_btn = QPushButton("Add a new Order")
        add_row_btn.clicked.connect(self.add_row)
        load_file_btn = QPushButton("Load Order File")
        load_file_btn.clicked.connect(self.load_file)
        done_btn = QPushButton("Done")
        done_btn.clicked.connect(self._done)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self._cancel)
        btn_layout.addWidget(add_row_btn, 0, 0, 1, 2)
        btn_layout.addWidget(load_file_btn, 1, 0, 1, 2)
        btn_layout.addWidget(done_btn, 2 , 0)
        btn_layout.addWidget(cancel_btn, 2, 1)
        done_btn.setDefault(True)
        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(self._form_layout)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        self._output = []
    
    def get_output(self):
        return self._output
    out = property(fget = get_output)
    def add_row(self):
        if len(self._row_list) > 10:
            QMessageBox.warning(self, "Addition Limit", "Only 10 row allowed at a time!")
        else:
            new_row = self.RowForm(self._storage_list)
            self._row_list.append(new_row)
            self._form_layout.addWidget(new_row)
    def load_file(self):
        file_dialog = QFileDialog(self)
        filename = file_dialog.getOpenFileName()[0]
        with open(filename, mode = 'r', newline = "") as file:
            reader = csv.reader(file)
            lines = [line for line in reader]
        self._output = lines
        self.accept()

    def _done(self):
        self._output = [row.out for row in self._row_list]
        self.accept()
    def _cancel(self):
        self.reject()

    class RowForm(QWidget):
        def __init__(self, unit_list : list):
            super().__init__()
            main_layout = QHBoxLayout()
            self._id_list = QComboBox()
            self._id_list.addItems(unit_list)
            self._action_list = QComboBox()
            self._action_list.addItems(["Load", "Unload"])
            self._amount = QLineEdit("0")
            restriction = QDoubleValidator(bottom = 0)
            self._amount.setValidator(restriction)
            main_layout.addWidget(QLabel("Storage Unit ID"), stretch = 1)
            main_layout.addWidget(self._id_list, stretch = 1)
            main_layout.addWidget(QLabel("Action"), stretch = 0.5)
            main_layout.addWidget(self._action_list, stretch = 0.5)
            main_layout.addWidget(QLabel("Amount"), stretch = 0.5)
            main_layout.addWidget(self._amount, stretch = 0.75)
            self.setLayout(main_layout) 
            self._output = ("", "", 0)

        def get_output(self):
            if self._amount == "":
                self._output = (self._id_list.currentText(), self._action_list.currentText(), 0)
            else:
                self._output = (self._id_list.currentText(), self._action_list.currentText(), float(self._amount.text()))
            return self._output
        out = property(fget = get_output)

class WarehouseSummary(QDialog):
    def __init__(self, warehouse_obj : Warehouse):
        super().__init__()
        self._monitor_obj = warehouse_obj
        self.setWindowTitle("Warehouse Summary")
        self.setWindowIcon(QIcon(ICON_PATH + "system-monitor.png"))
        title = QLabel("WAREHOUSE SUMMARY")
        title.setFont(BOLD_FONT)
        layout_label = QLabel("Layout Shape")
        layout_description = QLabel(warehouse_obj.get_layout(info_type = "description")["description"])
        max_load = self._monitor_obj.storage.unit_list["unit"].apply(lambda x : x.capacity).sum()
        current_load = self._monitor_obj.storage.unit_list["unit"].apply(lambda x : x.load).sum()
        load_status_label = QLabel("Loading Status")
        self._load_status = QLabel(str(current_load) + " / " + str(max_load))
        self._load_bar = QProgressBar()
        self._load_bar.setRange(0, max_load)
        self._load_bar.setValue(int(current_load))
        
        # Mainlayout
        main_layout = QGridLayout()
        main_layout.addWidget(title, 0, 0, 1, 2, alignment = Qt.AlignCenter)
        main_layout.addWidget(layout_label, 1, 0)
        main_layout.addWidget(layout_description, 1, 1, alignment = Qt.AlignRight)
        main_layout.addWidget(load_status_label, 2, 0)
        main_layout.addWidget(self._load_status, 2, 1, alignment = Qt.AlignRight)
        main_layout.addWidget(self._load_bar, 3, 0, 1, 2)
        # Table
        self._storage_tab = QTableView()
        self._vehicle_tab = QTableView()
        self.data_table()
        main_layout.addWidget(self._storage_tab, 4, 0)
        main_layout.addWidget(self._vehicle_tab, 4, 1)
        self.setLayout(main_layout)
        # Fix the size
        self.setFixedSize(self.width(), self.height())
        # Timer for real-time update
        self._timer = QTimer()
        self._timer.start(1000)
        self._timer.timeout.connect(self._update)
    
    def _update(self):
        max_load = self._monitor_obj.storage.unit_list["unit"].apply(lambda x : x.capacity).sum()
        current_load = self._monitor_obj.storage.unit_list["unit"].apply(lambda x : x.load).sum()
        self._load_status.setText(str(current_load) + " / " + str(max_load))
        self._load_bar.setValue(int(current_load))
        self.data_table()

    def data_table(self):
        # Table data
        # For Storage
        self._storage_tab.horizontalHeader().setFont(BOLD_FONT)
        self._storage_tab.verticalHeader().setVisible(False)
        self._storage_tab.setSelectionBehavior(QTableView.SelectRows)
        self._storage_tab.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # Clean up storage data
        storage_data : pd.DataFrame = self._monitor_obj.storage.unit_list.copy(deep = True)
        storage_data["ID"] = storage_data["id"]
        storage_data["Good Type"] = storage_data["unit"].apply(lambda x : x.category)
        storage_data["Current Load / Capacity"] = storage_data["unit"].apply(lambda x : str(x.load) + "/" + str(x.capacity))
        storage_data = storage_data.drop(columns = ["id", "unit"])
        storage_data = self.PandasModel(storage_data)
        self._storage_tab.setModel(storage_data)
        self._storage_tab.show()

        # For Vehicle
        self._vehicle_tab.horizontalHeader().setFont(BOLD_FONT)
        self._vehicle_tab.verticalHeader().setVisible(False)
        self._vehicle_tab.setSelectionBehavior(QTableView.SelectRows)
        self._vehicle_tab.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # Clean up vehicle data
        # Clean up storage data
        vehicle_data : pd.DataFrame = self._monitor_obj.vehicles.unit_list.copy(deep = True)
        vehicle_data["ID"] = vehicle_data["id"]
        vehicle_data["Docking Location"] = vehicle_data["unit"].apply(lambda x : str(x.dock_loc))
        vehicle_data["Battery"] = vehicle_data["unit"].apply(lambda x : str(x.battery) + "%")
        vehicle_data["Active"] = vehicle_data["unit"].apply(lambda x : str(x.active))      
        vehicle_data["Motion Status"] = vehicle_data["unit"].apply(lambda x : x.motion)
        vehicle_data = vehicle_data.drop(columns = ["id", "unit"])
        vehicle_data = self.PandasModel(vehicle_data)
        self._vehicle_tab.setModel(vehicle_data)
        self._vehicle_tab.show()

    class PandasModel(QAbstractTableModel):
        """
        A model to interface a Qt view with pandas dataframe
        """
        def __init__(self, dataframe: pd.DataFrame, parent = None):
            QAbstractTableModel.__init__(self, parent)
            self._dataframe = dataframe

        def rowCount(self, parent = QModelIndex()) -> int:
            """ Override method from QAbstractTableModel
            Return row count of the pandas DataFrame
            """
            if parent == QModelIndex():
                return len(self._dataframe)
            return 0

        def columnCount(self, parent=QModelIndex()) -> int:
            """Override method from QAbstractTableModel
            Return column count of the pandas DataFrame
            """
            if parent == QModelIndex():
                return len(self._dataframe.columns)
            return 0

        def data(self, index: QModelIndex, role=Qt.ItemDataRole):
            """Override method from QAbstractTableModel
            Return data cell from the pandas DataFrame
            """
            if not index.isValid():
                return None
            if role == Qt.ItemDataRole.DisplayRole:
                return str(self._dataframe.iloc[index.row(), index.column()])
            return None

        def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
            """Override method from QAbstractTableModel
            Return dataframe index as vertical header data and columns as horizontal header data.
            """
            if role == Qt.ItemDataRole.DisplayRole:
                if orientation == Qt.Orientation.Horizontal:
                    return str(self._dataframe.columns[section])
                if orientation == Qt.Vertical:
                    return str(self._dataframe.index[section])
            return None