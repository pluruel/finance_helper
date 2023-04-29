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

from app.db.base_class import Base
from app.utils.case import parse_date


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
    family = relationship("Family", back_populates="payment_methods")

    __table_args__ = (
        UniqueConstraint("name", "family_id", name="payment_mtd_name_family_id"),
    )

    @staticmethod
    def get_payment_method(db: Session, name: str, family: str):
        payment_method = (
            db.query(PaymentMethod)
            .join(Family)
            .filter(and_(PaymentMethod.name == name, Family.name == family))
        )

        if payment_method.count() > 0:
            return payment_method.first()
        else:
            f = db.query(Family).filter(Family.name == family).first()
            item = PaymentMethod(name=name, family=f)
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

    items = relationship("Item", back_populates="unit")

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

    item = relationship("Item", back_populates="prices")

    __table_args__ = (UniqueConstraint("date", "value", name="price_date_cost"),)

    @staticmethod
    def get_price(db: Session, value: float, date_str: str):
        price_date = parse_date(date_str)
        prices = db.query(Price).filter(
            and_(
                Price.value == value,
                Price.date == price_date,
            )
        )

        if prices.count() > 0:
            return prices.first()
        else:
            price = Price(value=value, date=price_date)
            db.add(price)
            db.flush()
            return price


class TransactionItemAssociation(Base):
    __tablename__ = "transaction_item_association"
    transaction_id = Column(Integer, ForeignKey("transaction.id"), primary_key=True)
    item_id = Column(Integer, ForeignKey("item.id"), primary_key=True)


class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    quantity = Column(Float)

    category_id = Column(Integer, ForeignKey("category.id"), index=True)
    unit_id = Column(Integer, ForeignKey("unit.id"), index=True)

    prices = relationship("Price", back_populates="item")
    category = relationship("Category", back_populates="items")
    unit = relationship("Unit", back_populates="items")
    transaction_targets = relationship(
        "TransactionTarget", secondary="transaction_target_item", back_populates="items"
    )
    transactions = relationship(
        "Transaction", secondary="transaction_item_association", back_populates="items"
    )

    @staticmethod
    def get_item(db: Session, item_dict: dict):
        item = db.query(Item).filter(Item.name == item_dict["name"]).first()

        if item is not None:
            return item

        item = Item(**item_dict)
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
    def get_transaction_target(db: Session, transaction_target: str):
        transaction_target_quary = db.query(TransactionTarget).filter(
            TransactionTarget.name == transaction_target
        )

        if transaction_target_quary.count():
            return transaction_target_quary.first()
        else:
            transaction_target = TransactionTarget(name=transaction_target)
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

    date = Column(Date, default=datetime.now)

    payment_method = relationship("PaymentMethod", back_populates="transactions")
    items = relationship(
        "Item", secondary="transaction_item_association", back_populates="transactions"
    )
