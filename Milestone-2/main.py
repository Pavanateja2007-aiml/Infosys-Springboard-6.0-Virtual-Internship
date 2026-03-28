# ================================
# IRCTC IVR SYSTEM - FIXED VERSION
# ================================

from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
import json
import logging
import os

# ================================
# Logging Configuration
# ================================

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Railway IVR System")

# ================================
# Utility Functions
# ================================

def load_data():
    """Load railway data from JSON file."""
    try:
        with open("irctc.json") as file:
            data = json.load(file)
            logging.info("JSON data loaded successfully")
            return data
    except Exception as e:
        logging.error(f"Error loading JSON: {e}")
        return {}

def fetch_pnr_details(pnr_number: str):
    """Return PNR details."""
    logging.info(f"PNR requested: {pnr_number}")

    data = load_data()
    ticket = data.get(pnr_number)

    if ticket:
        return f"Ticket status is {ticket['status']}. Coach {ticket['coach']}, Seat {ticket['seat']}."

    return "Sorry. PNR number not found."

def fetch_train_schedule(train_number: str):
    """Return train schedule."""
    logging.info(f"Train schedule requested: {train_number}")

    data = load_data()
    train = data.get(train_number)

    if train:
        return f"Departure at {train['departure']} and arrival at {train['arrival']}."

    return "Train details not available."

# ================================
# Root Endpoint
# ================================

@app.get("/")
async def home():
    logging.info("Server status checked")
    return {"status": "IVR Server Active"}

# ================================
# Twilio Call Trigger
# ================================

# FIX 1: Use environment variables instead of hardcoded credentials (security fix)
ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "AC******************************")
AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN",  "***********************")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER", "+19378836071")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

@app.get("/make-call")
async def make_call():
    try:
        logging.info("Triggering outbound call")

        call = client.calls.create(
            to="+919346196255",
            from_=TWILIO_NUMBER,
            url="https://nonhackneyed-ichnographic-maxima.ngrok-free.dev/voice"
        )

        logging.info(f"Call created: {call.sid}")
        return {"call_id": call.sid, "call_status": call.status}

    except Exception as e:
        logging.error(f"Call error: {e}")
        return {"error": str(e)}

# ================================
# Voice Entry
# ================================

@app.api_route("/voice", methods=["GET", "POST"])
async def voice(request: Request):
    try:
        logging.info("Incoming call received")

        vr = VoiceResponse()
        menu = Gather(num_digits=1, action="/select-language", method="POST")
        menu.say(
            "Welcome to Railway Information System. "
            "Press 1 for English. "
            "Press 2 for Hindi."
        )
        vr.append(menu)

        # FIX 2: Added redirect fallback so the call loops back instead of dropping
        vr.say("No input detected. Please try again.")
        vr.redirect("/voice")   # <-- was vr.hangup(), call now retries

        return Response(str(vr), media_type="application/xml")

    except Exception as e:
        logging.error(f"Voice error: {e}")
        return {"error": str(e)}

# ================================
# Language Selection
# ================================

@app.api_route("/select-language", methods=["GET", "POST"])
async def select_language(request: Request):
    try:
        form = await request.form()
        logging.info(f"Language input: {form}")

        choice = form.get("Digits")
        vr = VoiceResponse()

        if choice == "1":
            return await main_options()

        elif choice == "2":
            vr.say("Hindi service will be available soon.")
            vr.hangup()

        else:
            vr.say("Invalid selection.")
            vr.redirect("/voice")

        return Response(str(vr), media_type="application/xml")

    except Exception as e:
        logging.error(f"Language error: {e}")
        return {"error": str(e)}

# ================================
# Main Menu
# ================================

async def main_options():
    vr = VoiceResponse()

    options = Gather(num_digits=1, action="/handle-option", method="POST")
    options.say(
        "Press 1 for PNR enquiry. "
        "Press 2 for Train running status. "
        "Press 3 for Train schedule. "
        "Press 0 to exit."
    )
    vr.append(options)

    # FIX 3: Added fallback redirect — previously the call would silently drop
    # if the user didn't press anything within the timeout period
    vr.say("No input received. Returning to main menu.")
    vr.redirect("/voice")       # <-- this line was completely missing

    return Response(str(vr), media_type="application/xml")

# ================================
# Option Handler
# ================================

@app.api_route("/handle-option", methods=["GET", "POST"])
async def handle_option(request: Request):
    try:
        form = await request.form()
        logging.info(f"Menu selection: {form}")

        selection = form.get("Digits")
        vr = VoiceResponse()

        if selection == "1":
            gather = Gather(num_digits=10, action="/get-pnr", method="POST")
            gather.say("Enter your ten digit PNR number.")
            vr.append(gather)
            # FIX 4: Added fallback so call doesn't drop on PNR timeout
            vr.say("No PNR entered. Returning to main menu.")
            vr.redirect("/voice")

        elif selection == "2":
            vr.say("Train is running as per schedule.")
            # FIX 5: Redirect to main_options (English menu) instead of /voice
            # so the user doesn't have to re-select language every time
            vr.redirect("/handle-option-menu")

        elif selection == "3":
            gather = Gather(num_digits=5, action="/get-schedule", method="POST")
            gather.say("Enter five digit train number.")
            vr.append(gather)
            # FIX 6: Added fallback so call doesn't drop on schedule timeout
            vr.say("No train number entered. Returning to main menu.")
            vr.redirect("/voice")

        elif selection == "0":
            vr.say("Thank you for using our service. Goodbye.")
            vr.hangup()

        else:
            vr.say("Wrong option selected.")
            vr.redirect("/voice")

        return Response(str(vr), media_type="application/xml")

    except Exception as e:
        logging.error(f"Option error: {e}")
        return {"error": str(e)}

# ================================
# Helper: Return directly to English main menu
# ================================

# FIX 7: New helper endpoint so internal redirects skip the language selection step
@app.api_route("/handle-option-menu", methods=["GET", "POST"])
async def handle_option_menu(request: Request):
    return await main_options()

# ================================
# PNR Endpoint
# ================================

@app.api_route("/get-pnr", methods=["GET", "POST"])
async def get_pnr(request: Request):
    try:
        form = await request.form()
        logging.info(f"PNR input: {form}")

        pnr_input = form.get("Digits")
        vr = VoiceResponse()

        result = fetch_pnr_details(pnr_input)
        vr.say(result)
        vr.redirect("/handle-option-menu")  # FIX 8: Skip language re-selection

        return Response(str(vr), media_type="application/xml")

    except Exception as e:
        logging.error(f"PNR error: {e}")
        return {"error": str(e)}

# ================================
# Train Schedule
# ================================

@app.api_route("/get-schedule", methods=["GET", "POST"])
async def get_schedule(request: Request):
    try:
        form = await request.form()
        logging.info(f"Train number input: {form}")

        train_input = form.get("Digits")
        vr = VoiceResponse()

        result = fetch_train_schedule(train_input)
        vr.say(result)
        vr.redirect("/handle-option-menu")  # FIX 9: Skip language re-selection

        return Response(str(vr), media_type="application/xml")

    except Exception as e:
        logging.error(f"Schedule error: {e}")
        return {"error": str(e)}
