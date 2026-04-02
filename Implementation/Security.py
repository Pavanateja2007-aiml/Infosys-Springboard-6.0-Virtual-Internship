# ================================
# SECURITY MODULE
# ================================

from twilio.request_validator import RequestValidator
import os
import re

# -------------------------------
# CONFIG
# -------------------------------
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "your_auth_token")

validator = RequestValidator(TWILIO_AUTH_TOKEN)

# -------------------------------
# TWILIO REQUEST VALIDATION
# -------------------------------
def validate_twilio_request(request):
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    form = dict(request.form())

    return validator.validate(url, form, signature)


# -------------------------------
# PII MASKING
# -------------------------------
def mask_pii(text):
    # Mask phone numbers
    text = re.sub(r'\b\d{10}\b', 'XXXXXXXXXX', text)

    # Mask booking IDs (example: ABC1234)
    text = re.sub(r'\b[A-Z]{3}\d{4}\b', 'XXXXXXX', text)

    # Mask names (basic)
    text = re.sub(r'\b[A-Z][a-z]+\b', 'NAME', text)

    return text


# -------------------------------
# RATE LIMIT (BASIC)
# -------------------------------
request_counts = {}

def rate_limit(ip):
    if ip not in request_counts:
        request_counts[ip] = 0

    request_counts[ip] += 1

    if request_counts[ip] > 50:
        return False

    return True