import asyncio
from decimal import Decimal

from models import Product, Component


async def main():

    components = [
        Component(
            name='Fake',
            is_healthy=True,
            description='some description'
        ),
        Component(
            name='Fake2',
            is_healthy=False,
            description='some description 2'
        ),
        Component(
            name='Fake3',
            is_healthy=True,
            description='some description 3'
        )
    ]

    product = await Product.objects.create(
        barcode='5999860497875',
        name='Dummy prod',
        proteins=Decimal('4.20'),
        fats=Decimal('6.9'),
        carbohydrates=Decimal('14.88'),
        calories=Decimal('101'),
        mass=Decimal('8'),
        package='Box',
        is_gmo=False,
        is_organic=True,
        is_vegetarian=False,
        is_vegan=False,
        utilize='Metal',
    )

    for comp in components:
        await comp.save()
        await product.components.add(comp)


async def test():
    # print(await Product.objects.select_related("components").all())
    # print(await Component.objects.all())
    print(await Product.objects.delete(each=True))

if __name__ == '__main__':
    asyncio.run(main())
