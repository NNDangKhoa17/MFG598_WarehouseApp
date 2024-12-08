from app_module.warehouse_essential.storage import Storage, StorageUnit, StorageException
from app_module.warehouse_essential.vehicle import Vehicles, VehicleUnit
import app_module.warehouse_essential.geometry as geometry
import geopandas as pgd
import pandas as pd
from matplotlib import pyplot as plt
from os import makedirs
from json import load as js_load, dump as js_dump
import numpy as np

DEFAULT_WAREHOUSE_PATH = ".\\Metadata\\WarehouseData"
try:
    makedirs(DEFAULT_WAREHOUSE_PATH)
except FileExistsError:
    pass

# Assume the warehouse floor plan is of rectangular shape 
class Warehouse():
    def __init__(self, len_val : int | float | None = None, width_val : int | float | None = None, ref = (0,0)) -> None:
        try:
            self._layout = geometry.Rectangle(length = len_val, width = width_val, ref = ref, ref_pt_type = "corner")
        except:
            self._layout = None
        # Occupied zone == area that is placed with storage units & vehicles docking (does not include temporary locations of moving vehicles)
        self._occupied_zone = pd.Series() # Only for placement
        
        # Storage unit data frame
        self._storage_units : Storage = Storage()
        self._vehicles : Vehicles = Vehicles()

    @classmethod 
    def load_info(cls, filename = DEFAULT_WAREHOUSE_PATH + "\\autosave.json"):
        """
        Load warehouse info from a file (.json)
        """
        try:
            with open(filename, mode = "r") as file:
                info_dict : dict = js_load(file)
        except:
            raise Exception("No records of warehouse found!!!")
        else:
            layout_info : dict = info_dict.get("layout", {})
            size = layout_info.get("dimension", (1, 1))
            l_val, w_val = size
            ref = layout_info.get("ref_pt", (0, 0))
            warehouse = cls(l_val, w_val, ref)
            storage_info : list = info_dict.get("storage", [])
            vehicle_info : list = info_dict.get("vehicle", [])
            warehouse._storage_units.load_info(storage_info, warehouse.layout)
            warehouse._vehicles.load_info(vehicle_info, warehouse.layout)
            warehouse.update_placement_occupied_zone()
            return warehouse

    def get_layout(self, info_type = None):
        if not self._layout == None:
            if info_type == "dict":
                return self._layout.shape_description()
            if info_type == "description":
                return self._layout.shape_description(line_description = True)
            return self._layout
        return None
    def set_layout(self, layout : geometry.PolygonShape):
        self._layout = layout
    layout = property(fget = get_layout, fset = set_layout)

    def get_storage_units(self):
        return self._storage_units
    storage = property(fget = get_storage_units)
    def get_vehicles(self):
        return self._vehicles
    vehicles = property(fget = get_vehicles)

    def add_storage_unit(self, new_unit : StorageUnit):
        if not self.layout == None: 
            out_str = self._storage_units.add_unit(new_unit, self.layout, self._occupied_zone)
            return True, out_str
        return False, out_str

    def add_storage_units(self, *args):
        _quick_add = np.vectorize(self.add_storage_unit, otypes = [bool])
        _quick_add(args)

    def storage_load_change(self, load_def : list):
        success, err_msg, changes = self._storage_units.change_storage_load(load_def, abort_change = True)
        return success, err_msg, changes
    
    def remove_storage_unit(self, id, ignore_error : bool = False):
        if id in self._storage_units.unit_list.index:
            self._storage_units.unit_list = self._storage_units.unit_list.drop([id])
        else:
            if ignore_error:
                raise ValueError("The requested ID does not exist!!!")
        
    def remove_vehicle_unit(self, id, ignore_error : bool = False):
        """
        Remove a vehicle unit in the existing warehouse
        """
        if id in self._vehicles.unit_list.index:
            self._vehicles.unit_list = self._vehicles.unit_list.drop([id])
        else:
            if ignore_error:
                raise ValueError("The requested ID does not exist!!!")

    # Vehicle
    def add_vehicle_unit(self, new_unit : VehicleUnit):
        if not self.layout == None:
            out_str = self._vehicles.add_unit(new_unit, self.layout, self._occupied_zone)
            self._occupied_zone : geometry.Polygon = new_unit.shape 
            return True, out_str
        return False, out_str

    def add_vehicle_units(self, *args):
        _quick_add = np.vectorize(self.add_vehicle_unit, otypes = [bool])
        _quick_add(args)

    def save_data(self, filename = "autosave.json"):
        with open(DEFAULT_WAREHOUSE_PATH + "\\" + filename, mode = "w") as file:
            # Layout data
            layout_data = self.get_layout("dict")
            # Storage unit
            storage_data = self._storage_units.storage_info()
            vehicle_data = self._vehicles.vehicle_info()
            data = {"layout": layout_data, "storage": storage_data, "vehicle": vehicle_data}
            if not isinstance(layout_data, Exception):
                js_dump(data, file)
            else:
                pass
    
    def collision_check(self):
        collision_list = [] # List of collision records (type: str)
        vehicles = self._vehicles.unit_list["unit"].to_list()
        storage = self._storage_units.unit_list["unit"].to_list()
        all_occupants = vehicles + storage
        # quick_check = np.vectorize(VehicleUnit.collision_with, otypes = bool)
        # self._vehicles.unit_list["unit"].apply(quick_check)
        for vehicle in self._vehicles.unit_list["unit"].to_list():
            for occupant in all_occupants:
                collied, obj = vehicle.collision_with(occupant)
                if collied:
                    collision_list.append(obj)
                    collision_message = f"{vehicle.__str__()} collides with {obj.__str__()}"
                    return collision_message
        return ""

    # Plotting
    def show(self, ax, heat_display = True, path_display = True):
        """
        Plot the warehouse on some canvas
        """
        # self.layout.show_shape(ax = ax, color = "silver", boundary_color = "k")
        layout = self.layout.polygon
        layout = pgd.GeoSeries(layout)
        cmap = plt.get_cmap('jet')
        storage_data : pd.Series = self._storage_units.unit_list["unit"]
        loading_data = storage_data.apply(lambda x: float(x.load_percent))
        loading_data = loading_data.apply(lambda x: cmap(x / 100)).to_list()
        storage_units_geometry = storage_data.apply(lambda x: x.shape.polygon)
        storage_units_geometry = pgd.GeoSeries(storage_units_geometry)
        vehicles_geometry = self._vehicles.unit_list["unit"].apply(lambda x: x.shape.polygon)
        vehicles_geometry = pgd.GeoSeries(vehicles_geometry)
        vehicles_trail = self._vehicles.unit_list["unit"].apply(lambda x: x.trail).to_list()
        vehicles_trail = [trail for trail in vehicles_trail if not trail.is_empty]
        vehicles_trail = pgd.GeoSeries(vehicles_trail)
        if not layout.empty:
            layout.plot(ax = ax, color = "silver", edgecolor = "k")
            if not storage_units_geometry.empty:
                if heat_display:
                    storage_units_geometry.plot(ax = ax, color = loading_data)
                else:
                    storage_units_geometry.plot(ax = ax, color = "r")
            if not vehicles_geometry.empty:
                vehicles_geometry.plot(ax = ax, color = "#A020F0", edgecolor = "k")
            if not vehicles_trail.empty:
                if path_display:
                    vehicles_trail.plot(ax = ax, color = "k", edgecolor = "k")

    def update_placement_occupied_zone(self):
        storage_zone = self._storage_units.occupied
        vehicle_zone = self._vehicles.occupied
        occupied_zone_list = storage_zone + vehicle_zone
        self._occupied_zone = pd.Series(occupied_zone_list)

    # def update_occupied_zone(self):
    #     storage_zone = self._storage_units.occupied_zone()
    #     vehicle_zone = self._vehicles.occupied_zone()
    #     occupied_zone_list = storage_zone + vehicle_zone
    #     self._occupied_zone = pd.Series(occupied_zone_list)
