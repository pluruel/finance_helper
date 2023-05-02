import traceback
from datetime import date, timedelta
from typing import List, Type

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import (
    Transaction,
    PaymentMethod,
    TransactionTarget,
    Category,
    Unit,
    Item,
    Price,
)
from app import schemas
from app.utils.case import parse_date


class CRUDTransaction(
    CRUDBase[Transaction, schemas.TransactionCreate, schemas.TransactionCreate]
):
    def create(self, db: Session, *, obj_in: schemas.TransactionCreate) -> Transaction:
        # Extract data from obj_in
        try:
            with db.begin_nested():
                payment_method_data = obj_in.payment_method
                items = obj_in.items

                # Retrieve or create the related objects using get_~ methods
                payment_method = PaymentMethod.get_payment_method(
                    db=db, name=payment_method_data.name, family=obj_in.family
                )
                transaction = Transaction(
                    payment_method_id=payment_method.id,
                    date=parse_date(obj_in.date),
                )
                for item in items:
                    transaction_target = TransactionTarget.get_transaction_target(
                        db=db, transaction_target=item.transaction_target
                    )
                    category = Category.get_category(db=db, name=item.category)
                    unit = Unit.get_unit(db=db, name=item.unit)
                    item_ori_dict = item.dict()
                    item_dict = {
                        "name": item_ori_dict["name"],
                        "category_id": category.id,
                        "unit_id": unit.id,
                    }
                    new_item = Item.get_item(db=db, item_dict=item_dict)

                    # Create the price
                    price = Price.get_price(
                        db=db, value=item.price, date_str=obj_in.date
                    )

                    # Associate the price with the item
                    new_item.prices.append(price)
                    transaction.items.append(new_item)
                    transaction_target.items.append(new_item)
                db.add(price)

                # Create the transaction

                db.add(transaction)
                db.commit()

        except Exception as e:
            db.rollback()
            traceback.print_exc()
            raise HTTPException(
                status_code=400,
                detail="An error occurred while creating the transaction",
            )

        db.refresh(transaction)
        return transaction

    def delete_all(self, db: Session):
        db.query(Transaction).all().delete(synchronize_session=False)

    def delete_month(self, db: Session, target: schemas.TransactionDelete) -> List[int]:
        start_date = date(target.year, target.month, 1)
        end_date = start_date + timedelta(days=32)
        end_date = end_date.replace(day=1)
        results = (
            db.query(Transaction)
            .with_entities(Transaction.id)
            .filter(and_(Transaction.date >= start_date, Transaction.date < end_date))
            .all()
        )
        results = [item[0] for item in results]

        db.query(Transaction).filter(
            and_(Transaction.date >= start_date, Transaction.date < end_date)
        ).delete(synchronize_session=False)
        db.commit()

        return results

    def retrive_month(
        self, db: Session, target: schemas.TransactionDelete
    ) -> list[schemas.Transaction]:
        start_date = date(target.year, target.month, 1)
        end_date = start_date + timedelta(days=32)
        end_date = end_date.replace(day=1)

        results = (
            db.query(Transaction)
            .filter(and_(Transaction.date >= start_date, Transaction.date < end_date))
            .all()
        )
        return results


transaction = CRUDTransaction(Transaction)
