from enum import Enum

class Role(Enum):
    USER = "USER" # Can only view points
    SALES = "SALES" # Can only add points
    ADMIN = "ADMIN" # Can add and remove points