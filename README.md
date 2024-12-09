# MFG598_WarehouseApp
## Project Description
The application is aimed to provide monitoring assistance for automatic warehouse (i.e. warehouse capacity, mobile robots operation) via visualization of the real-time operation.
The program also give certain control to the virtual warehouse management, error preventation and notifications.
## Program structure
### Warehouse essential modules
Warehouse essential modules are stored inside app_module.warehouse_essential.
- __geometry:__ module for defining and displaying object and shape (the shape is defined using **Shapely 2.0.6** and **Matplotlib**)
- __storage:__ module of storage unit class and the dataframe contains all storage units
- __vehicle:__ module of vehicle (i.e., AGV, robots) class and the dataframe contains all vehicle units
- __operation_shift:__ module for controlling the operation (limit to only one operationg at a time) and the authorization of a person using the application
- __warehouse:__ module for warehouse class
### UI Component modules
The graphical interface of the application (programmed using PySide 6.8.0 - a Python-version of Qt). These modules are combine in qt_modules file and can be listed as
- __data_viewer:__ list widgets, tables, text editors, labels that support the visualization of data (i.e., working time, operator infomation, event nofitications)
- __login:__ the module for handling the login/logout operation
- __support_diaglog:__ pop-up diaglog for various purposes
- __warehouse_monitor_widget:__ a main widget for warehouse monitor
## External Public modules
- __Pandas:__ for managing the units of storage and vehicle
- __Numpy:__ usage of the `@np.vectorize` decorator for multiple units modifying
- __Matplotlib:__ for ploting the heatmap and vehicle motion
- __Shapely:__ for generating geometric entities such as **Point**, **LineString**, and **Polygon**
- __GeoPandas:__ similar to pandas module with additional functionalities for geometric entities
- __PySide__: GUI module
#### References
__[1]__ Qt 6.8. Qt documentation. (n.d.). https://doc.qt.io/qt-6/index.html 
