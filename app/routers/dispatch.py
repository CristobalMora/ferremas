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
