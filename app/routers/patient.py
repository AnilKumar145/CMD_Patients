from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, List, Any
from app.database import get_db
from app.schemas import PatientCreate, PatientResponse, PatientUpdate
from app import crud
from app.auth_utils import get_admin_user, get_doctor_user, get_patient_user, get_staff_user, User

router = APIRouter(prefix="/api/patients", tags=["Patients"])

@router.get("/", response_model=List[PatientResponse])
async def get_all_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_staff_user)
):
    """Get all patients (Staff and Admin)"""
    return crud.get_all_patients(db)

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_staff_user)
):
    """Get patient by ID (Staff and Admin)"""
    patient = crud.get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def add_patient(
    patient: PatientCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_staff_user)
):
    """Create a new patient (Staff and Admin)"""
    return crud.create_patient(db, patient)

@router.put("/{patient_id}", response_model=PatientResponse)
async def edit_patient(
    patient_id: str, 
    patient: PatientCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_staff_user)
):
    """Update patient information (Staff and Admin)"""
    updated_patient = crud.update_patient(db, patient_id, patient)
    if not updated_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated_patient

@router.patch("/{patient_id}", response_model=PatientResponse)
async def partial_update_patient(
    patient_id: str, 
    updates: Dict[str, Any], 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_staff_user)
):
    """Partially update patient information (Staff and Admin)"""
    updated_patient = crud.partial_update_patient(db, patient_id, updates)
    if not updated_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated_patient

@router.put("/removeimage/{patient_id}", response_model=PatientResponse)
async def remove_image(
    patient_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_staff_user)
):
    """Remove patient's profile image (Staff and Admin)"""
    updated_patient = crud.remove_patient_image(db, patient_id)
    if not updated_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated_patient

@router.put("/addimage/{patient_id}", response_class=JSONResponse)
async def add_image(
    patient_id: str, 
    profile_image: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_staff_user)
) -> Dict[str, str]:
    """Add or update patient's profile image (Staff and Admin)"""
    if not profile_image.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File uploaded is not an image"
        )

    try:
        image_data = await profile_image.read()
        success = crud.add_patient_image(db, patient_id, image_data)
        
        if not success:
            raise HTTPException(status_code=404, detail="Patient not found")
            
        return {"status": "success", "message": "Image uploaded successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading image: {str(e)}"
        )

@router.get("/image/{patient_id}", response_class=Response)
async def get_patient_image(
    patient_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_staff_user)
):
    """Get patient's profile image (Staff and Admin)"""
    patient = crud.get_patient_image_data(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return Response(
        content=patient,
        media_type="image/png"
    )

@router.put("/activate/{patient_id}", response_model=PatientResponse)
async def activate_patient(
    patient_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Activate a patient (Admin only)"""
    updated_patient = crud.update_patient_status(db, patient_id, True)
    if not updated_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated_patient

@router.put("/inactivate/{patient_id}", response_model=PatientResponse)
async def inactivate_patient(
    patient_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Inactivate a patient (Admin only)"""
    updated_patient = crud.update_patient_status(db, patient_id, False)
    if not updated_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated_patient

@router.get("/me/", response_model=PatientResponse)
async def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_patient_user)
):
    """Get the current patient's own profile (Patient only)"""
    patient = crud.get_patient_by_username(db, current_user.username)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return patient
