import fastapi
import ormar

import redis
import json
from typing import List

from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse

from models import Product, Component, User
from services import get_product_by_barcode


router = APIRouter()


@router.get('/product/{barcode}/', response_model=Product.get_pydantic(exclude={'DECIMAL_PARAMS'}))
async def get_product(request: Request, barcode: str):
    user: User = request.scope.get('authenticated_user')
    product: Product = await get_product_by_barcode(barcode)
    healthy_count = 0
    for comp in product.components:
        comp.is_blacklisted = comp.id in user.blacklist
        if comp.is_healthy:
            healthy_count += 1
    if product.components:
        product.healthy_components_percentage = str(round(healthy_count / len(product.components) * 100, 2))
    else:
        product.healthy_components_percentage = str('100.00')
    return product


@router.get('/blacklist', response_model=List[Component.get_pydantic(include={'id', 'name'})])
async def user_blacklist(request: Request):
    user: User = request.scope.get('authenticated_user')
    blacklist = user.blacklist
    components = []
    for component_id in blacklist:
        component = await Component.objects.get(id=component_id)
        components.append(component)
    return components


component_input = Component.get_pydantic(include={'name'})


@router.post('/blacklist/')
async def add_to_blacklist(request: Request, component_data: component_input):
    user: User = request.scope.get('authenticated_user')
    try:
        component = await Component.objects.get(name=component_data.name)
    except ormar.NoMatch:
        component = await Component.objects.create(
            name=component_data.name.lower(),
            is_autocreated=True,
            is_healthy=False,
            description=''
        )
    await user.add_component_to_blacklist(component)
    return JSONResponse({'ok': True})


@router.delete('/blacklist/{component_id}')
async def remove_from_blacklist(request: Request, component_id: int):
    user: User = request.scope.get('authenticated_user')
    component = await Component.objects.get(id=component_id)
    await user.remove_component_from_blacklist(component)
    return JSONResponse({'ok': True})
