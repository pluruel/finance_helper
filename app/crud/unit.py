from app.crud.base import CRUDBase
from app.models import Unit
from app.schemas.payments import UnitCreate


class CRUDUnit(CRUDBase[Unit, UnitCreate, UnitCreate]):
    pass


crud_unit = CRUDUnit(Unit)
