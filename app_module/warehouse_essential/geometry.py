import numpy as np
from shapely import Point, Polygon, plotting, affinity, LineString
# import pandas as pd
# from matplotlib import pyplot as plt
import matplotlib as mpl
from numbers import Number

physics_status = ("physical", "virtual", "semi-virtual")

class Position(): # 2D-Plane only
    def __init__(self, xy_tuple : tuple | list | np.ndarray  = (0, 0), **kwargs) -> None:
        '''
        Initialize the Position object based on the Point geometry of shapely.
            Method 1: Position(tuple(x_coor, y_coor))
            Method 2: Position(x = ..., y = ...)
        '''
        # Create from x, y
        x = kwargs.get("x", None)
        y = kwargs.get("y", None)
        if x and y:
            self._pos = Point(x, y)
            return None        
        if isinstance(xy_tuple, (list, tuple, np.ndarray)):
            self._pos = Point(xy_tuple)
            return None
        # End of __init__()
    # Point-type expression
    def get_pos(self):
        return self._pos
    def set_pos(self, position : tuple):
        self._pos = Point(position[0], position[1])
    pos = property(fget = get_pos, fset = set_pos)
    # x
    def get_x(self):
        return self._pos.x
    def set_x(self, x):
        if not isinstance(x, Number):
            raise TypeError("Only accept numerical value for x-coordinate")
        self._x = x
    x = property(fget = get_x, fset = set_x)
    # y
    def get_y(self):
        return self._pos.y
    def set_y(self, y):
        if not isinstance(y, Number):
            raise TypeError("Only accept numerical value for y-coordinate")
        self._y = y
    y = property(fget = get_y, fset = set_y)
    # x, y
    def get_xy(self):
        return self._pos.x, self._pos.y
    xy = property(fget = get_xy)
    # Find distance to other position
    def get_dist(self, other):
        if not isinstance(other, [Position, Point]):
            raise GeometryException("Expected another position")
        dist = self._pos.distance(other._pos)
        return dist
    # + and - operator overloading
    def __add__(self, other):
        if isinstance(other, (Position, Point)):
            x = self._pos.x + other.x
            y = self._pos.y + other.y
        elif isinstance(other, (tuple, list, np.ndarray)):
            x = self._pos.x + other[0]
            y = self._pos.y + other[1]
        return Position((x, y))
    # + and - operator overloading
    def __sub__(self, other):
        if isinstance(other, (Position, Point)):
            x = self._pos.x - other.x
            y = self._pos.y - other.y
        elif isinstance(other, (tuple, list, np.ndarray)):
            x = self._pos.x - other[0]
            y = self._pos.y - other[1]
        return Position((x, y))
    # str and repr
    def __str__(self):
        return f"P({self.x:.2f}, {self.y:.2f})"    
    def __repr__(self):
        return f"P({self.x:.2f}, {self.y:.2f})"

class Orientation():
    def __init__(self, angle : float | int = 0, deg_type = "rad"):
        if deg_type == "deg":
            angle = np.deg2rad(angle)
        self._omega = self.standardize(angle)
    def set_orientation(self, angle):
        """
        Orientation setter
        """
        angle = self.standardize(angle)
        self._omega = angle
    w = property(fget = lambda self: self._omega, fset = set_orientation)
    def standardize(self, angle : float | int) -> float:
        """
        Map angle value to -pi to pi
        """
        angle = angle % (2 * np.pi) # Map into 0 to 2pi range
        if np.abs(angle) > np.pi and angle > 0:
            angle = 2 * np.pi - angle
        elif np.abs(angle) > np.pi and angle < 0:
            angle = -2 * np.pi - angle
        return angle
    def points2angle(self, src : Position, dest : Position):
        try:
            delta_y = dest.y - src.y
            delta_x = dest.x - src.x
            tan_val = delta_y/delta_x
        except ZeroDivisionError:
            tan_val = np.inf
        except:
            pass
        return tan_val

    def __iadd__(self, other : float | int):
        """
        + Operator
        """
        self._omega += other
        self._omega = self.standardize(self._omega)
        return self
    def __isub__(self, other : float | int):
        """
        - Operator
        """
        self._omega -= other
        self._omega = self.standardize(self._omega)
        return self
    def __str__(self):
        return str(self._omega)
    
# Linked List
class Node():
        def __init__(self, val = None, next_node = None):
            self._val = val
            self.set_next(next_node)
        
        value = property(fget = lambda self: self._val)
        def get_next(self):
            return self._next
        def set_next(self, next_node = None):
            self._next = next_node
        next = property(fget = get_next, fset = set_next)

class LinkedList():
    def __init__(self):
        self._head = None
        self._current = self._head
        self._tail = None
        self._size = 0

    def get_head(self):
        return self._head
    def set_head(self, node : Node):
        self._head = node
    head = property(fget = get_head, fset = set_head)
    # current = property(fget = lambda self : self._current)

    def next_node(self):
        if not self._current.next == None:
            self._current = self._current.next

    def get_size(self):
        return self._size
    size = property(fget = get_size)

    def add_node(self, new_node : Node):
        self._size += 1
        if self._head == None:
            self.set_head(new_node)
            self._current = self._head
            self._tail = self._head
        else:
            self._tail.next = new_node
            self._tail = self._tail.next

    def begin(self):
        self._current = self._head

    def _is_iterable(self):
        if self._current == None:
            return False
        if self._current.next == None:
            return False
        return True
    is_iterable = property(fget = _is_iterable)
    def iter(self):
        output = self._current
        self._current = self._current.next
        return output.value
    def clear(self):
        """
        Clear the whole list
        """        
        current = self._head
        while not current == None:
            temp = current.next
            del current
            current = temp
        # Reassign an empty linked list
        self.__init__()

class Path():
    def __init__(self, pos_list = [], other_path = None):
        self._path_data = LinkedList()
        self.add_node(*pos_list)
        if not other_path == None:         
            if not isinstance(other_path, Path):
                raise GeometryException("Invalid Path object!!!")
            self.add_path(other_path)
    
    def add_node(self, *args):
        for pos in args:
            try:
                pos = Position(pos)
            except:
                continue # Ignore wrong argument (those cannot create a Position)
            else:
                self._path_data.add_node(Node(pos))
    def add_path(self, other_path):
        self._path_data.add_node(other_path._path_data.head)
    def get_path_data(self):
        return self._path_data
    path_data = property(fget = get_path_data)
    def get_path_length(self):
        n = len(self._path_data)
        if n > 1:
            path_lens = [self._path_data[k].get_dist(self._path_data[k+1]) for k in range(0, n-1)]
            return sum(path_lens)
        return 0
    def _is_empty(self):
        if self._path_data.head == None:
            return True
        return False
    empty = property(fget = _is_empty)
    def __add__(self, *args):
        for arg in args:
            if isinstance(arg, Path):
                self.add_path(arg)
            else:                
                self.add_node(arg)
        return self
    def print_path(self):
        current = self._path_data.head
        while self._path_data.is_iterable:
            # print(current.value)
            current = self._path_data.iter()


class PolygonShape():
    def __init__(self, ref : tuple = (0, 0), buffer = None):
        self._ref = Position(ref)
        self._polygon = Polygon()
        if isinstance(buffer, Number) and buffer > 0:
            self._buffer_size = buffer
        else:
            self._buffer_size = 0

        if not self._polygon.is_empty:
            self._buffer = self._polygon.buffer(self._buffer_size)
    def get_shape_polygon(self):
        return self._polygon
    def set_shape_polygon(self, polygon : Polygon):
        self._polygon = polygon
    polygon = property(fget = get_shape_polygon, fset= set_shape_polygon)
    def show_shape(self, ax = None, **kwargs) -> False:
        color = kwargs.get("color", "b")
        boundary_color = kwargs.get("boundary_color", "b")
        if not isinstance(ax, mpl.axes.Axes):
            pass
        else:
            plotting.plot_polygon(self._polygon, ax, add_points = False, facecolor = color, edgecolor = boundary_color)
            return True
    def show_ref(self, ax = None, **kwargs) -> False:
        if not isinstance(ax, mpl.axes.Axes):
            pass
        else:
            plotting.plot_points(self._ref.pt_repr, ax, color = "r")
            return True
    def check_interference(self, other):
        try:
            res = self.polygon.intersects(other.polygon)
        except:
            pass
        else:
            return res
    def check_contain(self, other):
        try:
            res = self._polygon.contains_properly(other._polygon)
        except:
            pass
        else:
            return res
    def translate(self, current_loc : Position, new_loc : Position | None = None):
        if not new_loc == None:
            self.polygon = affinity.translate(self.polygon, xoff = new_loc.x - current_loc.x, yoff = new_loc.y - current_loc.y)
            self._ref = new_loc

class Rectangle(PolygonShape):
    def __init__(self, length = None, width = None, ref = (0, 0), buffer = None, **kwargs):
        super().__init__(ref, buffer)
        # Check validity of length and width
        if not isinstance(length, Number):
            raise GeometryException("Invalid data type for length!!!")
        if length <= 0:
            raise GeometryException("Length has to be a positive value!!!")
        if not isinstance(width, Number):
            raise GeometryException("Invalid data type for width!!!")
        if width <= 0:
            raise GeometryException("Width has to be a positive value!!!")
        self._ref_pt_type = kwargs.get("ref_pt_type", "center")
        if not self._ref_pt_type in ("center", "corner"):
            # center reference point or lower-left corner reference point
            raise GeometryException("Invalid reference type!!!")
        
        if self._ref_pt_type == "corner":
            c0 = self._ref.xy
            c1 = (self._ref + (length, 0)).xy
            c2 = (self._ref + (length, width)).xy
            c3 = (self._ref + (0, width)).xy
        else:            
            half_length = length / 2
            half_width = width / 2
            c0 = (self._ref + (-half_length, -half_width)).xy
            c1 = (self._ref + (half_length, -half_width)).xy
            c2 = (self._ref + (half_length, half_width)).xy
            c3 = (self._ref + (-half_length, half_width)).xy
        coors = (c0, c1, c2, c3)
        self._polygon = Polygon(coors)
        self._size = length, width
    
    @classmethod
    def from_dict(cls, dictionary : dict):
        size = dictionary["dimension"]
        ref_pt_type = dictionary.get("ref_pt_type", "center")
        ref = dictionary.get("ref_pt", (0, 0))
        buffer = dictionary.get("buffer", 0)
        l_val, w_val = size
        rec = cls(l_val, w_val, ref, buffer, ref_pt_type = ref_pt_type)
        return rec

    def _is_defined(self):
        try:
            if not self.__dict__.get("_polygon", None):
                return False
        except:
            return False
        else:
            return True
    is_defined = property(_is_defined)

    def shape_description(self, line_description = False):
        """
        Return a dictionary of critical parameters of the shape
            OR
        Return a readable description of the current shape (set line_description = True)
        """
        if self.is_defined:
            if not line_description:
                geometry_dict = {"type": "Rectangle", "dimension": self._size, "ref_pt_type": self._ref_pt_type, "buffer": self._buffer_size,"ref_pt": self._ref.xy}
            else:
                geometry_dict = {"description": f"Rectangle of size ({self._size[0]}x{self._size[1]})"}
            return geometry_dict
        return {"type": "Rectangle"}

class Square(Rectangle):
    def __init__(self, side = None, ref = None, buffer = None, **kwargs):
        super().__init__(side, side, ref, buffer, **kwargs)

    def shape_description(self, line_description = False):
        """
        Return a dictionary of critical parameters of the shape 
            OR
        Return a readable description of the current shape (set line_description = True)
        """
        if not line_description:
            geometry_dict = super().shape_description()
            geometry_dict["type"] = "Square"
        else:
            geometry_dict = {"description": f"Square of size ({self._size[0]})"}
        return geometry_dict
    @classmethod
    def from_dict(cls, dictionary : dict):
        size = dictionary["dimension"]
        ref_pt_type = dictionary.get("ref_pt_type", "center")
        ref = dictionary.get("ref_pt", (0, 0))
        buffer = dictionary.get("buffer", 0)
        s_val, s_val = size
        rec = cls(s_val, ref, buffer, ref_pt_type = ref_pt_type)
        return rec
        
class GeometryException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __str__(self) -> str:
        return super().__str__()
