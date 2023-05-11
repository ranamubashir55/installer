from sqlalchemy.orm import Session
from . import models


def insert(db: Session, table_name: str, data: dict):
    model = getattr(models, table_name)
    record = model(
        **data
    )  # **user_data is used to unpack the user_data dictionary and pass its contents as keyword arguments to the constructor of the User model
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_record_by_param(
    db: Session, table_name: str, param_name: str, param_value: str
):
    model = getattr(models, table_name)
    param = getattr(model, param_name)
    return db.query(model).filter(param == param_value).first()


def get_all_records(db: Session, table_name: str):
    model = getattr(models, table_name)
    return db.query(model).all()


def delete_record(db: Session, table_name: str, param_name: str, param_value: str):
    model = getattr(models, table_name)
    param = getattr(model, param_name)
    records = db.query(model).filter(param == param_value)
    if records.count() > 0:
        records.delete()
        db.commit()
        return True
    else:
        return False


def update_record(
    db: Session, table_name: str, param_name: str, param_value: str, data: dict
):
    model = getattr(models, table_name)
    param = getattr(model, param_name)
    db_user = db.query(model).filter(param == param_value).update(data)
    db.commit()
    return db_user


def get_user_by_email(db: Session, email):
    return db.query(models.User).filter(models.User.email == email).first()


def set_password_change_token(db: Session, email, token):
    db.query(models.User).filter(models.User.email == email).update(
        {models.User.password_change_token: token}
    )
    db.commit()


def change_password(db: Session, email, password):
    db.query(models.User).filter(models.User.email == email).update(
        {models.User.password: password}
    )
    db.commit()
