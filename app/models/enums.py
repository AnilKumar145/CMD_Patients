from enum import Enum

class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class Status(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
