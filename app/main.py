from fastapi import FastAPI
from app.routers import category, products, auth, permissions

app = FastAPI()

@app.get("/")
async def welcome() -> dict:
    return {"message": "My shop"}

app.include_router(category.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(permissions.router)