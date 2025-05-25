from sqlalchemy import Column, Integer, String, Date, Enum as SQLEnum, LargeBinary, ARRAY
from sqlalchemy.orm import composite
from app.models.base import Base
from app.models.composites import AddressComposite
import enum

class Gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHERS = "OTHERS"

class Status(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    patient_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    phone_number = Column(String(15), nullable=False)
    gender = Column(SQLEnum(Gender), nullable=False)
    email = Column(String(100), nullable=False)
    status = Column(SQLEnum(Status), default=Status.ACTIVE)
    
    # Address composite columns
    street = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    postal_code = Column(String(10), nullable=False)
    
    # Composite property for address
    address = composite(
        AddressComposite,
        street,
        city,
        state,
        country,
        postal_code,
    )

    profile_image = Column(LargeBinary, nullable=True)
    medical_history = Column(ARRAY(String), nullable=True)
    date_of_birth = Column(Date, nullable=False)

    def __repr__(self):
        return f"Patient(id={self.id}, patient_id={self.patient_id}, name={self.name})"
