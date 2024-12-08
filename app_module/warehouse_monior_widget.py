from app_module.qt_modules import *
from app_module.warehouse_essential.warehouse import Warehouse, DEFAULT_WAREHOUSE_PATH
import app_module.warehouse_essential.geometry as geometry
import app_module.data_viewer as dtv
import app_module.support_diaglog as diag
import pandas as pd

class WarehouseMonitorWidget(QWidget):
    """
    Main widget of Warehouse Monitoring System
    """
    # Signal
    to_close = Signal(None)
    to_save = Signal(None)
    to_load = Signal(None)
    toggle_heatmap = Signal(None)
    toggle_path = Signal(None)
    warehouse_summary = Signal(None)

    def __init__(self, operation) -> None:
        super().__init__()
        # Signals
        self.to_load.connect(self.manual_load)
        self.to_close.connect(self.about_to_close)
        self.to_save.connect(self.manual_save)
        self.toggle_heatmap.connect(self._toggle_hm)
        self.toggle_path.connect(self._toggle_path)
        self.warehouse_summary.connect(self._warehouse_summary)
        # Immediately create a warehouse object
        # empty warehouse object
        self.warehouse_obj = Warehouse()
        self._options = {"heat_map" : True, "vehicle_path" : True}

        self._operation = operation
        self.setWindowTitle("Warehouse Operation Monitor v7")

        main_layout = QGridLayout()
        main_layout.setRowStretch(0, 0.5)
        main_layout.setRowStretch(1, 9)
        main_layout.setRowStretch(2, 0.5)
        main_layout.setColumnStretch(0, 3)
        main_layout.setColumnStretch(1, 7)

        # Push button & Layout
        btn_layout = QVBoxLayout()
        self._setup_layout_btn = QPushButton("Setup Layout")
        self._setup_layout_btn.clicked.connect(self.set_layout)
        self._load_warehouse = QPushButton("Quick Load a Warehouse")
        self._load_warehouse.setShortcut("F5")
        self._load_warehouse.clicked.connect(self.quick_load_warehouse)
        self._add_storage_btn = QPushButton("Add a Storage Unit")
        self._add_storage_btn.clicked.connect(self.add_storage)
        self._remove_storage_btn = QPushButton("Remove a Storage Unit")
        self._remove_storage_btn.clicked.connect(self.remove_storage)
        self._load_storage_btn = QPushButton("Load/Unload a Storage Unit")
        self._load_storage_btn.clicked.connect(self.modify_storage_load)
        self._add_vehicle_btn = QPushButton("Add a Vehicle")
        self._add_vehicle_btn.clicked.connect(self.add_vehicle)
        self._remove_vehicle_btn = QPushButton("Remove a Vehicle")
        self._remove_vehicle_btn.clicked.connect(self.remove_vehicle)
        self._add_path_btn = QPushButton("Setup a Vehicle Path")
        self._add_path_btn.clicked.connect(self.set_vehicle_path)
        btn_layout.addWidget(self._setup_layout_btn)
        btn_layout.addWidget(self._load_warehouse)
        btn_layout.addWidget(self._add_storage_btn)
        btn_layout.addWidget(self._remove_storage_btn)
        btn_layout.addWidget(self._load_storage_btn)
        btn_layout.addWidget(self._add_vehicle_btn)
        btn_layout.addWidget(self._remove_vehicle_btn)
        btn_layout.addWidget(self._add_path_btn)

        self._data_viewer = dtv.WarehouseInfoView()

        # Operation View
        self.operation_view_layout = dtv.OperationInfoView(operation)

        # Announcement
        self._announcement = dtv.AnnoucementView()
        #
        self._plot = dtv.WarehouseMonitorScreen(self)

        main_layout.addLayout(self.operation_view_layout, 0, 0, 1, 2)
        main_layout.addWidget(self._data_viewer)
        main_layout.addLayout(btn_layout, 2, 0)
        main_layout.addWidget(self._announcement, 2, 1)
        main_layout.addWidget(self._plot, 1, 1)

        self.setLayout(main_layout)

        self._timer = QTimer()
        self._timer.start(1000)
        self._timer.timeout.connect(self.timer_out)
        
    def timer_out(self):
        self.operation_view_layout.update()
        self._plot.clear_drawing()
        collision_msg = self.warehouse_obj.collision_check()
        if not collision_msg == "":
            self._announcement.add_event("COLLISION DETECTED: " + collision_msg  + "\nRemove path entity of Collided vehile(s)!!!", severity = 2)
        self.move_vehicle()
        if self.warehouse_obj.layout != None:
            self.warehouse_obj.show(ax = self._plot.ax, heat_display = self._options.get("heat_map"), path_display = self._options.get("vehicle_path"))

    def set_layout(self):
        form = diag.SetLayoutForm()
        try:
            if form.exec() == QDialog.Accepted:
                if not self.warehouse_obj.layout == None:
                    msg_box = QMessageBox()
                    msg_box.setWindowTitle("Setup Conflict")
                    msg_box.setText("There is an existing layout in the current Warehouse.\nSetting new layout will wipe out all current storages and vehicles")
                    msg_box.setInformativeText("Do you want to proceed?")
                    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                    msg_box.setDefaultButton(QMessageBox.Cancel)
                    msg_box.setIcon(QMessageBox.Warning)
                    ret = msg_box.exec()
                    if ret == QMessageBox.Yes:                        
                        self.warehouse_obj.layout = form.out
                        self.warehouse_obj.storage.clear_all()
                        self.warehouse_obj.vehicles.clear_all()
                        self._data_viewer.update()
                        self._announcement.add_event(f"Erase current Warehouse and Setup a new layout\nStorage and Vehicle Data is wiped out!", 1)
                    elif ret == QMessageBox.No:
                        self._announcement.add_event(f"Abandoned Attempt to Setup a new Layout on an existing Warehouse", 1)
                    elif ret == QMessageBox.Cancel:
                        pass
                else:
                    self.warehouse_obj.layout = form.out
                    self._announcement.add_event(f"New Storage Layout is setup", 0)
        except geometry.GeometryException as e:
            QMessageBox.critical(self, "Setup error", e.__str__())
        
    def load_warehouse(self):
        """
        Method open a data file of existing warehouse data
        """
        file_diag = diag.LoadFileForm()
        filename = file_diag.getOpenFileName()[0]
        # name == "" (empty string if no file is selected) (name == "" -> True)
        if not filename == "":
            try:
                self.warehouse_obj = Warehouse().load_info(filename)
            except Exception:
                QMessageBox.critical(self, "Load Warehouse Error", "Corrupted Warehouse Records or No record availble" + "\nUnable to load data of the Warehouse!!!")
                self._announcement.add_event(f"Failed attempt to Load data of a Warehouse", 1)
            else:
                self._data_viewer.update_storage()
                self._data_viewer.update_vehicle()
                self._announcement.add_event(f"Successfully Load a Warehouse\n  \u2022 Number of storage units: {len(self.warehouse_obj.storage.unit_list)}\n  \u2022 Number of vehicle unit: {len(self.warehouse_obj.vehicles.unit_list)}")

    def quick_load_warehouse(self):
        """
        Quickly load from autosave. Rasie error if the file not found
        """
        # Fail-safe when try to load on working warehouse
        if not self.warehouse_obj.layout == None:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Load Conflict")
            msg_box.setText("There is an existing layout in the current Warehouse.\nSetting new layout will wipe out all current storages and vehicles")
            msg_box.setInformativeText("Do you want to proceed?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Cancel)
            msg_box.setIcon(QMessageBox.Warning)
            ret = msg_box.exec()
            if ret == QMessageBox.Yes:
                self._announcement.add_event(f"Erase current Warehouse and Load a new layout from file\nStorage and Vehicle Data is wiped out!", 1)
                # and pass
            elif ret == QMessageBox.No:
                self._announcement.add_event(f"Abandoned Attempt to Load a Layout on an existing Warehouse", 1)
                return None
            elif ret == QMessageBox.Cancel:
                return None
        try:
            self.warehouse_obj = Warehouse().load_info(DEFAULT_WAREHOUSE_PATH + "\\autosave.json")
        except FileNotFoundError:
            QMessageBox.critical(self, "File not found", "No autosaved file found. Cannot perform quick load")
        except Exception:
                QMessageBox.critical(self, "Load Warehouse Error", "Corrupted Warehouse Records or No record availble" + "\nUnable to load data of the Warehouse!!!")
                self._announcement.add_event(f"Failed attempt to Load data of a Warehouse", 1)
        else:
            self._data_viewer.update_storage()
            self._data_viewer.update_vehicle()
            self._announcement.add_event(f"Successfully Load a Warehouse\n  \u2022 Number of storage units: {len(self.warehouse_obj.storage.unit_list)}\n  \u2022 Number of vehicle unit: {len(self.warehouse_obj.vehicles.unit_list)}")

    def add_storage(self):
        """
        Method for placing an individual unit of storage
        """
        if self.warehouse_obj.layout == None:
            QMessageBox.warning(self, "Warning", "Warehouse has no layout!!!")
            return None
        form = diag.AddStorageFrom()
        if form.exec() == QDialog.Accepted:
            new_storage_unit = form.out
            ret, error = self.warehouse_obj.add_storage_unit(new_storage_unit)
            if ret == True:
                if len(error) > 0:
                    error_msg = "Unable to add a new storage due to the following error(s):"
                    for e in error:
                        error_msg += f"\n \u2022 {e}"
                    QMessageBox.critical(self, "Error in adding a storage unit", error_msg)
                    self._announcement.add_event("Fail to add a new Storage Unit", 2)
                else:
                    self._data_viewer.update_storage()
                    self._announcement.add_event(f"A new Storage Unit ID#{new_storage_unit.id} is added", 0)

    def remove_storage(self):
        """
        Method for removing an existing storage unit
        """
        if self.warehouse_obj.layout == None:
            QMessageBox.warning(self, "Warning", "Warehouse has no layout!!!")
            return None
        if self.warehouse_obj.storage.empty:
            QMessageBox.warning(self, "Warning", "Warehouse does not contain any storage unit!!!")
            return None
        form = diag.RemoveStorageFrom(parent = self)
        if form.exec() == QDialog.Accepted:
            _shelf_id = form.out
            try:
                self.warehouse_obj.remove_storage_unit(_shelf_id)
            except ValueError as e:
                QMessageBox.critical(self, "ID does not match", e.__str__())
            else:
                self._data_viewer.update_storage()

    def modify_storage_load(self):
        """
        Method for loading/unloading good into an existing storage unit (input diaglogue)
        """
        if self.warehouse_obj.layout == None:
            QMessageBox.warning(self, "Warning", "Warehouse has no layout!!!")
            return None
        if self.warehouse_obj.storage.empty:
            QMessageBox.warning(self, "Warning", "Warehouse does not contain any storage unit!!!")
        form = diag.StorageLoadForm(self, self.warehouse_obj.storage.unit_list.index.to_list())
        if form.exec() == QDialog.Accepted:
            lines = form.out
            success, error, changes = self.warehouse_obj.storage_load_change(lines)
            if not success:
                QMessageBox.warning(self, "Invalid operation", error)
            if len(changes) > 0:
                changes.insert(0, "Storage Unit Load Changes:")
                self._announcement.add_event("\n".join(changes))

    def add_vehicle(self):
        """
        Method for placing an individual unit of vehicle
        """
        if self.warehouse_obj.layout == None:
            QMessageBox.warning(self, "Warning", "Warehouse has no layout!!!")
            return None
        form = diag.AddVehicleFrom()
        if form.exec() == QDialog.Accepted:
            new_vehicle = form.out
            ret, error = self.warehouse_obj.add_vehicle_unit(new_vehicle)
            if ret == True:
                if len(error) > 0:
                    error_msg = "Unable to add a new vehicle due to the following error(s):"
                    for e in error:
                        error_msg += f"\n \u2022 {e}"
                    QMessageBox.critical(self, "Error in adding vehicle", error_msg)
                    self._announcement.add_event("Fail to add a new Vehicle Unit", 2)
                else:
                    self._data_viewer.update_vehicle()
                    self._announcement.add_event(f"A new Vehicle Unit ID#{new_vehicle.id} is added", 0)
    
    def remove_vehicle(self):
        """
        Method for removing an existing vehicle unit
        """
        if self.warehouse_obj.layout == None:
            QMessageBox.warning(self, "Warning", "Warehouse has no layout!!!")
            return None
        form = diag.RemoveVehicleFrom(parent = self)
        if form.exec() == QDialog.Accepted:
            _shelf_id = form.out
            try:
                self.warehouse_obj.remove_vehicle_unit(_shelf_id)
            except ValueError as e:
                QMessageBox.critical(self, "ID does not match", e.__str__())
            else:
                self._data_viewer.update_vehicle()

    def set_vehicle_path(self):
        """
        Add a certain path file (list of coordinate) to a vehicle
        Raise error the vehicle does not exist
        """
        form = diag.AddVehiclePath(self.warehouse_obj.vehicles.unit_list["id"].to_list())
        if form.exec() == QDialog.Accepted:
            vehicle_id, filename = form.out
            vehicle_unit = self.warehouse_obj.vehicles.unit_list["unit"][vehicle_id]
            try:
                path_data = pd.read_csv(filename, header = None)
                pos_list = path_data.apply(lambda x : (float(x[0]), float(x[1])), axis = 1).to_list()
            except:
                QMessageBox.critical(self, "File not found", f"The requested file does exist!!!")
                pos_list = []
            else:
                result = vehicle_unit.set_path(pos_list)
                if not result[0]: # If the path is not successfully import, show error:
                    QMessageBox.warning(self, "Failed operation", result[1])
    
    def move_vehicle(self):
        self.warehouse_obj.vehicles.unit_list["unit"].apply(lambda unit : unit.move())
    
    @Slot(None) # call before erase the current widget
    def manual_load(self):
        self.load_warehouse()

    @Slot(None) # call before erase the current widget
    def about_to_close(self):
        if not self.warehouse_obj.layout == None:
            self.warehouse_obj.save_data()

    @Slot(str)
    def manual_save(self):
        if not self.warehouse_obj.layout == None:
            form = diag.ManualSaveForm()
            if form.exec() == QDialog.Accepted:
                filename = form.out
                self.warehouse_obj.save_data(filename)
        else:
            QMessageBox.critical(self, "Error", "No warehouse layout to save!!!")
    
    @Slot(None)
    def _toggle_hm(self):
        if self._options["heat_map"] == False:
            self._options["heat_map"] = True
        else:
            self._options["heat_map"] = False

    @Slot(None)
    def _toggle_path(self):
        if self._options["vehicle_path"] == False:
            self._options["vehicle_path"] = True
        else:
            self._options["vehicle_path"] = False

    @Slot(None)
    def _warehouse_summary(self):
        if not self.warehouse_obj.layout == None:
            summary = diag.WarehouseSummary(self.warehouse_obj)
            summary.exec()
        else:
            QMessageBox.warning(self, "Summary's unavailable", "Cannot summarize an empty warehouse!")

class ManagerMode(WarehouseMonitorWidget):
    """
    Manager Mode allow full access to all the functions
    """
    def __init__(self, operation) -> None:
        super().__init__(operation)

class TechnicianMode(WarehouseMonitorWidget):
    """
    Technician Mode allow full access to limited number functions (mostly, monitoring, and unit load/unload actions)
    """
    def __init__(self, operation) -> None:
        super().__init__(operation)
        # Limit the Technician functionality
        self._setup_layout_btn.setDisabled(True)
        self._load_warehouse.setDisabled(False)
        self._add_storage_btn.setDisabled(True)
        self._remove_storage_btn.setDisabled(True)
        self._load_storage_btn.setDisabled(False)
        self._add_vehicle_btn.setDisabled(True)
        self._remove_vehicle_btn.setDisabled(True)
        self._add_path_btn.setDisabled(False)