from fastapi import status, Depends, APIRouter, HTTPException, Body
from schemas import pydantic_models as schemas
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db import crud
from utils.auth import authenticate
from db.database import get_db
import logging

log = logging.getLogger("omniroom-logger")

router = APIRouter()


@router.post("/category", status_code=status.HTTP_201_CREATED)
def add_service_category(
    category_name: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    is_auhtenticate=Depends(authenticate),
):
    try:
        record = crud.insert(
            db, table_name="ServiceCategory", data={"category_name": category_name}
        )
        log.info("New service category created successfully")
        return {
            "msg": "New service category created successfully",
            "category_id": record.id,
        }
    except IntegrityError as e:
        log.error(f"Create: IntegrityError: {e.orig}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"service category already exits!",
        )


@router.post("", status_code=status.HTTP_201_CREATED)
def add_digital_service(
    service: schemas.ServiceCreate,
    db: Session = Depends(get_db),
    is_auhtenticate=Depends(authenticate),
):
    record = crud.get_record_by_param(
        db,
        table_name="ServiceCategory",
        param_name="id",
        param_value=service.service_category_id,
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"invalid service category id supplied!",
        )
    try:
        record = crud.insert(db, table_name="Services", data=service.dict())
        log.info("New service created successfully")
        return {"msg": "New service created successfully"}
    except IntegrityError as e:
        log.error(f"Create: IntegrityError: {e.orig}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"service name already exits!",
        )


@router.get("/category", status_code=status.HTTP_200_OK)
def get_all_services_category(
    db: Session = Depends(get_db), is_auhtenticate=Depends(authenticate)
):
    records = crud.get_all_records(db, table_name="ServiceCategory")
    for x in records:
        x.digital_services
    return records


@router.get("", status_code=status.HTTP_200_OK)
def get_services(db: Session = Depends(get_db), is_auhtenticate=Depends(authenticate)):
    records = crud.get_all_records(db, table_name="Services")
    return records


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_category_and_associated_services(
    id: int, db: Session = Depends(get_db), is_auhtenticate=Depends(authenticate)
):
    record = crud.delete_record(
        db, table_name="ServiceCategory", param_name="id", param_value=id
    )
    if record:
        log.info(f"Service category deleted successfully with id {id}")
        return {"msg": f"Service category deleted successfully with id {id}"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Service category id supplied!",
        )
