import traceback

from fastapi import HTTPException
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


transaction = CRUDTransaction(Transaction)
