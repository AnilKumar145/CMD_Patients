from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date
from enum import Enum
import base64

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHERS = "OTHERS"

class Status(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class Address(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str
    country: str

    class Config:
        from_attributes = True

class PatientBase(BaseModel):
    name: str
    age: int
    phone_number: str
    gender: Gender
    email: EmailStr
    address: Address
    status: Status = Status.ACTIVE
    date_of_birth: date
    profile_image: Optional[bytes] = None
    medical_history: Optional[List[str]] = []

    class Config:
        json_encoders = {
            date: lambda v: v.strftime("%d/%m/%Y")
        }

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int
    patient_id: str
    profile_image: Optional[str] = None  # Change bytes to str for serialization

    class Config:
        from_attributes = True

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    phone_number: Optional[str] = None
    gender: Optional[Gender] = None
    email: Optional[EmailStr] = None
    address: Optional[Address] = None
    status: Optional[Status] = None
    date_of_birth: Optional[date] = None
    profile_image: Optional[bytes] = None
    medical_history: Optional[List[str]] = None

    class Config:
        json_encoders = {
            date: lambda v: v.strftime("%d/%m/%Y")
        }
        
    @classmethod
    def from_orm(cls, obj):
        # Convert binary image to base64 if it exists
        if obj.profile_image:
            obj.profile_image = base64.b64encode(obj.profile_image).decode('utf-8')
        return super().from_orm(obj)
