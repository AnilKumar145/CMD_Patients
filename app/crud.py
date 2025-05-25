from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models import Patient
from app.models.composites import AddressComposite
from app.schemas import PatientCreate, PatientResponse
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def create_patient(db: Session, patient: PatientCreate):
    try:
        # Get the last patient and extract the numeric part of the ID
        last_patient = db.query(Patient).order_by(Patient.id.desc()).first()
        if last_patient:
            last_id = int(last_patient.patient_id[3:])  # Extract number after 'PAT'
            next_id = last_id + 1
        else:
            next_id = 1
            
        patient_id = f"PAT{str(next_id).zfill(4)}"  # Format: PAT0001, PAT0002, etc.
        
        # Create AddressComposite instance
        address = AddressComposite(
            street=patient.address.street,
            city=patient.address.city,
            state=patient.address.state,
            country=patient.address.country,
            postal_code=patient.address.postal_code
        )

        # Create patient instance
        db_patient = Patient(
            patient_id=patient_id,
            name=patient.name,
            age=patient.age,
            phone_number=patient.phone_number,
            gender=patient.gender,
            email=patient.email,
            status=patient.status,
            date_of_birth=patient.date_of_birth,
            profile_image=patient.profile_image,
            medical_history=patient.medical_history,
            # Set address fields individually
            street=address.street,
            city=address.city,
            state=address.state,
            country=address.country,
            postal_code=address.postal_code
        )

        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        
        return db_patient
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Patient with this email already exists")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating patient: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def update_patient(db: Session, patient_id: str, patient: PatientCreate) -> Optional[Patient]:
    # Get the actual Patient model object directly from the database
    db_patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not db_patient:
        return None
    
    # Update address fields
    db_patient.street = patient.address.street
    db_patient.city = patient.address.city
    db_patient.state = patient.address.state
    db_patient.country = patient.address.country
    db_patient.postal_code = patient.address.postal_code
    
    # Update other fields
    db_patient.name = patient.name
    db_patient.age = patient.age
    db_patient.phone_number = patient.phone_number
    db_patient.gender = patient.gender
    db_patient.email = patient.email
    db_patient.status = patient.status
    db_patient.date_of_birth = patient.date_of_birth
    db_patient.profile_image = patient.profile_image
    db_patient.medical_history = patient.medical_history
    
    db.commit()
    db.refresh(db_patient)
    return db_patient

def get_patient_by_id(db: Session, patient_id: str) -> Optional[Dict]:
    try:
        patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if not patient:
            return None
            
        # Convert patient to dictionary and handle binary data
        patient_dict = {
            "id": patient.id,
            "patient_id": patient.patient_id,
            "name": patient.name,
            "age": patient.age,
            "phone_number": patient.phone_number,
            "gender": patient.gender,
            "email": patient.email,
            "address": {
                "street": patient.street,
                "city": patient.city,
                "state": patient.state,
                "country": patient.country,
                "postal_code": patient.postal_code
            },
            "status": patient.status,
            "date_of_birth": patient.date_of_birth,
            "medical_history": patient.medical_history,
            "profile_image": None if not patient.profile_image else "profile_image_available"
        }
        
        return patient_dict
    except Exception as e:
        logger.error(f"Error fetching patient by ID: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_patient_by_email(db: Session, email: str) -> Optional[Patient]:
    return db.query(Patient).filter(Patient.email == email).first()

def get_all_patients(db: Session) -> List[PatientResponse]:
    try:
        patients = db.query(Patient).all()
        patient_responses = []
        
        for patient in patients:
            # Create a dict of patient data
            patient_data = {
                "id": patient.id,
                "patient_id": patient.patient_id,
                "name": patient.name,
                "age": patient.age,
                "phone_number": patient.phone_number,
                "gender": patient.gender,
                "email": patient.email,
                "address": {
                    "street": patient.street,
                    "city": patient.city,
                    "state": patient.state,
                    "country": patient.country,
                    "postal_code": patient.postal_code
                },
                "status": patient.status,
                "date_of_birth": patient.date_of_birth,
                "medical_history": patient.medical_history,
                "profile_image": None if not patient.profile_image else "profile_image_available"
            }
            patient_responses.append(PatientResponse(**patient_data))
        
        return patient_responses
    except Exception as e:
        logger.error(f"Error fetching all patients: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def delete_patient(db: Session, patient_id: str) -> bool:
    patient = get_patient_by_id(db, patient_id)
    if patient:
        db.delete(patient)
        db.commit()
        return True
    return False

def partial_update_patient(db: Session, patient_id: str, updates: Dict[str, Any]) -> Optional[Patient]:
    db_patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not db_patient:
        return None
        
    # Handle address updates separately if present
    if 'address' in updates:
        address_data = updates.pop('address')
        for field, value in address_data.items():
            setattr(db_patient, field, value)
    
    # Update other fields
    for field, value in updates.items():
        if hasattr(db_patient, field):
            setattr(db_patient, field, value)
    
    try:
        db.commit()
        db.refresh(db_patient)
        return db_patient
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating patient: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def remove_patient_image(db: Session, patient_id: str) -> Optional[Patient]:
    """Remove the profile image of a patient"""
    db_patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not db_patient:
        return None
    
    try:
        db_patient.profile_image = None
        db.commit()
        db.refresh(db_patient)
        
        # Return in the same format as get_patient_by_id
        return {
            "id": db_patient.id,
            "patient_id": db_patient.patient_id,
            "name": db_patient.name,
            "age": db_patient.age,
            "phone_number": db_patient.phone_number,
            "gender": db_patient.gender,
            "email": db_patient.email,
            "address": {
                "street": db_patient.street,
                "city": db_patient.city,
                "state": db_patient.state,
                "country": db_patient.country,
                "postal_code": db_patient.postal_code
            },
            "status": db_patient.status,
            "date_of_birth": db_patient.date_of_birth,
            "medical_history": db_patient.medical_history,
            "profile_image": None
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error removing patient image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error removing patient image")

def add_patient_image(db: Session, patient_id: str, image_data: bytes) -> bool:
    """Add or update a patient's profile image"""
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        return False
    
    try:
        patient.profile_image = image_data
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding patient image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading image: {str(e)}"
        )

def update_patient_status(db: Session, patient_id: str, status: bool) -> Optional[Dict]:
    """Update the status of a patient (active/inactive)"""
    db_patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not db_patient:
        return None
    
    # Convert boolean to appropriate status enum value
    db_patient.status = "ACTIVE" if status else "INACTIVE"
    
    try:
        db.commit()
        
        # Return a dictionary with serializable data
        return {
            "id": db_patient.id,
            "patient_id": db_patient.patient_id,
            "name": db_patient.name,
            "age": db_patient.age,
            "phone_number": db_patient.phone_number,
            "gender": db_patient.gender,
            "email": db_patient.email,
            "address": {
                "street": db_patient.street,
                "city": db_patient.city,
                "state": db_patient.state,
                "country": db_patient.country,
                "postal_code": db_patient.postal_code
            },
            "status": db_patient.status,
            "date_of_birth": db_patient.date_of_birth,
            "medical_history": db_patient.medical_history,
            "profile_image": None if not db_patient.profile_image else "profile_image_available"
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating patient status: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating patient status")

def get_patient_image_data(db: Session, patient_id: str) -> Optional[bytes]:
    """Get patient's profile image data"""
    try:
        patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if not patient or not patient.profile_image:
            return None
        return patient.profile_image
    except Exception as e:
        logger.error(f"Error fetching patient image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching patient image")
