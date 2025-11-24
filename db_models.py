from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class UserORM(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    password = Column(String(128), nullable=False)

    records = relationship("RecordORM", back_populates="user", cascade="all, delete-orphan")
    account = relationship("AccountORM", back_populates="user", uselist=False, cascade="all, delete-orphan")


class CategoryORM(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)

    records = relationship("RecordORM", back_populates="category")

class RecordORM(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserORM", back_populates="records")
    category = relationship("CategoryORM", back_populates="records")


class AccountORM(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    balance = Column(Numeric(14, 2), nullable=False, default=0)

    user = relationship("UserORM", back_populates="account")
