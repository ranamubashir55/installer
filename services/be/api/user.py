import re
from fastapi import status, Depends, APIRouter, HTTPException
from fastapi import UploadFile, File
from schemas import pydantic_models as schemas
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db import crud
from utils.auth import authenticate, get_password_hash, verify_password
from db.database import get_db
import logging, shutil

log = logging.getLogger('omniroom-logger')

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        user_data = user.dict()
        user_data['password']=get_password_hash(user_data['password'])
        crud.insert(db, table_name="User", data=user_data)
        log.info('New user created successfully')
        return {"msg": "New user created successfully"}
    except IntegrityError as e:
        log.error(f"Create: IntegrityError: {e.orig}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"email or company or mobile already exits!")


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_one_user(id: int, db: Session = Depends(get_db), is_authenticate=Depends(authenticate)):
    db_user = crud.get_user_by_id(db, id)
    if db_user:
        return db_user
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error: Invalid id supplied...")


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_user(id: int, user: schemas.UserCreate, db: Session = Depends(get_db), is_authenticate=Depends(authenticate)):
    db_user = crud.get_user_by_id(db, id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error: Invalid id supplied...")
    try:
        user_data = user.dict()
        if verify_password(user_data['password'], db_user.password):
            user_data['password'] = get_password_hash(user_data['password'])
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Your current password is inavlid..")
        db_user = crud.update_user(db, id, user_data)
        log.info('User updated successfully')
        return {"msg": "User updated successfully"}
    except IntegrityError as e:
        log.error(f"Update: IntegrityError: {e.orig}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"email or company or mobile already exits!")


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_user(id:int, db: Session = Depends(get_db), is_authenticate=Depends(authenticate)):
    db_user = crud.get_user_by_id(db, id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error: Invalid id supplied...")
    crud.delete_user(db, id)
    return {"msg":"User deleted successfully.."}


@router.post("/floorplan", status_code=status.HTTP_201_CREATED)
def upload_floorplan(file: UploadFile = File(...), is_authenticate=Depends(authenticate)):
    file_path = 'uploads/'+file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    log.info("File uploaded successfully..")
    return {"msg":"file uploaded successfully.", "file_path":file.filename}