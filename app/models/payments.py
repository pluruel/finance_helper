from datetime import datetime

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
            db.commit()
            db.refresh(item)
            return item


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)

    items = relationship("Item", back_populates="category")


class Unit(Base):
    __tablename__ = "unit"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)

    ratio = Column(Float, default=1.0)


class Price(Base):
    __tablename__ = "price"
    id = Column(Integer, primary_key=True, index=True)

    item_id = Column(Integer, ForeignKey("item.id"), index=True)

    value = Column(Float)
    date = Column(Date, default=datetime.now)

    __table_args__ = (UniqueConstraint("date", "value", name="price_date_cost"),)

    @staticmethod
    def get_price(db: Session, price_dict: dict):
        prices = db.query(Price).filter(
            and_(
                Price.value == price_dict["value"],
                Price.date == price_dict["date"],
            )
        )

        if prices.count() > 0:
            return prices.first()
        else:
            price = Price(**price_dict)
            db.add(price)
            db.commit
            db.refresh(price)
            return price


class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(Float)

    transaction_target_id = Column(
        Integer, ForeignKey("transaction_target.id"), index=True
    )
    category_id = Column(Integer, ForeignKey("category.id"), index=True)
    unit_id = Column(Integer, ForeignKey("unit.id"), index=True)

    prices = relationship("Price", back_populates="item")

    __table_args__ = (
        UniqueConstraint(
            "name", "transaction_target_id", name="item_name_transaction_target_id"
        ),
    )

    @staticmethod
    def get_item(db: Session, item_dict: dict):
        items = db.query(Item).filter(
            and_(
                Item.name == item_dict["name"],
                Item.transaction_target_id == item_dict["transaction_target_id"],
            )
        )

        if items.count() > 0:
            return items.first()
        else:
            item = Item(**item_dict)
            db.add(item)
            db.commit
            db.refresh(item)
            return item


class TransactionTarget(Base):
    tablename = "transaction_target"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    items = relationship("Item", back_populates="transaction_target")


class Transaction(Base):
    tablename = "transaction"
    id = Column(Integer, primary_key=True, index=True)

    payment_method_id = Column(Integer, ForeignKey("payment_method.id"))
    item_id = Column(Integer, ForeignKey("item.id"))

    date = Column(Date, default=datetime.now)

    payment_method = relationship("PaymentMethod", back_populates="transactions")
    item = relationship("Item")
