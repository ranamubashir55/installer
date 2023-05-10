from sqlalchemy.orm import Session
from . import models
from utils.auth import get_password_hash


def create_user(db: Session, user=None):
    db_user = models.User(**user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id, user_data):
    db_user = db.query(models.User).filter(models.User.id == user_id).update(user_data)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db.delete(db_user)
    db.commit()


def get_user_by_email(db: Session, email):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id):
    return db.query(models.User).filter(models.User.id == user_id).first()


def set_password_change_token(db: Session, email, token):
    db.query(models.User).filter(models.User.email == email).update({models.User.password_change_token: token})
    db.commit()


def change_password(db: Session, email, password):
    db.query(models.User).filter(models.User.email == email).update({models.User.password: password})
    db.commit()

