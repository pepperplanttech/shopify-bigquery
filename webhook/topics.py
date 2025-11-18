from bigquery import stream_to_bq_carts_create_update
from datetime import datetime
from google.cloud import bigquery
from pydantic import ValidationError
from models import CartsCreateUpdateWebhook, LineItem
import os
import pytz


GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
bigquery_client = bigquery.Client()


class TopicHandlerResult:
    def __init__(self, status: str = "", message: str = "", response_code: int = 200):
        self.status = status
        self.message = message
        self.response_code = response_code

def handle_cart_create_update(data: dict, topic: str = "") -> TopicHandlerResult:
    topic_handler_result = TopicHandlerResult()

    try:
        create_update_webhook_data = CartsCreateUpdateWebhook(**data)
        # Replace with logging in production
        print("✅ Webhook data validated successfully."
              f" Cart ID: {create_update_webhook_data.id}, Created At: {create_update_webhook_data.created_at}")
        
        utc_now = datetime.now(pytz.utc).isoformat() 
        bq_line_items = [prepare_line_item_bq_carts_create_update(item) for item in create_update_webhook_data.line_items]
        total_price = sum(float(item.line_price) for item in create_update_webhook_data.line_items)
        row_to_insert = {
            "id": create_update_webhook_data.id,
            "token": create_update_webhook_data.token,
            "note": create_update_webhook_data.note,
            "updated_at": create_update_webhook_data.updated_at,
            "created_at": create_update_webhook_data.created_at,
            "line_items": bq_line_items,
            "webhook_received_at": utc_now,
            "total_price": total_price,
            "topic": topic
        }
        stream_to_bq_carts_create_update(row_to_insert)
        topic_handler_result = TopicHandlerResult("success", "Webhook processed successfully", 200)

    except ValidationError as e:
        # Replace with logging in production
        print(f"❌ Pydantic Validation Error: {e.errors()}")
        topic_handler_result = TopicHandlerResult("error", "Invalid webhook payload structure", 400)

    except Exception:
        topic_handler_result = TopicHandlerResult("error", "❌ Failed to stream to BigQuery", 500)

    return topic_handler_result


def prepare_line_item_bq_carts_create_update(item: LineItem) -> dict:
    print("⚠️ Preparing line item for BigQuery:", item)
    return {
        "id": item.id,
        "quantity": item.quantity,
        "variant_id": item.variant_id,
        "key": item.key,
        "discounted_price": float(item.discounted_price) if item.discounted_price else None,
        "grams": item.grams,
        "line_price": float(item.line_price),
        "original_line_price": float(item.original_line_price) if item.original_line_price else None,
        "original_price": float(item.original_price) if item.original_price else None,
        "price": float(item.price), 
        "product_id": item.product_id,
        "sku": item.sku,
        "title": item.title,
        "total_discount": float(item.total_discount) if item.total_discount else None,
        "vendor": item.vendor,
    }

topic_handlers = {
    "carts/create": handle_cart_create_update,
    "carts/update": handle_cart_create_update,
}

accepted_topics = list(topic_handlers.keys())