from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # baad mein Alembic migrations lagayenge
    yield


app = FastAPI(title="Catalog Service", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- Retailers ----------
@app.post("/retailers", response_model=schemas.RetailerOut, status_code=201)
def create_retailer(data: schemas.RetailerCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(models.Retailer).where(models.Retailer.phone == data.phone))
    if exists:
        raise HTTPException(409, "Is phone number se retailer already registered hai")
    retailer = models.Retailer(**data.model_dump())
    db.add(retailer)
    db.commit()
    db.refresh(retailer)
    return retailer


@app.get("/retailers", response_model=list[schemas.RetailerOut])
def list_retailers(pincode: str | None = None, db: Session = Depends(get_db)):
    stmt = select(models.Retailer).where(models.Retailer.is_active.is_(True))
    if pincode:
        stmt = stmt.where(models.Retailer.pincode == pincode)
    return db.scalars(stmt).all()


@app.get("/retailers/{retailer_id}", response_model=schemas.RetailerOut)
def get_retailer(retailer_id: int, db: Session = Depends(get_db)):
    retailer = db.get(models.Retailer, retailer_id)
    if not retailer:
        raise HTTPException(404, "Retailer nahi mila")
    return retailer


# ---------- Products ----------
@app.post("/retailers/{retailer_id}/products", response_model=schemas.ProductOut, status_code=201)
def add_product(retailer_id: int, data: schemas.ProductCreate, db: Session = Depends(get_db)):
    if not db.get(models.Retailer, retailer_id):
        raise HTTPException(404, "Retailer nahi mila")
    product = models.Product(retailer_id=retailer_id, **data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.get("/products", response_model=list[schemas.ProductOut])
def list_products(
    retailer_id: int | None = None,
    q: str | None = Query(default=None, description="naam se search"),
    db: Session = Depends(get_db),
):
    stmt = select(models.Product).where(models.Product.is_available.is_(True))
    if retailer_id:
        stmt = stmt.where(models.Product.retailer_id == retailer_id)
    if q:
        stmt = stmt.where(models.Product.name.ilike(f"%{q}%"))
    return db.scalars(stmt).all()


@app.get("/products/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(404, "Product nahi mila")
    return product


@app.put("/products/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, data: schemas.ProductUpdate, db: Session = Depends(get_db)):
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(404, "Product nahi mila")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(404, "Product nahi mila")
    db.delete(product)
    db.commit()