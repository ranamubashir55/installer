from fastapi import status, Depends, APIRouter, HTTPException, Body
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
def add_question(question_text: str= Body(..., embed=True), db: Session = Depends(get_db) , is_auhtenticate = Depends(authenticate)):
    try:
        record = crud.insert(db, table_name = "Question", data = {"question_text": question_text})
        log.info('New question created successfully')
        return {"msg": "New question created successfully"}
    except IntegrityError as e:
        log.error(f"Create: IntegrityError: {e.orig}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"question already exits!")


@router.post("/option", status_code=status.HTTP_201_CREATED)
def add_question_option(option: schemas.OptionCreate, db: Session = Depends(get_db) , is_auhtenticate = Depends(authenticate)):
    record = crud.get_record_by_param(db, table_name="Question", param_name="id", param_value=option.question_id)
    if not record: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"question_id is invalid!")
    try:
        record = crud.insert(db, table_name = "Option", data = option.dict())
        log.info('New option added successfully')
        return {"msg": "New option added successfully"}
    except IntegrityError as e:
        log.error(f"Create: IntegrityError: {e.orig}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"option already exits!")


@router.get("", status_code=status.HTTP_200_OK)
def get_questions(db: Session = Depends(get_db) , is_auhtenticate = Depends(authenticate)):
    records = crud.get_all_records(db, table_name="Question")
    for x in records:
        x.options
    return records


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_question(id:int, db: Session = Depends(get_db), is_auhtenticate = Depends(authenticate)):
    record = crud.delete_record(db, table_name="Question", param_name="id", param_value=id)
    if record:
        log.info(f'Question deleted successfully with id {id}')
        return {"msg": f'Question deleted successfully with id {id}'}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid question id supplied!")


@router.get("/suited/package", status_code=status.HTTP_200_OK)
def suited_package(is_auhtenticate = Depends(authenticate)):
    package = ['Inventory Trackor','Object Tracking', 'Zoning', 'WTIL','Productivity Trackor']
    return {"package":package}