import numpy as np
import pandas as pd
# from json import dump, load
from datetime import datetime as dt
import app_module.warehouse_essential.geometry as geometry
from copy import deepcopy

class VehicleUnit():
    def __init__(self, id = None, dock_loc : tuple = (0,0), current_position : tuple | None = None, size : tuple = (1, 1), battery_cap : int = 100):
        """
        Assign a new vehicle with:
          - ID
          - Capacity
          - Location
          - Shape & Size
        """
        self.set_id(id)
        self._loading = 0
        self._dock_location = geometry.Position(dock_loc)
        self._shape = geometry.Rectangle(size[0], size[1], ref = (self._dock_location.xy), buffer = 0.5)
        self.set_battery(battery_cap)
        self._trail = []
        self._active = True # no error to stop normal operation (i.e., no collision)
        self.set_path([])
        if current_position == None:
            self._kinematic = Kinematic(dock_loc)
            self._shape = geometry.Rectangle(size[0], size[1], ref = (self._dock_location.xy), buffer = 0.5)
        else:
            self._kinematic = Kinematic(current_position)
            self._shape = geometry.Rectangle(size[0], size[1], ref = current_position, buffer = 0.5)        
        
    # Vehicle ID
    def set_id(self, id):
        self._id = id
    def get_id(self):
        return self._id
    def _is_defined(self): # Check whether the vehicle has ID or not
        return not self._id == None
    id = property(fget = get_id, fset = set_id)
    is_defined = property(fget = _is_defined)
    
    # Docking location
    def get_docking(self):
        return self._dock_location.xy
    def set_docking(self, position : tuple):
        self._dock_location = geometry.Position(position)
    dock_loc = property(fget = get_docking, fset = set_docking)

    # Vehicle shape
    def get_shape(self):
        return self._shape
    shape = property(fget = get_shape)
    
    # Vehicle's kinematic infomation
    def set_kinematic(self, position, orient = 0, initial_velo = (0, 0)):
        self._kinematic = Kinematic(position, orient, initial_velo)
    # Vehicle position
    def set_pos(self, loc):
        self._kinematic.pos = loc
    def get_pos(self):
        return self._kinematic.pos
    pos = property(fget = get_pos, fset = set_pos)
    # Vehicle orientation
    def set_ort(self, ort):
        self._kinematic.set_ort(ort)
    def get_ort(self):
        return self._kinematic.get_ort()
    ort = property(fget = get_ort, fset = set_ort)
    # Vehicle velocity
    def set_velo(self, velocity_tuple):
        self._kinematic.set_velo(velocity_tuple)
    def get_velo(self):
        return self._kinematic.get_velo()
    def get_motion(self):
        velo_list = np.array(self._kinematic.get_velo())
        if len(velo_list[velo_list != 0]) > 0:
            return "Moving"
        return "Resting"
    velocity = property(fget = get_velo, fset = set_velo)
    # Vehicle path
    def set_path(self, position_list):
        success = True
        error_msg = ""
        if self._active: # Only active_vehicle is allow to get new_path
            self._path = geometry.Path(position_list)
            return success, error_msg
        else:
            self._path = geometry.Path([])
            success = False
            error_msg = "Unable to set new path due to unit's inactivity! Resolve inactivity before attempting to set new path!!!"
            return success, error_msg
    def get_path(self):
        return self._path
    def get_path_dist(self):
        return self._path
    path = property(fget = get_path, fset = set_path)
    path_length = property(fget = get_path_dist)
    def path_finish_signal(self):
        time = dt.now()
        dist = self.path_length
        remain_batt = self._battery
        tempt = pd.DataFrame({"Datetime": time.strftime("%Y-%m-%d %H:%M:%S"), "Moving Distance":  f"{dist}", "Remaining battery": remain_batt}, index = [0])
    def get_trail(self):
        if len(self._trail) > 1:
            return geometry.LineString(self._trail)
        else:
            return geometry.LineString([])
    trail = property(fget = get_trail)
    # Vehicle battery
    def set_battery(self, percent):
        try:
            percent = int(percent)
        except ValueError:
            self._battery = 0
        else:
            if percent > 100:
                self._battery = 100
            elif percent <= 0:
                self._battery = 0
            else:
                self._battery = percent
    def get_battery(self):
        return self._battery
    battery = property(fget = get_battery, fset = set_battery)

    # Active vs. Inactive
    def get_active(self):
        return self._active
    active = property(fget = get_active)

    # Moving vs. Resting
    def get_motion(self):
        if not self._path.empty:
            if self._path.path_data.is_iterable:
                return "Moving"
        return "Resting"
    motion = property(fget = get_motion)


    def move_to(self, new_loc : geometry.Position):
        """
        Method to set the vehicle to move to a specific location
        """
        self._trail.append(self._kinematic.pos)
        if not new_loc == None:
            self._shape.translate(geometry.Position(self._kinematic.pos), new_loc)
            self.set_pos((new_loc.x, new_loc.y),)
            # self._complete_path.append(geometry.Point(new_loc.x, new_loc.y),)
            
    def move(self):
        if not self._path.empty:
            if self._path.path_data.is_iterable:
                location = self._path.path_data.iter()
                self.move_to(location)
            else:
                self._path.path_data.clear()
                self._trail = [] # Clear trail after the path is finished

    def unit_info(self, formal = False):
        if formal:
            return {"ID": self.id, "Docking Location": self._dock_location.xy, "Curent Location": self._kinematic.pos, "Shape": self._shape.shape_description(line_description = True).get("description", None), "Current battery": self.battery}
        return {"id": self.id, "dock_location": self._dock_location.xy, "geometry": self._shape.shape_description(), "battery": self.battery}
    
    @classmethod
    def load_unit(cls, info_dict : dict):
        vehicle_id = info_dict.get("id", None)
        dock_location = info_dict.get("dock_location", (0, 0))
        geometry = info_dict.get("geometry", None)
        size = geometry["dimension"]
        current_position = geometry["ref_pt"]
        battery = info_dict["battery"]
        vehicle = cls(vehicle_id, dock_location, current_position, size, battery)
        return vehicle

    def collision_with(self, other) -> bool:
        if self._active == True:
            if other == self:
                return False, None # ignore itself
            if other.shape.check_interference(self.shape):
                self.path.path_data.clear()
                self._active = False # make the vehicle inactive and remove its from collision check (it does not mean it won be served as obstacle)
                return True, other
            return False, None    
        return False, None # If false (no collision), return empty tuple in the result

    def forced_homing(self):
        """
        Force the vehicle back to the home (docking location)
        """
        self.move_to(self._dock_location)
        return self

    def __repr__(self) -> str:
        if self.is_defined:
            return f"Vehicle ID#{self.id}"
        return "Vehicle"
    
    def __str__(self) -> str:
        if self.is_defined:
            return f"Vehicle ID#{self.id}"
        return "Vehicle"

    # def __str__(self) -> str:
    #     msg = "Vehicle Information\n"
    #     msg += f"Position: {self.get_pos()} - Orientation: {self.get_ort()}\n"
    #     msg += f"Velocity: {self.get_velo()}\n - Status: {self.get_motion()}\n"
    #     msg += f"Remaining battery: {self._battery}%"
    #     return msg


class Vehicles():
    def __init__(self) -> None:
        self._dataframe = pd.DataFrame(columns = ["id", "unit"])
        self._dataframe.set_index("id")
        self._occupied_zone : list = []

    def get_dataframe(self):
        return self._dataframe
    def set_dataframe(self, data : pd.DataFrame):
        self._dataframe = data
    unit_list = property(fget = get_dataframe, fset = set_dataframe)

    def get_occupy(self):
        return self._occupied_zone
    occupied = property(fget = get_occupy)

    def add_unit(self, new_unit : VehicleUnit, warehouse_layout = None, occupied_zone : pd.Series | None = None):
        """
        Add a new unit of vehicle into the Vehicle dataframe
        Return list of errors if fail otherwise, an empty list
        """
        error_list = []
        new_id = new_unit.id
        add_shape : geometry.PolygonShape = deepcopy(new_unit.shape)
        # Criterion 1: No duplicate id
        if self._dataframe.index.empty:
            crit1 = True
        else:
            crit1 = not new_id in self._dataframe.index.to_list()
        # Criterion 2: Inside the warehouse (if applicable)
        if not warehouse_layout == None:
            # At the current position
            crit2_1 = warehouse_layout.check_contain(add_shape)
            # At the docking position
            add_shape.translate(geometry.Position(new_unit.pos), geometry.Position(new_unit.dock_loc))
            crit2_2 = warehouse_layout.check_contain(add_shape)
            crit2 = crit2_1 and crit2_2
        else:
            crit2 = True # ignore the condition
        # Criterion 3: No collision
        if isinstance(occupied_zone, pd.Series): # zones is of type Polygon & Point
            if occupied_zone.empty:
                crit3 = True
            else:
                crit3 = not occupied_zone.apply(lambda zones, new_unit: zones.check_interference(new_unit), args = (new_unit.shape,)).sum()
        else:
            crit3 = True
        # Criterion 4: No collision (in case no occupied zone is provided)
        if self._dataframe.index.empty:
            crit4 = True
        else:
            crit4 = not self._dataframe["unit"].apply(lambda units, new_unit: units.shape.check_interference(new_unit), args = (new_unit.shape,)).sum()
        # Criterion 5: No collision with orther object in docking position
        if self._dataframe.index.empty:
            crit5 = True
        else:
            all_vehicle_at_dock : pd.Series = self._dataframe["unit"].apply(lambda unit : deepcopy(unit)) # deepcopy to avoid tamper with original data
            all_vehicle_at_dock = all_vehicle_at_dock.apply(lambda unit : unit.forced_homing())
            crit5 = not all_vehicle_at_dock.apply(lambda units : units.shape.check_interference(add_shape)).sum()
        if not crit1:
            error_list.append(f"ID# {new_id} is already in the dataframe!!!")
        if not crit2:
            error_list.append(f"Out of bound! Violation of Warehouse Space!!!")
        if not crit3:
            if not "Collision with existing object(s)" in error_list:
                error_list.append("Collision with existing object(s)")
        if not crit4:
            if not "Collision with existing object(s)" in error_list:
                error_list.append("Collision with existing object(s)")
        if not crit5:
            error_list.append("Docking location violation! Docking space is occupied!!!")
        combine_cond = crit1 and crit2 and crit3 and crit4 and crit5
        if combine_cond:
            self._dataframe.loc[new_id, ["id", "unit"]] = [new_id, new_unit]
            self._occupied_zone.append(geometry.Rectangle.from_dict(new_unit.shape.shape_description()))
        return error_list

    def vehicle_info(self):
        info = self._dataframe["unit"].apply(lambda unit : unit.unit_info()).to_list()
        return info

    def load_info(self, unit_infos, warehouse_layout : geometry.PolygonShape | None = None, occupied_zone : pd.Series | None = None):
        """
        Method for mass conversion of data of multiple vehicles into VehicleUnit(s)
        """
        _quick_conv = np.vectorize(VehicleUnit.load_unit, otypes = [VehicleUnit]) # Input an array of storage unit data
        units = _quick_conv(unit_infos)
        for unit in units:
            self.add_unit(unit, warehouse_layout, occupied_zone) 
    
    def clear_all(self):
        """
        Wipe out all the vehicle units from the dataframe
        """
        self._dataframe = self._dataframe.iloc[0:0]

class Kinematic():
    def __init__(self, position_tuple: tuple = (0, 0), angle:  int | float = 0, velocity_tuple: tuple = (0, 0)):
        self._position = geometry.Position(position_tuple)
        self._orientation = geometry.Orientation(angle)
        self._velocity = velocity_tuple
        
    # Position information
    def set_pos(self, pos : tuple):
        self._position = geometry.Position(pos)
    def get_pos(self):
        return self._position.xy
    pos = property(fget = get_pos, fset = set_pos)
    # Orientation information
    def set_ort(self, angle:  int | float = 0):
        self._orientation = geometry.Orientation(angle)
    def get_ort(self):
        return self._orientation
    ort = property(fget = get_ort, fset = set_ort)
    # Velocity information
    def set_velo(self, velo_tuple = (0, 0)):
        self._velocity = velo_tuple
    def get_velo(self):
        return self._velocity[0], self._velocity[1]
    def get_v(self):
        return self._velocity[0]
    def get_w(self):
        return self._velocity[0]
    velocity = property(fget = get_velo, fset = set_velo)
    v = property(fget = get_v)
    w = property(fget = get_w)
    # Representation func
    def __str__(self):
        # pos = self._pos.get_xy()
        msg = "Kinematic infomation:\n"
        msg += f"x = {self.pos[0]}, y = {self.pos[1]}, Phi = {self._orientation}\n"
        msg += f"v = {self.v}, w = {self.w}"
        return msg
