from http.client import HTTPException
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from starlette import status

from app.backend.db_depends import get_db
from app.models import Product, Category
from app.routers.auth import get_current_user
from app.schemas import CreateProduct

router = APIRouter(prefix='/products', tags=['products'])


@router.get('/')
async def all_products(session: Annotated[AsyncSession, Depends(get_db)]):
    products = (
        await session.scalars(
            select(Product)
            .join(Category)
            .where(Product.is_active == True,
                   Product.stock > 0,
                   Category.is_active == True)
        )
    ).all()
    if products is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='There is not products found')
    return products


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_product(session: Annotated[AsyncSession, Depends(get_db)],
                         get_user: Annotated[dict, Depends(get_current_user)],
                         create_product: CreateProduct):
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        category = await session.scalar(select(Category).where(Category.id == create_product.category))
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no category found'
            )
        product = Product(
            name=create_product.name,
            slug=slugify(create_product.name),
            description=create_product.description,
            price=create_product.price,
            image_url=create_product.image_url,
            stock=create_product.stock,
            rating=0.0,
            category_id=create_product.category,
            supplier_id=get_user.get('id')
        )
        session.add(product)
        await session.commit()
        return {'status_code': status.HTTP_201_CREATED,
                'transaction': 'Successful'}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to use this method"
        )


@router.get('/{category_slug}')
async def product_by_category(session: Annotated[AsyncSession, Depends(get_db)], category_slug: str):
    category = (
        await session.scalar(
            select(Category)
            .where(Category.slug == category_slug)
        )
    )
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Category not found')
    subcategories = (
        await session.scalars(
            select(Category)
            .where(Category.parent_id == category.id)
        )
    ).all()

    categories_and_subcategories = [category.id] + [x.id for x in subcategories]

    product_category = await session.scalars(
        select(Product)
        .where(
            Product.category_id.in_(categories_and_subcategories),
            Product.is_active == True,
            Product.stock > 0
        )
    )
    return product_category.all()



@router.get('/detail/{product_slug}')
async def product_detail(session: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await session.scalar(
        select(Product).where(Product.slug == product_slug, Product.is_active == True, Product.stock > 0))
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no product'
        )
    return product


@router.put("/{product_slug}")
async def update_product(session: Annotated[AsyncSession, Depends(get_db)],
                         get_user: Annotated[dict, Depends(get_current_user)],
                         product_slug: str,
                         product_update: CreateProduct):
    product = await session.scalar(
        select(Product)
        .where(Product.slug == product_slug)
    )
    if get_user.get('is_admin') or \
        (get_user.get('is_supplier') and get_user.get('id') == product.supplier_id):
        product = await session.scalar(
            select(Product)
            .where(Product.slug == product_slug)
        )
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='There is not product found')
        category = await session.scalar(
            select(Category)
            .where(Category.id == product_update.category)
        )
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='There is no category found')

        product.name = product_update.name
        product.slug = slugify(product_update.name)
        product.description = product_update.description
        product.price = product_update.price
        product.image_url = product_update.image_url
        product.stock = product_update.stock
        product.category_id = product_update.category
        await session.commit()

        return {'status_code': status.HTTP_200_OK,
                'transaction': 'Product update is successful'}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to use this method"
        )



@router.delete("/{product_slug}")
async def delete_product(session: Annotated[AsyncSession, Depends(get_db)],
                         get_user: Annotated[dict, Depends(get_current_user)],
                         product_slug: str):
    product = await session.scalar(
        select(Product)
        .where(Product.slug == product_slug)
    )
    if get_user.get('is_admin') or \
            (get_user.get('is_supplier') and get_user.get('id') == product.supplier_id):
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='There is not product found')
        product.is_active = False
        await session.commit()
        return {'status_code': status.HTTP_200_OK,
                'transaction': 'Product delete is successful'}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to use this method"
        )

