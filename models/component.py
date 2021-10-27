import ormar
import pydantic

from db import BaseMeta


class Component(ormar.Model):

    class Meta(BaseMeta):
        tablename = 'component'

    id: int = ormar.Integer(primary_key=True, autoincrement=True)
    is_healthy = ormar.Boolean()
    name: str = ormar.Text(index=True, unique=True)
    description: str = ormar.Text()
    is_blacklisted: bool = ormar.Boolean(pydantic_only=True, default=False)
    is_autocreated: bool = ormar.Boolean(default=False)
    # products: List['Product']


Component.update_forward_refs()


