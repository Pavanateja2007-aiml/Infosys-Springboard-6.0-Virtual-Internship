# ==========================================
# MULTI-LANGUAGE + ACCESSIBILITY IVR
# SINGLE FILE IMPLEMENTATION
# ==========================================

from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather

app = FastAPI()

# -------------------------------
# LANGUAGE CONFIG
# -------------------------------
LANGUAGES = {
    "1": {"code": "en-IN", "voice": "Polly.Joanna", "name": "English"},
    "2": {"code": "hi-IN", "voice": "Polly.Aditi", "name": "Hindi"},
    "3": {"code": "te-IN", "voice": "Polly.Raveena", "name": "Telugu"}
}

# Store user language (use DB in production)
user_language = {}


# ==========================================
# 1. ENTRY POINT (LANGUAGE SELECTION)
# ==========================================
@app.post("/voice")
async def voice():
    response = VoiceResponse()

    gather = Gather(num_digits=1, action="/set-language", method="POST")

    gather.say("Welcome to Smart Railway IVR.")
    gather.say("Press 1 for English.")
    gather.say("Press 2 for Hindi.")
    gather.say("Press 3 for Telugu.")

    response.append(gather)

    return Response(str(response), media_type="application/xml")


# ==========================================
# 2. SET LANGUAGE
# ==========================================
@app.post("/set-language")
async def set_language(request: Request):
    form = await request.form()
    choice = form.get("Digits", "1")

    lang_data = LANGUAGES.get(choice, LANGUAGES["1"])
    user_language["current"] = lang_data

    response = VoiceResponse()

    # SSML Welcome
    ssml_text = f"""
    <speak>
        <prosody rate="medium" pitch="medium">
            You selected {lang_data["name"]}.
            <break time="500ms"/>
            Please tell your request.
        </prosody>
    </speak>
    """

    gather = Gather(
        input="speech",
        action="/process",
        method="POST",
        language=lang_data["code"],
        speechTimeout="auto"
    )

    gather.say(ssml_text, voice=lang_data["voice"], language=lang_data["code"])
    response.append(gather)

    return Response(str(response), media_type="application/xml")


# ==========================================
# 3. PROCESS SPEECH INPUT
# ==========================================
@app.post("/process")
async def process(request: Request):
    form = await request.form()
    speech_text = form.get("SpeechResult", "")

    lang_data = user_language.get("current", LANGUAGES["1"])

    response = VoiceResponse()

    # SSML Response
    ssml_response = f"""
    <speak>
        <prosody rate="medium" pitch="medium">
            You said: {speech_text}
            <break time="500ms"/>
            We are processing your request.
        </prosody>
    </speak>
    """

    response.say(
        ssml_response,
        voice=lang_data["voice"],
        language=lang_data["code"]
    )

    # Enable Real-Time Transcription
    response.record(
        transcribe=True,
        transcribe_callback="/transcription",
        max_length=30
    )

    # Loop back
    response.redirect("/voice")

    return Response(str(response), media_type="application/xml")


# ==========================================
# 4. TRANSCRIPTION CALLBACK
# ==========================================
@app.post("/transcription")
async def transcription(request: Request):
    form = await request.form()

    transcription_text = form.get("TranscriptionText", "")
    print("Live Transcription:", transcription_text)

    return "OK"