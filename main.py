from fastapi import FastAPI
from Ferremas.routers import auth, cart_items, inventory, items, pay_service, productos, purchase_details, receipts, sales, users
from Ferremas.sql_app import models, schemas, crud
from Ferremas.sql_app.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router, prefix="/users")
app.include_router(inventory.router, prefix="/inventory")
app.include_router(items.router, prefix="/items")
app.include_router(auth.router, prefix="/auth")
app.include_router(cart_items.router, prefix="/cart_items")
app.include_router(purchase_details.router, prefix="/purchase_details")
app.include_router(items.router, prefix="/items")
app.include_router(pay_service.router, prefix="/pay_service")
app.include_router(productos.router, prefix="/productos")
app.include_router(receipts.router, prefix="/receipts")
app.include_router(sales.router, prefix="/sales")

