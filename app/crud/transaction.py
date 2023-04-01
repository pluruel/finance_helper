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
from app.schemas.payments import TransactionCreate


class CRUDTransaction(CRUDBase[Transaction, TransactionCreate, TransactionCreate]):
    def create(self, db: Session, *, obj_in: TransactionCreate) -> Transaction:
        # Extract data from obj_in
        payment_method_data = obj_in.payment_method
        item_data = obj_in.item

        # Retrieve or create the related objects using get_~ methods
        payment_method = PaymentMethod.get_category(
            db=db, name=payment_method_data["name"], family=obj_in.family
        )
        transaction_target = TransactionTarget.get_category(
            db=db, name=item_data["transaction_target"]
        )
        category = Category.get_category(db=db, name=item_data["category"])
        unit = Unit.get_category(db=db, name=item_data["unit"])

        item_dict = {
            "name": item_data["name"],
            "transaction_target_id": transaction_target.id,
            "category_id": category.id,
            "unit_id": unit.id,
        }
        item = Item.get_item(db=db, item_dict=item_dict)

        # Create the price
        price_dict = {
            "value": item_data["price"]["value"],
            "date": item_data["price"]["date"] or obj_in.date,
        }
        price = Price.get_price(db=db, price_dict=price_dict)

        # Associate the price with the item
        item.prices.append(price)
        db.add(price)

        # Create the transaction
        transaction = Transaction(
            payment_method_id=payment_method.id, item_id=item.id, date=obj_in.date
        )
        db.add(transaction)

        try:
            db.commit()
            db.refresh(transaction)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail="An error occurred while creating the transaction",
            )

        return transaction


transaction = CRUDTransaction(Transaction)
