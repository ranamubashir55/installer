from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(length=60), nullable=False)
    email = Column(String(length=50), unique=True, nullable=False, index=True)
    mobile = Column(String(length=15), unique=True, nullable=False)
    company = Column(String(length=50), unique=True)
    facility = Column(String(length=50), nullable=False)
    password = Column(String(length=100), nullable=False)
    account_type = Column(String(length=50), default="individual")
    password_change_token = Column(String, default=None)


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question_text = Column(String, unique=True, nullable=False)
    options = relationship('Option', cascade='all, delete', backref='question')

class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'))
    option_text = Column(String, unique=True, nullable=False)