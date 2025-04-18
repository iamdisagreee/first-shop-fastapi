from typing import Annotated

from fastapi import APIRouter
from fastapi import APIRouter, Depends, status, HTTPException
from slugify import slugify
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models import Category
from app.schemas import CreateCategory

router = APIRouter(prefix='/categories', tags=['category'])

@router.get('/')
async def get_all_categories(session: Annotated[AsyncSession, Depends(get_db)]):
    categories = await session.scalars(
        select(Category)
        .where(Category.is_active == True)
    )
    return categories.all()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_category(session: Annotated[AsyncSession, Depends(get_db)], create_category: CreateCategory):
    category = Category(
        name=create_category.name,
        parent_id=create_category.parent_id,
        slug=slugify(create_category.name)
    )
    session.add(category)
    await session.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Succesful'
    }

@router.put('/{category_slug}')
async def update_category(session: Annotated[AsyncSession, Depends(get_db)], category_slug: str,
                          update_category: CreateCategory):
    category = await session.scalar(select(Category).where(Category.slug == category_slug))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )

    await session.execute(update(Category).where(Category.slug == category_slug).values(
            name=update_category.name,
            slug=slugify(update_category.name),
            parent_id=update_category.parent_id))

    await session.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Category update is successful'
    }



@router.delete('/{category_slug}')
async def delete_category(session: Annotated[AsyncSession, Depends(get_db)], category_slug: str):
    category = await session.scalar(select(Category).where(Category.slug == category_slug,
                                                           Category.is_active == True))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found!'
        )
    await session.execute(update(Category).where(Category.slug == category_slug).values(is_active=False))
    await session.commit()

    return {'status_code': status.HTTP_200_OK,
            'transaction': 'Category delete is successful'}

