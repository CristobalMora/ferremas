from fastapi import FastAPI
from Ferremas.routers import auth, cart_items, inventory, items, pay_service, productos, purchase_details, receipts, sales, users
from Ferremas.sql_app.database import engine, Base

app = FastAPI()

# Reinicar base de datos cada vez que se inciae otra vez 
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Include routers from different modules with tags
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(cart_items.router, prefix="/cart_items", tags=["Cart Items"])
app.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
app.include_router(items.router, prefix="/items", tags=["Items"])
app.include_router(pay_service.router, prefix="/pay_service", tags=["Payment Service"])
app.include_router(productos.router, prefix="/productos", tags=["Products"])
app.include_router(purchase_details.router, prefix="/purchase_details", tags=["Purchase Details"])
app.include_router(receipts.router, prefix="/receipts", tags=["Receipts"])
app.include_router(sales.router, prefix="/sales", tags=["Sales"])
app.include_router(users.router, prefix="/users", tags=["Users"])

# Root endpoint
@app.get("/", tags=["Root"])
def read_root():
    return {"Hello": "World"}
