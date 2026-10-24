from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class RetailerCreate(BaseModel):
    shop_name: str = Field(min_length=2, max_length=120)
    owner_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=10, max_length=15)
    address: str = Field(min_length=5, max_length=255)
    pincode: str = Field(min_length=6, max_length=10)


class RetailerOut(RetailerCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool
    created_at: datetime


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=500)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=500)
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)
    is_available: bool | None = None


class ProductOut(ProductCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    retailer_id: int
    is_available: bool
    created_at: datetime