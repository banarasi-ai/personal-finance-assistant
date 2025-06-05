from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class Transaction(BaseModel):
    """Transaction Schema"""
    transaction_id: int
    transaction_date: datetime
    amount: float = Field(default=0.0,ge=0)
    vendor_name: Optional[str] = None
    category: Optional[str] = None
    transaction_additional_info: Optional[str] = Field(default_factory=lambda: "")

class TransactionBase(BaseModel):
    """Transaction Schema without ID"""
    transaction_date: datetime
    amount: float = Field(default=0.0,ge=0)
    vendor_name: Optional[str] = None
    category: Optional[str] = None
    transaction_additional_info: Optional[str] = Field(default_factory=lambda: "")