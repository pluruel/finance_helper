from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class FamilyBase(BaseModel):
    name: str


class FamilyCreate(FamilyBase):
    pass


class Family(FamilyBase):
    id: int

    class Config:
        orm_mode = True


class AccountBase(BaseModel):
    name: str


class AccountCreate(AccountBase):
    family_id: int


class Account(AccountBase):
    id: int
    balance: int

    class Config:
        orm_mode = True


class PaymentMethodBase(BaseModel):
    name: str
    tax_deduction_rate: float


class PaymentMethodCreate(PaymentMethodBase):
    family_id: int


class PaymentMethod(PaymentMethodBase):
    id: int

    class Config:
        orm_mode = True


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int

    class Config:
        orm_mode = True


class UnitBase(BaseModel):
    name: str
    ratio: float


class UnitCreate(UnitBase):
    pass


class Unit(UnitBase):
    id: int

    class Config:
        orm_mode = True


class PriceBase(BaseModel):
    date: Optional[str]


class PriceCreate(BaseModel):
    value: float
    date: datetime.date


class Price(PriceBase):
    id: int

    class Config:
        orm_mode = True


class ItemBase(BaseModel):
    name: str


class ItemCreate(ItemBase):
    transaction_target_id: int
    category_id: int
    unit_id: int
    quantity: float


class Item(ItemBase):
    id: int
    prices: List[Price]

    class Config:
        orm_mode = True


class TransactionTargetBase(BaseModel):
    name: str


class TransactionTargetCreate(TransactionTargetBase):
    pass


class TransactionTarget(TransactionTargetBase):
    id: int
    items: List[Item]

    class Config:
        orm_mode = True


class TransactionBase(BaseModel):
    date: Optional[str]


class TransactionCreate(TransactionBase):
    payment_method_id: int
    item_id: int


class Transaction(TransactionBase):
    id: int

    class Config:
        orm_mode = True