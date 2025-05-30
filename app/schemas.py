from pydantic import BaseModel

class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category: int

class CreateCategory(BaseModel):
    name: str
    parent_id: int | None = None

class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str

class CreateReview(BaseModel):
    user_id: int
    product_id: int
    comment: str
    rate_grade: int