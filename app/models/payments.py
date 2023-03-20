from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Double
from sqlalchemy.orm import relationship, Session

from app.db.base_class import Base


class Family(Base):
    __tablename__ = "family"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(16), index=True, unique=True)

    payment_methods = relationship("PaymentMethods", back_populates="family")


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    family_id = Column(Integer, ForeignKey("family.id"), index=True)

    balance = Column(Integer)


class PaymentMethod(Base):
    __tablename__ = "payment_method"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    tax_deduction_rate = Column(Double)

    family_id = Column(Integer, ForeignKey("family.id"), index=True)

    transactions = relationship("Transaction", back_populates="payment_method")


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)

    items = relationship("Items", back_populates="category")


class Unit(Base):
    __tablename__ = "unit"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)

    ratio = Column(Double, default=1.0)


class Price(Base):
    __tablename__ = "price"
    id = Column(Integer, primary_key=True, index=True)

    item_id = Column(Integer, ForeignKey("item.id"), index=True)

    date = Column(Date, default=datetime.now)


class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    transaction_target_id = Column(
        Integer, ForeignKey("transaction_target.id"), index=True
    )
    category_id = Column(Integer, ForeignKey("category.id"), index=True)
    unit_id = Column(Integer, ForeignKey("unit.id"), index=True)

    prices = relationship("Price", back_populates="item")


class TransactionTarget(Base):
    __tablename__ = "transaction_target"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    items = relationship("Items", back_populates="transaction_target")


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True, index=True)

    payment_method_id = Column(Integer, ForeignKey("payment_method.id"))
    item_id = Column(Integer, ForeignKey("item.id"))

    date = Column(Date, default=datetime.now)
