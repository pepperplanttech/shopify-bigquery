from flask import jsonify
from pydantic import ValidationError
from models import CartsCreateUpdateWebhook, LineItem
from google.cloud import bigquery
from datetime import datetime
import os
import pytz


# Environment Variables for Google Cloud Platform / BigQuery setup
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID") 
BQ_DATASET_ID = "shopify_raw_data"
CARTS_CREATE_UPDATE_TABLE_ID = "carts_create_update"
CARTS_CREATE_UPDATE_BQ_TABLE = f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{CARTS_CREATE_UPDATE_TABLE_ID}"

bigquery_client = bigquery.Client()

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

def stream_to_bq_carts_create_update(row_data: dict):
    try:
        errors = bigquery_client.insert_rows_json(
            CARTS_CREATE_UPDATE_BQ_TABLE, 
            [row_data]
        )

        if errors:
            print(f"❌ BigQuery Insert Errors: {errors}")
            raise Exception(f"Failed to insert row into BigQuery: {errors}")
        else:
            print("✅ Data successfully streamed to BigQuery.")

    except Exception as e:
        print(f"⚠️ An unexpected error occurred during BigQuery stream: {e}")
        raise

# Main entry point for the webhook
def shopify_webhook_handler(request=None):
    if GCP_PROJECT_ID is None:
        return 'Internal Server Error: Missing environment variable: GCP_PROJECT_ID', 500
    
    if request is None:
        return 'Internal Server Error: Missing Request Object', 500

    if request.method != 'POST':
        return 'Method Not Allowed', 405

    topic = request.headers.get('X-Shopify-Topic')

    try:
        data = request.get_json(silent=True)
        if data is None:
            raise ValueError("No JSON data received in request.")
            
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return jsonify({"status": "error", "message": "Invalid JSON format"}), 400

    if topic == 'carts/create' or topic == 'carts/update':
            print(f"⚠️ Received {topic.upper()} event for Cart ID: {data.get('id')}")
            handle_cart_create_update(data, topic)
    else:
        print(f"❌ Unhandled Shopify topic: {topic}")
        return jsonify({"status": "error", "message": "Unhandled Shopify topic"}), 400

    return jsonify({"status": "success"}), 200

def handle_cart_create_update(data: dict, topic: str = ""):
    try:
        create_update_webhook_data = CartsCreateUpdateWebhook(**data)
        print("✅ Webhook data validated successfully."
              f" Cart ID: {create_update_webhook_data.id}, Created At: {create_update_webhook_data.created_at}")
    except ValidationError as e:
        print(f"❌ Pydantic Validation Error: {e.errors()}")
        return jsonify({"status": "error", "message": "Invalid webhook payload structure"}), 400
    
    utc_now = datetime.now(pytz.utc).isoformat() 
    bq_line_items = [prepare_line_item_bq_carts_create_update(item) for item in create_update_webhook_data.line_items]
    total_price = sum(float(item.line_price) for item in create_update_webhook_data.line_items)

    # Construct the final row to insert
    row_to_insert = {
        "id": create_update_webhook_data.id,
        "token": create_update_webhook_data.token,
        "note": create_update_webhook_data.note,
        "updated_at": create_update_webhook_data.updated_at,
        "created_at": create_update_webhook_data.created_at,
        "line_items": bq_line_items,
        "webhook_received_at": utc_now,
        "total_price": total_price,
        "topic": topic,
    }

    try:
        stream_to_bq_carts_create_update(row_to_insert)

    except Exception:
        return jsonify({"status": "error", "message": "❌ Failed to stream to BigQuery"}), 500

    return jsonify({
        "status": "success", 
        "topic": topic,
        "cart_id": create_update_webhook_data.id, 
        "webhook_received_at": utc_now,
        }), 200
