from app_module.qt_modules import *
import app_module.warehouse_essential.operation_shift as ops

class Login(QDialog):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()
        # Form for info input
        layout = QFormLayout()
        self._id = QLineEdit()
        self._id.setPlaceholderText("Username")
        self._id.setText("knn1")
        self._pwd = QLineEdit()
        self._pwd.setPlaceholderText("Password")
        self._pwd.setText("nome1")
        self._pwd.setEchoMode(QLineEdit.Password) # To hide the password
        # Information input
        self._id.textEdited.connect(self.info_change)
        self._pwd.textEdited.connect(self.info_change)
        layout.addRow("Username/IDs", self._id)
        layout.addRow("Password", self._pwd)
        
        # Push buttons (i.e., OK, Quit)
        btn_layout = QHBoxLayout()
        self._login_btn = QPushButton("Login")
        # self._login_btn.setEnabled(False)
        self._login_btn.clicked.connect(self._login_pressed)
        _cancel_btn = QPushButton("Cancel/Exit")
        _cancel_btn.clicked.connect(self._cancel_pressed)
        btn_layout.addWidget(self._login_btn)
        btn_layout.addWidget(_cancel_btn)
        
        # Main layout
        main_layout.addLayout(layout)
        main_layout.addLayout(btn_layout)
        self.setFixedSize(400, 120)
        self.setLayout(main_layout)
        self.setWindowTitle("Login")
        self.setWindowIcon(QIcon(ICON_PATH + "lock.png"))
        # Misc
        self._attempt = 0

    def _login_pressed(self):
        id = self._id.text()
        pwd = self._pwd.text()

        if self._verified_login(id, pwd):
            self._attempt = 0
            self.accept()
        else:
            self._attempt += 1            
        if self._attempt >= 3: # Deal with attempting try fail logins
            QMessageBox.critical(self, "Authorization locked", "Too many fail login attempts!!!")
            exit()
            QCoreApplication.quit()

    def _verified_login(self, id, pwd) -> False:
        # Data reading
        try:
            operator = ops.Operator(id, pwd)
        except ops.OperationError as e:
            err_msg = e.__str__()
            QMessageBox.warning(self, "Login error", err_msg)
        else:
            self._operator = operator
            return True

    def _cancel_pressed(self):
        exit()
        QCoreApplication.quit()

    def reject(self):
        pass

    def info_change(self): # Enable login function
        if self._id.text() == "" or self._pwd.text() == "":
            self._login_btn.setEnabled(False)
        else:
            self._login_btn.setEnabled(True)