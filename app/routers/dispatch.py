from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.domain.dispatch import schemas, service
from app.domain.user.service import get_current_user
from database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Dispatch)
def create_dispatch(
    dispatch: schemas.DispatchCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    if current_user.role != "Cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to create dispatch"
        )
    return service.create_dispatch(db, dispatch, current_user.id)

@router.get("/{dispatch_id}", response_model=schemas.Dispatch)
def get_dispatch(dispatch_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    dispatch = service.get_dispatch(db, dispatch_id)
    if not dispatch or dispatch.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispatch not found")
    return dispatch

@router.put("/{dispatch_id}", response_model=schemas.Dispatch)
def update_dispatch(dispatch_id: int, dispatch: schemas.DispatchCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    existing_dispatch = service.get_dispatch(db, dispatch_id)
    if not existing_dispatch or existing_dispatch.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispatch not found")
    return service.update_dispatch(db, dispatch_id, dispatch)

@router.delete("/{dispatch_id}", response_model=schemas.Dispatch)
def delete_dispatch(dispatch_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    existing_dispatch = service.get_dispatch(db, dispatch_id)
    if not existing_dispatch or existing_dispatch.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispatch not found")
    return service.delete_dispatch(db, dispatch_id)

@router.get("/", response_model=list[schemas.Dispatch])
def list_dispatches(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.list_dispatches(db, current_user.id, skip=skip, limit=limit)
