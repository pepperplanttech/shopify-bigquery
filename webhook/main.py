from flask import jsonify
import os
from validation import verify_valid_request
from topics import topic_handlers


GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")

def shopify_webhook_handler(request=None):
    """
    Google Cloud Function to handle Shopify Webhook events.
    Processes 'carts/create' and 'carts/update' events and streams data to Big Query.

    :param request: Flask Request object containing the webhook payload.
    :return: Flask Response object with status of processing.
    """
    topic = request.headers.get("X-Shopify-Topic", "")
    validation_result = verify_valid_request(request, GCP_PROJECT_ID, topic)

    if not validation_result.is_valid:
        return jsonify({"status": "error", "message": validation_result.message}), validation_result.response_code

    topic_hander_result = topic_handlers[topic](validation_result.request_data, topic)

    return jsonify({"status": "success", "message": topic_hander_result.message}), topic_hander_result.response_code

    # return jsonify({"status": "success", "message": "Webhook processed successfully"}), 200

