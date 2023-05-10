from fastapi import status, Depends, APIRouter, HTTPException
from schemas import pydantic_models as schemas
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db import crud
from utils.auth import authenticate
from db.database import get_db
import logging

log = logging.getLogger('omniroom-logger')

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        crud.create_user(db=db, user=user.dict())
        log.info('New user created successfully')
        return {"msg": "New user created successfully"}
    except IntegrityError as e:
        log.error(f"IntegrityError: {e.orig}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"email or company already exits!")


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_one_user(id: int, db: Session = Depends(get_db), is_authenticate=Depends(authenticate)):
    db_user = crud.get_user_by_id(db, id)
    if db_user:
        return db_user
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error: Invalid id supplied...")
