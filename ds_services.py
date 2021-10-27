from ds_staff import form_component, runn


def get_component_info_by_name(component_name: str) -> dict:
    return form_component(component_name)


def get_product_info(barcode: str):
    return runn(barcode)

