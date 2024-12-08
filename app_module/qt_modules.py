# Main functionalilty (i.e., exit, timer, signal -> slot)
from sys import argv, exit
from PySide6.QtCore import (Qt, 
                            QSize,
                            QCoreApplication, 
                            QAbstractTableModel,
                            QModelIndex,
                            QTimer, 
                            Signal, Slot)
# Widget components
from PySide6.QtWidgets import (QApplication,
                               QMainWindow,
                               QLabel,
                               QPushButton,
                               QComboBox,
                               QLineEdit, QTextEdit,
                               QTabWidget,
                               QToolBar, 
                               QListWidget, 
                               QDialog, QFileDialog,
                               QProgressBar,
                               QMessageBox,
                               QTableView,
                               QHeaderView,
                               QWidget)
# Layout components
from PySide6.QtWidgets import (QHBoxLayout, 
                               QVBoxLayout, 
                               QGridLayout,
                               QFormLayout)
# Miscellaneous components (i.e., font, icons, validators)
from PySide6.QtGui import (QAction, 
                           QFont, 
                           QColor,
                           QIcon, 
                           QIntValidator, 
                           QDoubleValidator)

ICON_PATH = ".//app_module//icon//"
BOLD_FONT = QFont()
BOLD_FONT.setBold(True)