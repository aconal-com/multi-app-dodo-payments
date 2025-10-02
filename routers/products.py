"""
Product Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal

from services.database import get_db, ProductCatalog
from middleware.auth import get_current_app_name

router = APIRouter(prefix="/products", tags=["products"])


# Request/Response Models
class ProductResponse(BaseModel):
    product_id: str
    product_name: str
    description: Optional[str]
    product_type: str
    price: float
    currency: str
    credits_granted: int
    is_popular: bool
    is_active: bool
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int


@router.get("/{app_name}", response_model=ProductListResponse)
async def list_products(
    app_name: str,
    active_only: bool = True,
    db: Session = Depends(get_db),
    authenticated_app: str = Depends(get_current_app_name)
):
    """
    List all products for an app
    
    Query params:
    - active_only: Return only active products (default: true)
    """
    # Verify app access
    if app_name != authenticated_app:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this app's products"
        )
    
    # Query products
    query = db.query(ProductCatalog).filter(
        ProductCatalog.app_name == app_name
    )
    
    if active_only:
        query = query.filter(ProductCatalog.is_active == True)
    
    products = query.order_by(ProductCatalog.display_order).all()
    
    return ProductListResponse(
        products=[
            ProductResponse(
                product_id=p.product_id,
                product_name=p.product_name,
                description=p.description,
                product_type=p.product_type.value,
                price=float(p.price),
                currency=p.currency,
                credits_granted=p.credits_granted,
                is_popular=p.is_popular,
                is_active=p.is_active
            )
            for p in products
        ],
        total=len(products)
    )


@router.get("/{app_name}/{product_id}", response_model=ProductResponse)
async def get_product(
    app_name: str,
    product_id: str,
    db: Session = Depends(get_db),
    authenticated_app: str = Depends(get_current_app_name)
):
    """Get details of a specific product"""
    if app_name != authenticated_app:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    product = db.query(ProductCatalog).filter(
        ProductCatalog.app_name == app_name,
        ProductCatalog.product_id == product_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return ProductResponse(
        product_id=product.product_id,
        product_name=product.product_name,
        description=product.description,
        product_type=product.product_type.value,
        price=float(product.price),
        currency=product.currency,
        credits_granted=product.credits_granted,
        is_popular=product.is_popular,
        is_active=product.is_active
    )

