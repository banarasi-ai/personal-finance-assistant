from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class ProductPrice(BaseModel):
    """Product Price Schema"""

    product_id: int
    product_name: str
    product_price: float = Field(default=0.0, ge=0)
    product_search_date: datetime = Field(default_factory=datetime.now)
    product_search_url: Optional[str] = None
    product_search_vendor: Optional[str] = None
    product_additional_info: Optional[str] = Field(default_factory=lambda: "")


class ProductPriceBase(BaseModel):
    """Product Price Schema without ID"""

    product_name: str
    product_price: float = Field(default=0.0, ge=0)
    product_search_date: datetime = Field(default_factory=datetime.now)
    product_search_url: Optional[str] = None
    product_search_vendor: Optional[str] = None
    product_additional_info: Optional[str] = Field(default_factory=lambda: "")