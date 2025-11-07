resource "google_bigquery_dataset" "shopify_raw_data" {
  dataset_id                  = "shopify_raw_data"
  friendly_name               = "Shopify Raw Webhook Data"
  description                 = "Contains raw, near-real-time data from Shopify webhooks."
  project                     = var.project_id
  location                    = "US"
  delete_contents_on_destroy  = false
}

resource "google_bigquery_table" "carts_create_update" {
  dataset_id  = google_bigquery_dataset.shopify_raw_data.dataset_id
  table_id    = "carts_create_update"
  project     = var.project_id
  description = "Real-time Shopify cart creation/update events from webhooks."

  # Time Partitioning is highly recommended
  time_partitioning {
    type  = "DAY"
    field = "webhook_received_at" # Partition on the data ingestion timestamp
  }

  schema = <<EOF
[
  { "name": "id", "type": "STRING", "mode": "REQUIRED", "description": "The unique Shopify Cart Token/ID." },
  { "name": "token", "type": "STRING", "mode": "NULLABLE", "description": "The unique token associated with the cart (often the same as the ID)." },
  { "name": "note", "type": "STRING", "mode": "NULLABLE", "description": "Any note added to the cart." },
  { "name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE", "description": "The time the cart was created (ISO 8601)." },
  { "name": "updated_at", "type": "TIMESTAMP", "mode": "NULLABLE", "description": "The time the cart was last updated (ISO 8601)." },
  { "name": "webhook_received_at", "type": "TIMESTAMP", "mode": "REQUIRED", "description": "The timestamp the Cloud Function received the payload." },
  { "name": "total_price", "type": "NUMERIC", "mode": "NULLABLE", "description": "Total price of the cart (extracted from the string value in the payload)." },
  { "name": "topic", "type": "STRING", "mode": "REQUIRED", "description": "Shopify topic from X-Shopify-Topic HTTP header." },
  
  {
    "name": "line_items",
    "type": "RECORD",
    "mode": "REPEATED",
    "description": "Repeated line item details for each product in the cart.",
    "fields": [
      { "name": "id", "type": "INTEGER", "mode": "NULLABLE" },
      { "name": "quantity", "type": "INTEGER", "mode": "NULLABLE" },
      { "name": "variant_id", "type": "INTEGER", "mode": "NULLABLE" },
      { "name": "key", "type": "STRING", "mode": "NULLABLE" },
      { "name": "discounted_price", "type": "NUMERIC", "mode": "NULLABLE", "description": "Discounted price for this line item (extracted from the string value in the payload)." },
      { "name": "grams", "type": "INTEGER", "mode": "NULLABLE", "description": "Weight of the item in grams (from payload)." },
      { "name": "line_price", "type": "NUMERIC", "mode": "NULLABLE", "description": "Total price for this line item (extracted from the string value in the payload)." },
      { "name": "original_line_price", "type": "NUMERIC", "mode": "NULLABLE", "description": "Original total price before discounts (if any)." },
      { "name": "original_price", "type": "NUMERIC", "mode": "NULLABLE", "description": "Original unit price before discounts (if any)." },
      { "name": "price", "type": "NUMERIC", "mode": "NULLABLE", "description": "Unit price (extracted from the string value in the payload)." },
      { "name": "product_id", "type": "INTEGER", "mode": "NULLABLE" },
      { "name": "sku", "type": "STRING", "mode": "NULLABLE" },
      { "name": "title", "type": "STRING", "mode": "NULLABLE" },
      { "name": "total_discount", "type": "NUMERIC", "mode": "NULLABLE", "description": "Total discount applied to this line item (if any)." },
      { "name": "vendor", "type": "STRING", "mode": "NULLABLE", "description": "Vendor name (from payload)." }
    ]
  }
]
EOF
}
