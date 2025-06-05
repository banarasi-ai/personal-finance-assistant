from fastapi import APIRouter

from app import endpoint_product, endpoint_transaction


router1 = APIRouter()
router2 = APIRouter()
#router.include_router(endpoint.router, prefix="/events", tags=["events"])

router1.include_router(endpoint_transaction.router, prefix="/transactions", tags=["expenses"])
router2.include_router(endpoint_product.router, prefix="/product_prices", tags=["wishlist"])


