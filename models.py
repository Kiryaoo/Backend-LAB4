from pydantic import BaseModel, Field, field_validator
from pydantic import ConfigDict
from decimal import Decimal
from datetime import datetime

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

class CategoryBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=50)
    model_config = ConfigDict(from_attributes=True)

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

class RecordBase(BaseModel):
    user_id: int = Field(..., ge=1)
    category_id: int = Field(..., ge=1)
    amount: float = Field(..., gt=0)
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

    @field_validator("timestamp")
    @classmethod
    def validate_date(cls, value: datetime) -> datetime:
        if value > datetime.now():
            raise ValueError("Timestamp cannot be in the future")
        return value

class RecordCreate(RecordBase):
    pass

class Record(RecordBase):
    id: int


class AccountBase(BaseModel):
    user_id: int
    model_config = ConfigDict(from_attributes=True)

class Account(AccountBase):
    id: int
    balance: Decimal

class AccountDeposit(BaseModel):
    amount: Decimal = Field(..., gt=0)