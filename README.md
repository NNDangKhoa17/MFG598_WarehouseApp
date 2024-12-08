# MFG598_WarehouseApp
## Project Description
The application is aimed to provide monitoring assistance for automatic warehouse (i.e. warehouse capacity, mobile robots operation) via visualization of the real-time operation.
The program also give certain control to the virtual warehouse management, error preventation and notifications.
## Program structure
### Warehouse essential modules
Warehouse essential modules are stored inside app_module.warehouse_essential.
- geometry: module for defining and displaying object and shape (the shape is defined using Shapely 2.0.6 and Matplotlib)
- storage: module of storage unit class and the dataframe contains all storage units
- vehicle: module of vehicle (i.e., AGV, robots) class and the dataframe contains all vehicle units
- operation_shift: module for controlling the operation (limit to only one operationg at a time) and the authorization of a person using the application
- warehouse: module for warehouse class
### UI Component modules
The graphical interface of the application (programmed using PySide 6.8.0 - a Python-version of Qt). These modules are combine in qt_modules file and can be listed as
- data_viewer: list widgets, tables, text editors, labels that support the visualization of data (i.e., working time, operator infomation, event nofitications)
- login: the module for handling the login/logout operation
- support_diaglog: pop-up diaglog for various purposes
- warehouse_monitor_widget: a main widget for warehouse monitor
