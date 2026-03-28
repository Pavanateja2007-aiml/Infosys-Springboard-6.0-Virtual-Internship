# INTEGRATION_TEST.py
# Integration tests for the FastAPI application.
# These tests verify that multiple components work correctly together —
# intent detection, routing logic, and TwiML response generation.
# Some tests use TestClient (no live server needed); load tests use
# `requests` and require the server to be running at 127.0.0.1:8000.

from fastapi.testclient import TestClient
from main import app
import requests

# Initialize the test client with the FastAPI app instance
client = TestClient(app)


def test_pnr_intent():
    """
    Integration test for PNR intent detection via POST /process-intent.
    Simulates a speech input of "check pnr" and verifies that the response
    redirects to the /ask-pnr route, confirming the intent classifier and
    routing logic work together correctly.
    """
    res = client.post("/process-intent", data={"SpeechResult": "check pnr"})
    assert res.status_code == 200
    assert "/ask-pnr" in res.text


def test_train_intent():
    """
    Integration test for train status intent detection via POST /process-intent.
    Simulates a speech input of "train status" and verifies that the response
    redirects to the /ask-train route, confirming the correct intent is
    identified and the appropriate handler is invoked.
    """
    res = client.post("/process-intent", data={"SpeechResult": "train status"})
    assert res.status_code == 200
    assert "/ask-train" in res.text


def test_load_voice():
    """
    Load test for the voice (POST /voice) endpoint against a live server.
    Sends 5 consecutive POST requests and asserts HTTP 200 on each,
    verifying the endpoint is stable under repeated integration-level load.
    Requires the server to be running at http://127.0.0.1:8000.
    """
    for _ in range(5):
        res = requests.post("http://127.0.0.1:8000/voice")
        assert res.status_code == 200


def test_empty_input():
    """
    Edge-case integration test for POST /process-intent with no input data.
    Sends a request with an empty payload and asserts HTTP 200, verifying
    that the endpoint handles missing SpeechResult gracefully without
    crashing or returning a server error.
    """
    res = client.post("/process-intent", data={})
    assert res.status_code == 200
