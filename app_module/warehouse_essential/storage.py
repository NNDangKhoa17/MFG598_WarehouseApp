import app_module.warehouse_essential.geometry as geometry
from numbers import Number
import pandas as pd
import numpy as np
"""
Class for Shelf objects used in Warehouse class
"""
class StorageUnit:
    def __init__(self, id : str, center : tuple | list = (0, 0), load_loc : tuple | list = (0, 0), size : Number = 1, capacity : Number = 1, **kwargs) -> None:
        '''
        Define a single Storage unit (Square shape) object using id, size, capacity and center location\n
        '''
        self._id = id
        self._shape = geometry.Square(size, center)
        self.set_capacity(cap = capacity)
        self.set_category(kwargs.get("category", "Generic"))
        self._loading = 0
        self._loading_location = geometry.Position(load_loc)
    
    # ID
    def get_id(self):
        return self._id
    id = property(fget = get_id)
    # Capacity
    def set_capacity(self, cap):
        if cap <= 0:
            raise ValueError("Capacity needs to be a positive number!!!")
        self._capacity = cap
    def get_capacity(self):
        return self._capacity
    capacity = property(fget = get_capacity, fset = set_capacity)
    def get_load(self):
        return self._loading
    def set_load(self, load):
        self._loading = load
    load = property(fget = get_load, fset = set_load)
    # Geometry information
    def get_shape(self):
        return self._shape
    def set_shape(self, shape):
        if isinstance(shape, (geometry.PolygonShape, geometry.Rectangle, geometry.Square)):
            self._shape = shape
    shape = property(get_shape, set_shape)
    # def get_center(self):
    #     return self._center
    # center = property(get_center)
    # Goods category
    def set_category(self, goods_type):
        self._category = goods_type
    def get_category(self):
        return self._category
    category = property(fget = get_category, fset = set_category)
    # Plotting
    def show_shelf(self, ax):
        if self.is_geo_defined:
            self._shape.show_shape(ax, color = "r")
    # misc
    # I/O method
    def unit_info(self, formal = False):
        if formal:
            info = {"ID": self.id,
                "Current load": str(self._loading) + " / " + str(self._capacity),
                "Category": self.category,
                "Shape": self._shape.shape_description(line_description = True).get("description", None),}
        else:
            info = {"id": self.id,
                "cap": self.capacity,
                "load_location": self._loading_location.xy,
                "geo": self._shape.shape_description(),
                "load": self._loading,
                "type": self.category}
        return info
    
    @classmethod
    def load_unit(cls, info_dict : dict):
        id_parameter = info_dict.get("id", None)
        geo_info : dict = info_dict.get("geo", {})
        center = geo_info.get("ref_pt", (0, 0))
        load_location = info_dict.get("load_location", (0, 0))
        size = geo_info.get("dimension", (1, 1))[0]
        capacity = info_dict.get("cap", 1)
        current_load = info_dict.get("load", 0)
        category_des = info_dict.get("type", None)
        if not category_des == None:
            unit = cls(id_parameter, center, load_location, size, capacity, category = category_des)
            unit.load = current_load
        else:
            unit = cls(id_parameter, center, load_location, size, capacity)
            unit.load = current_load
        return unit

    def __add__(self, load): 
        added_load = 0
        if isinstance(load, Number):
            added_load = load  
        if self._loading + added_load > self._capacity:
            raise StorageException(f"Overflow shelf {self._id}'s capacity!!!")
        self._loading += added_load
        return self
    
    def __sub__(self, load):
        subed_load = 0
        if isinstance(load, Number):
            subed_load = load  
        if self._loading - subed_load < 0:
            raise StorageException(f"Underflow shelf {self._id}'s capacity!!!")
        self._loading -= subed_load
        return self
    
    def get_loading_percent(self):
        return self._loading / self._capacity * 100
    load_percent = property(fget = get_loading_percent)

    def __repr__(self):
        return f"Storage Unit ID#{self._id}"
    
    def __str__(self):
        return f"Storage Unit ID#{self._id}"

class Storage():
    def __init__(self):
        self._dataframe = pd.DataFrame(columns = ["id", "unit"])
        self._dataframe.set_index("id")
        self._occupied_zone = []

    def get_storage_dataframe(self):
        return self._dataframe
    def set_storage_dataframe(self, new_data):
        self._dataframe = new_data
    unit_list = property(fget = get_storage_dataframe, fset = set_storage_dataframe)

    def get_occupy(self):
        return self._occupied_zone
    occupied = property(fget = get_occupy)

    def add_unit(self, new_unit : StorageUnit, warehouse_layout : geometry.PolygonShape | None = None, occupied_zone : pd.Series | None = None):
        error_list = []
        new_id = new_unit.id
        # Criterion 1: No duplicate id
        if self._dataframe.index.empty:
            crit1 = True
        else:
            crit1 = not new_id in self._dataframe.index.to_list()
        # Criterion 2: Inside the warehouse (if applicable)
        if not warehouse_layout == None:
            crit2 = warehouse_layout.check_contain(new_unit.shape)
        else:
            crit2 = True
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
        if not crit1:
            error_list.append(f"ID# {new_id} is already in the dataframe!!!")
        if not crit2:
            error_list.append(f"Out of bound! Violation of Warehouse Space!!!")
        if not (crit3 and crit4):
            error_list.append("Collision with existing object(s)")
        combine_cond = crit1 and crit2 and crit3 and crit4
        if combine_cond:
            self._dataframe.loc[new_id, ["id", "unit"]] = [new_id, new_unit]
            self._occupied_zone.append(geometry.Square.from_dict(new_unit.shape.shape_description()))
        return error_list
    
    def storage_info(self):
        info = self._dataframe["unit"].apply(lambda unit : unit.unit_info()).to_list()
        return info

    def load_info(self, unit_infos, warehouse_layout : geometry.PolygonShape | None = None, occupied_zone : pd.Series | None = None):
        _quick_conv = np.vectorize(StorageUnit.load_unit, otypes = [StorageUnit]) # Input an array of storage unit data
        units = _quick_conv(unit_infos)
        for unit in units:
            self.add_unit(unit, warehouse_layout,occupied_zone)
    
    def change_storage_load(self, load_change_data : list, abort_change : bool = False):
        """
        Method to mass change the loading variable of each of the storage unit in the storage dataframe
        The format of each of item in the list load_change_data = [item1, item2, ..., item n] where item(i) is a tuple of (id, action - Load/Unload, delta_load > 0)
        Set abort_change = True to ignore all the change if error occur
        """
        # Handle of error
        error_signal = False
        error_msg = ""
        change_log = [] # list of string, contain change made in the process
        self._dataframe["current_load"] = self._dataframe["unit"].apply(lambda x : x.load) # create a data frame to store original data (in case that revert action needed)
        
        for data in load_change_data:
            try:
                load = float(data[2])
                # Not allow negative load/unload amount
                if load < 0:
                    error_signal = True
                    error_msg = "Negative load detected!!!"
                    break
                elif load == 0:
                    continue # irgnore the value and continue (no error here)
                # Check authorized action
                if data[1] == "Load":
                    msg = f"  \u2022 Storage unit ID# {data[0]}: {self._dataframe['unit'][data[0]].load} \u2192 " #\u2192 : right arrow
                    self._dataframe["unit"][data[0]] + load
                    msg += f"{self._dataframe['unit'][data[0]].load}"
                    change_log.append(msg)
                elif data[1] == "Unload":
                    msg = f"  \u2022 Storage unit ID# {data[0]}: {self._dataframe['unit'][data[0]].load} \u2192 "
                    self._dataframe["unit"][data[0]] - load
                    msg += f"{self._dataframe['unit'][data[0]].load}"
                    change_log.append(msg)
                else:
                    error_signal = True
                    error_msg = "Invalid action!!!"
                    break
            except StorageException as e:
                error_signal = True
                error_msg = e.__str__()
                break
            except ValueError as e:                
                error_signal = True
                error_msg = e.__str__()
                break
            except TypeError as e:                
                error_signal = True
                error_msg = e.__str__()
                break
            except KeyError:                
                error_signal = True
                error_msg = "Invalid ID detected!!!"
                break
            except Exception:
                error_signal = True
                error_msg = "Unknown error!!!"
                break
        if error_signal and abort_change:
            self._dataframe.apply(lambda row : row["unit"].set_load(row["current_load"]), axis = 1)
            # Remove the addtional data frame
            self._dataframe = self._dataframe.drop(columns=["current_load"])
            change_log = []
        return (not error_signal), error_msg, change_log

    def clear_all(self):
        """
        Wipe out all the storage units from the dataframe
        """
        self._dataframe = self._dataframe.iloc[0:0]

    def _is_empty(self):
        return self._dataframe.index.empty
    """
    Return whether there is any unit in the current Storage 
    """
    empty = property(fget = _is_empty)  
    

class StorageException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
