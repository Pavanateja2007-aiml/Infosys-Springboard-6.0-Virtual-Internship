# UNIT_TEST.py
# Unit tests for the FastAPI application using FastAPI's built-in TestClient.
# These tests validate individual endpoints in isolation without requiring
# a live server instance.

from fastapi.testclient import TestClient
from main import app

# Initialize the test client with the FastAPI app instance
client = TestClient(app)


def test_root():
    """
    Test the root (GET /) endpoint.
    Verifies that the server is running and returns the expected
    health-check JSON response: {"message": "Server Running"}.
    """
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["message"] == "Server Running"


def test_voice():
    """
    Test the voice (POST /voice) endpoint.
    Verifies that a POST request to /voice returns a valid TwiML response
    containing a <Say> verb, confirming the voice greeting is rendered correctly.
    """
    res = client.post("/voice")
    assert res.status_code == 200
    assert "<Say>" in res.text


def test_language_selection():
    """
    Test the language selection (POST /language) endpoint.
    Simulates a Twilio DTMF input where the caller presses '1' (English).
    Verifies that the response contains a <Gather> TwiML verb, indicating
    the IVR is prompting the user for further input after language selection.
    """
    res = client.post("/language", data={"Digits": "1"})
    assert res.status_code == 200
    assert "<Gather" in res.text
