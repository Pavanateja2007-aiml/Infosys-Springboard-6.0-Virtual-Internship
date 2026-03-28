# E2E_TEST.py
# End-to-end (E2E) tests for the FastAPI IVR application.
# These tests simulate complete real-world call flows from start to finish,
# chaining multiple endpoint calls in sequence to validate that the entire
# user journey works correctly — from call initiation through intent handling.

from fastapi.testclient import TestClient
from main import app

# Initialize the test client with the FastAPI app instance
client = TestClient(app)


def test_full_call_flow():
    """
    E2E test for a complete IVR call flow ending at PNR inquiry.

    Simulates a caller going through three steps:
      Step 1 — POST /voice        : Call is received; welcome TwiML is returned.
      Step 2 — POST /language     : Caller presses '1' to select English.
      Step 3 — POST /process-intent: Caller says "pnr"; intent is detected.

    Each step asserts HTTP 200, verifying the entire flow is functional
    end-to-end without any intermediate failures.
    """
    # Step 1: Incoming call triggers the voice greeting
    res = client.post("/voice")
    assert res.status_code == 200

    # Step 2: Caller selects English by pressing digit '1'
    res = client.post("/language", data={"Digits": "1"})
    assert res.status_code == 200

    # Step 3: Caller speaks "pnr"; intent processor handles the request
    res = client.post("/process-intent", data={"SpeechResult": "pnr"})
    assert res.status_code == 200


def test_booking_flow():
    """
    E2E test for the ticket booking intent flow.

    Simulates a caller saying "book ticket" and verifies that the response
    redirects to /ask-origin, confirming the booking intent is correctly
    identified and the first step of the booking journey is initiated.
    """
    res = client.post("/process-intent", data={"SpeechResult": "book ticket"})
    assert res.status_code == 200
    assert "/ask-origin" in res.text
