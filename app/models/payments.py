from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Date,
    Float,
    UniqueConstraint,
    and_,
)
from sqlalchemy.orm import relationship, Session

from app import schemas
from app.db.base_class import Base


class Family(Base):
    __tablename__ = "family"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(16), index=True, unique=True)

    payment_methods = relationship("PaymentMethod", back_populates="family")


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    family_id = Column(Integer, ForeignKey("family.id"), index=True)

    balance = Column(Integer)


class PaymentMethod(Base):
    __tablename__ = "payment_method"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    tax_deduction_rate = Column(Float)

    family_id = Column(Integer, ForeignKey("family.id"), index=True)

    transactions = relationship("Transaction", back_populates="payment_method")

    __table_args__ = (
        UniqueConstraint("name", "family_id", name="payment_mtd_name_family_id"),
    )

    @staticmethod
    def get_payment_method(db: Session, name: str, family: Family):
        payment_method = db.query(PaymentMethod).filter(
            and_(PaymentMethod.name == name, PaymentMethod.family_id == family.id)
        )

        if payment_method.count() > 0:
            return payment_method.first()
        else:
            item = PaymentMethod(name=name, family_id=family.id)
            db.add(item)
            db.flush()
            return item


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)

    items = relationship("Item", back_populates="category")

    @staticmethod
    def get_category(db: Session, name: str):
        category_q = db.query(Category).filter(Category.name == name)

        if category_q.count() > 0:
            return category_q.first()
        else:
            item = Category(name=name)
            db.add(item)
            db.flush()
            return item


class Unit(Base):
    __tablename__ = "unit"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)

    ratio = Column(Float, default=1.0)

    @staticmethod
    def get_unit(db: Session, name: str):
        unit_q = db.query(Unit).filter(Unit.name == name)

        if unit_q.count() > 0:
            return unit_q.first()
        else:
            raise HTTPException(status_code=404, detail="There is no proper unit.")


class Price(Base):
    __tablename__ = "price"
    id = Column(Integer, primary_key=True, index=True)

    item_id = Column(Integer, ForeignKey("item.id"), index=True)

    value = Column(Float)
    date = Column(Date, default=datetime.now)

    __table_args__ = (UniqueConstraint("date", "value", name="price_date_cost"),)

    @staticmethod
    def get_price(db: Session, value: float, date: date):
        prices = db.query(Price).filter(
            and_(
                Price.value == value,
                Price.date == date,
            )
        )

        if prices.count() > 0:
            return prices.first()
        else:
            price = Price()
            db.add(price)
            db.flush()
            return price


class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    quantity = Column(Float)

    category_id = Column(Integer, ForeignKey("category.id"), index=True)
    unit_id = Column(Integer, ForeignKey("unit.id"), index=True)

    prices = relationship("Price", back_populates="item")
    transaction_targets = relationship(
        "TransactionTarget", secondary="transaction_target_item", back_populates="items"
    )

    @staticmethod
    def get_item(db: Session, item: schemas.ItemCreate):
        item = db.query(Item).filter(Item.name == item.name).first()

        if item is not None:
            return item

        item = Item(**item)
        transaction_target = db.query(TransactionTarget).get(item.transaction_target_id)
        item.transaction_targets.append(transaction_target)
        db.add(item)
        db.flush()
        return item


class TransactionTarget(Base):
    __tablename__ = "transaction_target"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    items = relationship(
        "Item",
        secondary="transaction_target_item",
        back_populates="transaction_targets",
    )

    @staticmethod
    def get_transaction_target(
        db: Session, transaction_target: schemas.TransactionTargetBase
    ):
        transaction_target = (
            db.query(TransactionTarget)
            .filter(TransactionTarget.name == transaction_target.name)
            .first()
        )

        if transaction_target:
            return transaction_target
        else:
            transaction_target = TransactionTarget(**transaction_target)
            db.add(transaction_target)
            db.flush()
            return transaction_target


class TransactionTargetItem(Base):
    __tablename__ = "transaction_target_item"
    transaction_target_id = Column(
        Integer, ForeignKey("transaction_target.id"), primary_key=True
    )
    item_id = Column(Integer, ForeignKey("item.id"), primary_key=True)


class Transaction(Base):
    __tablename__ = "transaction"
    id = Column(Integer, primary_key=True, index=True)

    payment_method_id = Column(Integer, ForeignKey("payment_method.id"))
    item_id = Column(Integer, ForeignKey("item.id"))

    date = Column(Date, default=datetime.now)

    payment_method = relationship("PaymentMethod", back_populates="transactions")
    item = relationship("Item")
