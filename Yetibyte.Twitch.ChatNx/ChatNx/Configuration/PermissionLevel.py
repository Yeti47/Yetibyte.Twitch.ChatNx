from enum import Enum

class PermissionLevel(Enum):
    ANY = "ANY"
    SUB = "SUB"
    MOD = "MOD"
    OWN = "OWN"

    def get_int_value(self)->int:

        int_val = 0

        if self.value == 'SUB':
            int_val = 1
        if self.value == 'MOD':
            int_val = 2
        if self.value == 'OWN':
            int_val = 3

        return int_val

