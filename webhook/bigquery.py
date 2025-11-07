from google.cloud import bigquery
import os

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BQ_DATASET_ID = "shopify_raw_data"
CARTS_CREATE_UPDATE_TABLE_ID = "carts_create_update"
CARTS_CREATE_UPDATE_BQ_TABLE = f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{CARTS_CREATE_UPDATE_TABLE_ID}"
bigquery_client = bigquery.Client()

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
    