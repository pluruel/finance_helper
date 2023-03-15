from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    CHAR,
    Boolean,
    DOUBLE,
    Date,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Session

from app.db.base_class import Base


class Family(Base):
    __tablename__ = "family"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(16), index=True, unique=True)

    payment_methods = relationship("PaymentMethods", back_populates="family")


class PaymentMethod(Base):
    __tablename__ = "payment_method"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(16), index=True, unique=True)

    deduction_rate = Column(DOUBLE)

    family_id = Column(Integer, ForeignKey("family.id"))


class SpendCategory(Base):
    __tablename__ = "spend_category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)


class Unit(Base):
    __tablename__ = "unit"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)

    ratio_with_standard = Column(DOUBLE, default=1.0)


class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Integer, unique=True, index=True)

    price = Column(Integer, unique=True, index=True)
    account_id = Column(Integer, ForeignKey("account.id"))


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Integer, unique=True, index=True)


class Transaction(Base):
    id = Column(Integer, primary_key=True, index=True)

    family_id = Column(Integer, ForeignKey("family.id"))
    payment_method_id = Column(Integer, ForeignKey("family.id"))
    item_id = Column(Integer, ForeignKey("item.id"))
    spend_category_id = Column(Integer, ForeignKey("spend_category.id"))

    date = Column(Date, default=datetime.now)


class ProductType(Base):
    __tablename__ = "product_type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(16), index=True, unique=True)

    products = relationship("Product", back_populates="product_type")

    def get_product_type(db: Session, product_type_dict: dict):
        product_type = db.query(ProductType).filter(
            ProductType.name == product_type_dict["name"]
        )

        if product_type.count() > 0:
            return product_type.first()
        else:
            new_product_type = ProductType(**product_type_dict)
            db.add(new_product_type)
            db.commit()
            db.refresh(new_product_type)
            return new_product_type


class File(Base):
    id = Column(Integer, primary_key=True, index=True)

    host = Column(String)
    filepath = Column(String)
    sha1 = Column(CHAR(40), index=True, nullable=True)

    creator_id = Column(Integer, ForeignKey("user.id"))
    creator = relationship("User", back_populates="files")

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    product = relationship("Product", back_populates="file")
    workspace_db = relationship("WorkspaceDB", back_populates="file")

    __table_args__ = (UniqueConstraint("host", "filepath", name="_host_filepath"),)
