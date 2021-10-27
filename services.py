import json

import ormar
from typing import Optional

import redis
from models import Product, Component
from ds_services import get_product_info, get_component_info_by_name


async def _create_or_update_component(component_name: str, component_id: Optional[int] = None):
    component_data: dict = get_component_info_by_name(component_name.lower())
    if component_id:
        component_data['id'] = component_data
        component_data['is_autocreated'] = False
    component = Component(**component_data)
    return component


async def _find_product_info_by_barcode(barcode: str) -> Product:
    # contains all product's fields and component's names as list of strings
    general_info: dict = get_product_info(barcode)
    components = general_info.pop('components')
    image_url = general_info.get('image_url')
    if image_url == '':
        general_info.pop('image_url')

    product = Product(**general_info)
    product = await product.save()
    for component_name in components:
        try:
            component = await Component.objects.get(name=component_name, is_autocreated=False)
            component = await _create_or_update_component(component.name, component.id)
            component = await component.save()
        except ormar.NoMatch:
            # contains all component's fields
            component = await _create_or_update_component(component_name)
            component = await component.save()
        await product.components.add(component)
    return product


async def get_product_by_barcode(barcode: str) -> Product:
    try:
        product: Product = await Product.objects.select_related('components').get(barcode=barcode)
    except ormar.NoMatch:
        # DS part
        product = await _find_product_info_by_barcode(barcode)
        await product.upsert()

    return product
