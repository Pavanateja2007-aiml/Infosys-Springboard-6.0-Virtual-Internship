# PERFORMANCE_TEST.py
# Performance / load tests for the FastAPI application.
# These tests hit a live running server at 127.0.0.1:8000 using the
# `requests` library and verify that the endpoints hold up under
# repeated rapid calls. Start the server before running these tests.

import requests


def test_load_root():
    """
    Load test for the root (GET /) endpoint.
    Sends 10 consecutive GET requests to the root URL and asserts that
    every response returns HTTP 200, confirming the endpoint remains
    stable under repeated load.
    """
    for _ in range(10):
        res = requests.get("http://127.0.0.1:8000/")
        assert res.status_code == 200


def test_load_voice():
    """
    Load test for the voice (POST /voice) endpoint.
    Sends 5 consecutive POST requests to /voice and asserts that every
    response returns HTTP 200, confirming the TwiML voice endpoint
    handles repeated calls without error.
    """
    for _ in range(5):
        res = requests.post("http://127.0.0.1:8000/voice")
        assert res.status_code == 200
