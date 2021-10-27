import ormar
import pydantic
import json

from db import BaseMeta
from .component import Component


class User(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'user'

    id: int = ormar.Integer(primary_key=True, autoincrement=True)

    is_authenticated: bool = False
    blacklist: pydantic.Json = ormar.JSON(default=[])

    async def add_component_to_blacklist(self, component: Component):
        current_blacklist: list = self.blacklist
        if component.id in current_blacklist:
            return
        else:
            current_blacklist.append(component.id)
        self.blacklist = json.dumps(current_blacklist)
        await self.upsert()

    async def remove_component_from_blacklist(self, component: Component):
        current_blacklist: list = self.blacklist
        if component.id not in current_blacklist:
            return
        else:
            current_blacklist.remove(component.id)
        self.blacklist = json.dumps(current_blacklist)
        await self.upsert()


User.update_forward_refs()
