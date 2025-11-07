from pydantic import BaseModel, Field
from typing import List, Optional

"""
Pydantic models for Shopify Webhooks

Models have been slimmed down for 'carts/create' and 'carts/update' webhook payloads, focusing on selected fields.
"""
class LineItem(BaseModel):
    """
    Represents a single item in the cart, compatible with both carts/create and carts/update webhook payloads.
    """
    id: Optional[int] = Field(None, description="The unique identifier for the line item.")
    quantity: int = Field(..., description="The quantity of the item.")
    variant_id: int = Field(..., description="The ID of the product variant.")
    key: str = Field(..., description="A unique identifier for the line item within the cart.")
    discounted_price: Optional[str] = Field(None, description="The price of the item after discounts.")
    grams: int = Field(..., description="The weight of the item in grams.")
    line_price: str = Field(..., description="The total price for the line item (quantity * price).")
    original_line_price: Optional[str] = Field(None, description="The total price before any line-item specific discounts.")
    original_price: Optional[str] = Field(None, description="The price of the product variant before line-item specific discounts.")
    price: str = Field(..., description="The price of the product variant (unit price).")
    product_id: int = Field(..., description="The ID of the product.")
    sku: str = Field(..., description="The Stock Keeping Unit of the variant.")
    title: str = Field(..., description="The title of the product.")
    total_discount: Optional[str] = Field(None, description="The total discount amount for this line item.")
    vendor: str = Field(..., description="The vendor of the product.")

# Models for the Webhook Payloads
class CartsCreateUpdateWebhook(BaseModel):
    """Slimmed down Pydantic model for the Shopify 'carts/create' and 'carts/update'webhook payloads."""
    id: str = Field(..., description="The unique ID of the cart.")
    token: str = Field(..., description="A unique token that identifies the cart (often the same as 'id').")
    note: Optional[str] = Field(None, description="Extra information about the cart.")
    line_items: List[LineItem] = Field(..., description="A list of items in the cart.")
    updated_at: str = Field(..., description="The date and time when the cart was last updated.")
    created_at: str = Field(..., description="The date and time when the cart was created.")
