from flask import Request
import hmac
import hashlib
import base64
from topics import accepted_topics
from typing import Union


class ValidationResult:
    def __init__(self, is_valid: bool, message: str = None, response_code: int = 200, request_data: dict = None):
        self.is_valid = is_valid
        self.message = message
        self.response_code = response_code
        self.request_data = request_data

def verify_valid_request(request: Request, GCP_PROJECT_ID: str, topic: str) -> ValidationResult:
    # TODO: Implement shopify request header signature verification
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256", "")

    # Request Method Validation
    if request.method != 'POST':
        validation_result = ValidationResult(False, 'Method Not Allowed', 405)
        return validation_result
    
    # Environment Validation
    if GCP_PROJECT_ID is None:
        validation_result = ValidationResult(False, 'Internal Server Error: Missing GCP_PROJECT_ID', 500)
        return validation_result

    # Topic validation
    if topic not in accepted_topics:
        validation_result = ValidationResult(False, 'Unsupported Topic', 400)
        return validation_result
    
    # JSON Body Validation
    try:
        request_data = request.get_json(silent=True)
        if request_data is None:
            raise ValueError("No JSON data received in request.")
    except Exception as e:
        validation_result = ValidationResult(False, 'Invalid JSON format', 400)
        return validation_result
    
    # Successful Validation
    return ValidationResult(True, request_data=request_data)


# def verify_shopify_webhook(raw_body: Union[bytes, str], hmac_header: str) -> bool:
#     """
#     Verifies the Shopify webhook signature.

#     :param raw_body: The raw, unparsed request body (must be bytes).
#     :param hmac_header: The value of the X-Shopify-Hmac-Sha256 header.
#     :return: True if the signature is valid, False otherwise.
#     """
#     SHOPIFY_WEBHOOK_SECRET = "" # Replace with value from call to Google Secret Manager

#     if isinstance(raw_body, str):
#         # Ensure the body is in bytes for hashing
#         raw_body = raw_body.encode('utf-8')

#     # 2. Calculate the HMAC-SHA256 digest
#     # The key must be in bytes
#     calculated_hmac = hmac.new(
#         key=SHOPIFY_WEBHOOK_SECRET.encode('utf-8'),
#         msg=raw_body,
#         digestmod=hashlib.sha256
#     )

#     # 3. Encode the calculated digest in base64
#     calculated_digest = base64.b64encode(calculated_hmac.digest()).decode()

#     # 4. Securely compare the calculated digest with the header value
#     # hmac.compare_digest is used to prevent timing attacks.
#     return hmac.compare_digest(calculated_digest, hmac_header)


# # --- Example Usage (Placeholders) ---

# # This is the raw request body (e.g., from Flask's request.data or FastAPI's await request.body())
# example_raw_body = b'{"id":1234567890,"email":"customer@example.com","created_at":"2025-10-31T22:13:30-04:00"}'

# # This is the signature read from the 'X-Shopify-Hmac-Sha256' header
# # Replace this with the actual header value in your application
# example_hmac_header = "W9rCg7mQ1S3j/7/I1Y7xT5q7j/K0/L+X0cQ2Xv4Z0kI=" # A hypothetical or actual example

# if verify_shopify_webhook(example_raw_body, example_hmac_header):
#     print("✅ Webhook signature is valid. Processing request.")
# else:
#     print("❌ Webhook signature is INVALID. Rejecting request.")