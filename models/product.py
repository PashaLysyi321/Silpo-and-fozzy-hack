import ormar
from typing import List
import random
from pydantic import validator
from decimal import Decimal

from db import BaseMeta
from .component import Component


def get_rand_price() -> float:
    return round(random.uniform(10.0, 35.0), 2)


DEFAULT_PHOTO_URL = 'https://e7.pngegg.com/pngimages/140/347/png-clipart-grocery-store-shopping-list-food-icon-a-bag-of-food-text-hand.png'

component_relation_serializer = Component.get_pydantic(exclude={'is_autocreated'})


class Product(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'product'

    barcode: str = ormar.String(max_length=15, primary_key=True)
    name: str = ormar.Text()

    proteins: str = ormar.Float()
    fats: str = ormar.Float()
    carbohydrates: str = ormar.Float()
    calories: str = ormar.Float()

    mass: str = ormar.Float()
    price: str = ormar.Float(default=get_rand_price)

    package: str = ormar.Text()
    utilize: str = ormar.Text()

    is_gmo: bool = ormar.Boolean()
    is_organic: bool = ormar.Boolean()

    is_vegetarian: bool = ormar.Boolean()
    is_vegan: bool = ormar.Boolean()
    image_url: str = ormar.Text(default=DEFAULT_PHOTO_URL)

    components: List[component_relation_serializer] = ormar.ManyToMany(Component)

    healthy_components_percentage: str = ormar.String(pydantic_only=True, default="0.0", max_length=6)

    @validator('proteins', 'fats', 'carbohydrates', 'calories', 'mass', 'price')
    def convert_to_string(cls, v):
        return str(v)


Product.update_forward_refs()
