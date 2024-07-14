from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.domain.sucursal import schemas, models, service
from database import get_db
from app.dependencies import get_admin_user
from app.domain.user.models import User  # Corregir esta línea

router = APIRouter()

@router.post("/", response_model=schemas.Sucursal)
def create_sucursal(
    sucursal: schemas.SucursalCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_admin_user)
):
    return service.create_sucursal(db, sucursal, current_user)

@router.get("/{sucursal_id}", response_model=schemas.Sucursal)
def read_sucursal(
    sucursal_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_admin_user)
):
    db_sucursal = service.get_sucursal(db, sucursal_id)
    if db_sucursal is None:
        raise HTTPException(status_code=404, detail="Sucursal not found")
    return db_sucursal

@router.get("/", response_model=list[schemas.Sucursal])
def read_sucursales(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_admin_user)
):
    return service.get_sucursales(db)

@router.put("/{sucursal_id}", response_model=schemas.Sucursal)
def update_sucursal(
    sucursal_id: int, 
    sucursal: schemas.SucursalCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_admin_user)
):
    return service.update_sucursal(db, sucursal_id, sucursal, current_user)

@router.delete("/{sucursal_id}", response_model=schemas.Message)
def delete_sucursal(sucursal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    sucursal = db.query(models.Sucursal).filter(models.Sucursal.id == sucursal_id).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal not found")
    db.delete(sucursal)
    db.commit()
    return {"detail": "Sucursal deleted"}
