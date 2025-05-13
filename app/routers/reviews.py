from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.backend.db_depends import get_db
from app.models import Product
from app.models.review import Review
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas import CreateReview

router = APIRouter(prefix='/review', tags=['review'])

@router.get("/")
async def all_reviews(session: Annotated[AsyncSession, Depends(get_db)]):
    reviews = (
        await session.scalars(
            select(Review)
            .join(Product)
            .join(User)
            .where(Review.is_active == True,
                   Product.is_active == True,
                   User.is_active == True)
        )
    ).all()
    if reviews is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='There is not reviews found')
    return reviews

@router.get("/{product_slug}")
async def products_reviews(session: Annotated[AsyncSession, Depends(get_db)],
                             product_slug: str):
    product = await session.scalar(
        select(Product)
        .where(Product.slug == product_slug,
               Product.is_active == True)
    )
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Product not found')
    reviews = (
        await session.scalars(
        select(Review)
        .where(Review.product_id == product.id)
        )
    ).all()

    if reviews is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Reviews not found')

    return reviews

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_review(session: Annotated[AsyncSession, Depends(get_db)],
                        get_user: Annotated[dict, Depends(get_current_user)],
                        create_review: CreateReview):
    if get_user.get('is_supplier'):

        product = await session.scalar(select(Product).where(Product.id == create_review.product_id))
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no product found'
            )


        review = Review(
            user_id=create_review.user_id,
            product_id=create_review.product_id,
            comment=create_review.comment,
            grade=create_review.rate_grade
        )
        session.add(review)

        reviews = (
            await session.scalars(
                select(Review)
                .where(Review.product_id == create_review.product_id)
            )
        ).all()
        product.rating = sum(review.grade for review in reviews) / len(reviews)

        await session.commit()
        return {'status_code': status.HTTP_201_CREATED,
                'transaction': 'Successful'}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have supplier permission"
        )

@router.delete("/{review_id}")
async def delete_reviews(session: Annotated[AsyncSession, Depends(get_db)],
                         get_user: Annotated[dict, Depends(get_current_user)],
                         review_id: int):
    if get_user.get('is_admin'):
        await session.execute(update(Review)
                              .where(Review.id == review_id)
                              .values(is_active=False))
        await session.commit()
        return {'status_code': status.HTTP_200_OK,
            'transaction': 'Review delete is successful'}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin permission"
        )



