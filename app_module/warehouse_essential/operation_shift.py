import pandas as pd
from datetime import datetime as dt
from os import makedirs

DEFAULT_OPERATION_PATH = ".\\Metadata\\OperationData"
try:
    makedirs(DEFAULT_OPERATION_PATH)
except FileExistsError:
    pass

class Operation():
    cnt = 0
    def __init__(self):
        if Operation.cnt > 0:
            raise OperationError("Only one Operation object is allowed at a time!!!")
        self._operator = None
        Operation.cnt += 1

    def operator_login(self, uid, pwd):
        if not self._operator == None:
            raise OperationError("Only one Operator is allowed at a time!!!")
        self._operator = Operator(uid, pwd)
        self._start_time = dt.now()

    def add_operator(self, operator):
        self._operator = operator

    def get_operator(self):
        return self._operator
    operator = property(get_operator)

    def operator_logout(self):
        if self._operator == None:
            raise OperationError("No operator detected! Invalid operation!!!")
        self._end_time = dt.now()
        # Recording the info of the operator working on the shift
        dic = {"employee id": self._operator._employee_id,
                                "name": [" ".join([self._operator._firstname, self._operator._lastname])],
                                "start": self._start_time.strftime("%Y-%m-%d %H:%M:%S"),
                                "end": self._end_time.strftime("%Y-%m-%d %H:%M:%S"),
                                "time eslapse": (self._end_time - self._start_time).seconds}
        try:
            df = pd.read_csv(DEFAULT_OPERATION_PATH + "\\operation_records.csv") # Try to verify if the file exists or not
        except FileNotFoundError:
            df = pd.DataFrame(dic)
            df.to_csv(DEFAULT_OPERATION_PATH + "\\operation_records.csv", header = True, index = False)
        else:
            pd.DataFrame(dic).to_csv(DEFAULT_OPERATION_PATH + "\\operation_records.csv", mode = 'a', header = False, index = False)

    def __del__(self):
        Operation.cnt -= 1
        # clear all the values
        self._operator = None
        try:
            del self._start_time, self._end_time
        except:
            pass
    
    def __add__(self, other):
        if isinstance(other, Operator) and self._operator == None:
            self._operator = other
            self._start_time = dt.now()
            
        return self

    def __str__(self) -> str:
        if self._operator is None:
            return ""
        return self._operator.__str__()

class Operator():
    def __init__(self, uid, pwd):
        employee_info = self.load_operator(uid, pwd)
        self._firstname = employee_info["fname"]
        self._lastname = employee_info["lname"]
        self._employee_id = employee_info["employee id"]
        self._position = employee_info["position"]

    position = property(fget = lambda self : self._position)

    def load_operator(self, uid, pwd, file_name = DEFAULT_OPERATION_PATH + "\\employee_data.csv"):
        try:
            employee_df = pd.read_csv(file_name, header = 0, index_col = "user id")
            if not pwd == employee_df.loc[uid]["password"]:
                raise OperationError("Unauthorized login attempt!!!")
        except KeyError:
            raise OperationError("Unauthorized login attempt!!!")
        except FileNotFoundError:
            raise OperationError("No employee data founded!!!")
        else:
            employee_df = employee_df.loc[uid][["employee id", "fname", "lname", "position"]].to_dict()
            return employee_df
        
    def __str__(self) -> str:
        msg = ""
        msg += f"Operator: {self._firstname} {self._lastname}\n"
        msg += f"Employee ID: {self._employee_id}\n"
        msg += f"Position: {self._position.upper()}\n"
        return msg
    
class OperationError(Exception):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"{super().__str__()}"
