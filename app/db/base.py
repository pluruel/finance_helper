# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa

from app.models.file import (  # noqa
    File,
    Product,
    WorkspaceDB,
    Version,
    DataOrigin,
    ProductType,
)
from app.models.user import User, UserGroup, user_group_users  # noqa

# from app.models.item import Item
# from app.models.user2 import User
