from fastapi import FastAPI
from database import engine, Base
from app.routers import user, auth, inventory, sales, cart, cart_summary, dispatch, payment

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(auth.router, tags=["auth"])
app.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
app.include_router(sales.router, prefix="/sales", tags=["sales"])
app.include_router(cart.router, prefix="/cart", tags=["cart"])
app.include_router(cart_summary.router, prefix="/cart_summary", tags=["cart_summary"])
app.include_router(dispatch.router, prefix="/dispatch", tags=["dispatch"])
app.include_router(payment.router, prefix="/payments", tags=["payments"])
