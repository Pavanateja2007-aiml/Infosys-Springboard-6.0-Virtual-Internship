# ================================
# IRCTC IVR SYSTEM - FASTAPI
# ================================

from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Railway IVR System")

# ================================
# Twilio Credentials (Environment)
# ================================

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_PHONE")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# ================================
# Utility Functions
# ================================

def load_data():
    try:
        with open("irctc.json") as file:
            return json.load(file)
    except:
        return {}

def fetch_pnr_details(pnr_number: str):
    data = load_data()
    ticket = data.get(pnr_number)

    if ticket:
        return f"Ticket status is {ticket['status']}. Coach {ticket['coach']}, Seat {ticket['seat']}."
    return "Sorry. PNR number not found."

def fetch_train_schedule(train_number: str):
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
    return {"status": "IVR Server Active"}


# ================================
# Call Start
# ================================

@app.api_route("/start", methods=["GET", "POST"])
async def start_call():

    vr = VoiceResponse()

    gather = Gather(num_digits=1, action="/select-language", method="POST")

    gather.say(
        "Welcome to Railway Information System. "
        "Press 1 for English. "
        "Press 2 for Hindi."
    )

    vr.append(gather)
    vr.say("No input detected. Goodbye.")
    vr.hangup()

    return Response(str(vr), media_type="application/xml")


# ================================
# Language Selection
# ================================

@app.api_route("/select-language", methods=["GET", "POST"])
async def select_language(request: Request):

    form = await request.form()
    choice = form.get("Digits")

    vr = VoiceResponse()

    if choice == "1":
        return await main_menu()

    elif choice == "2":
        vr.say("Hindi service coming soon.")
        vr.hangup()

    else:
        vr.say("Invalid selection.")
        vr.redirect("/start")

    return Response(str(vr), media_type="application/xml")


# ================================
# Main Menu
# ================================

async def main_menu():

    vr = VoiceResponse()

    gather = Gather(num_digits=1, action="/handle-option", method="POST")

    gather.say(
        "Press 1 for PNR enquiry. "
        "Press 2 for Train running status. "
        "Press 3 for Train schedule. "
        "Press 0 to exit."
    )

    vr.append(gather)

    return Response(str(vr), media_type="application/xml")


# ================================
# Handle Options
# ================================

@app.api_route("/handle-option", methods=["GET", "POST"])
async def handle_option(request: Request):

    form = await request.form()
    selection = form.get("Digits")

    vr = VoiceResponse()

    if selection == "1":

        gather = Gather(num_digits=10, action="/get-pnr", method="POST")
        gather.say("Enter your ten digit PNR number.")
        vr.append(gather)

    elif selection == "2":

        vr.say("Train is running as per schedule.")
        vr.redirect("/start")

    elif selection == "3":

        gather = Gather(num_digits=5, action="/get-schedule", method="POST")
        gather.say("Enter five digit train number.")
        vr.append(gather)

    elif selection == "0":

        vr.say("Thank you for using railway information system.")
        vr.hangup()

    else:

        vr.say("Wrong option selected.")
        vr.redirect("/start")

    return Response(str(vr), media_type="application/xml")


# ================================
# PNR Handler
# ================================

@app.api_route("/get-pnr", methods=["GET", "POST"])
async def get_pnr(request: Request):

    form = await request.form()
    pnr_input = form.get("Digits")

    vr = VoiceResponse()

    result = fetch_pnr_details(pnr_input)

    vr.say(result)
    vr.redirect("/start")

    return Response(str(vr), media_type="application/xml")


# ================================
# Train Schedule
# ================================

@app.api_route("/get-schedule", methods=["GET", "POST"])
async def get_schedule(request: Request):

    form = await request.form()
    train_input = form.get("Digits")

    vr = VoiceResponse()

    result = fetch_train_schedule(train_input)

    vr.say(result)
    vr.redirect("/start")

    return Response(str(vr), media_type="application/xml")


# ================================
# Outbound Call
# ================================

@app.get("/make-call")
async def make_call():

    call = client.calls.create(
        to=os.getenv("USER_PHONE"),
        from_=TWILIO_NUMBER,
        url=os.getenv("NGROK_URL") + "/start"
    )

    return {"call_id": call.sid, "status": call.status}