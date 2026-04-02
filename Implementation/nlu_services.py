# ================================
# NLU + AI SERVICE LAYER
# ================================

import requests
from textblob import TextBlob

# -------------------------------
# CONFIG (Replace with your keys)
# -------------------------------
AZURE_CLU_ENDPOINT = "https://<your-endpoint>.cognitiveservices.azure.com/"
AZURE_CLU_KEY = "YOUR_AZURE_KEY"

DIALOGFLOW_PROJECT_ID = "your-project-id"
DIALOGFLOW_URL = f"https://dialogflow.googleapis.com/v2/projects/{DIALOGFLOW_PROJECT_ID}/agent/sessions/123:detectIntent"

# -------------------------------
# INTENT DETECTION (Azure CLU)
# -------------------------------
def detect_intent_azure(text):
    url = AZURE_CLU_ENDPOINT + "language/:analyze-conversations?api-version=2022-10-01-preview"

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_CLU_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "kind": "Conversation",
        "analysisInput": {
            "conversationItem": {
                "id": "1",
                "text": text,
                "modality": "text",
                "language": "en"
            }
        },
        "parameters": {
            "projectName": "ivr-project",
            "deploymentName": "production"
        }
    }

    response = requests.post(url, headers=headers, json=body)
    return response.json()


# -------------------------------
# DIALOGFLOW CX (OPTIONAL)
# -------------------------------
def detect_intent_dialogflow(text):
    headers = {
        "Authorization": "Bearer YOUR_GOOGLE_TOKEN"
    }

    body = {
        "queryInput": {
            "text": {
                "text": text,
                "languageCode": "en"
            }
        }
    }

    response = requests.post(DIALOGFLOW_URL, headers=headers, json=body)
    return response.json()


# -------------------------------
# SENTIMENT ANALYSIS
# -------------------------------
def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity < -0.3:
        return "negative"
    elif polarity > 0.3:
        return "positive"
    else:
        return "neutral"


# -------------------------------
# MULTI-LANGUAGE SUPPORT
# -------------------------------
def get_language_voice(lang):
    voices = {
        "en": "Polly.Joanna",
        "hi": "Polly.Aditi",
        "te": "Polly.Raveena"
    }
    return voices.get(lang, "Polly.Joanna")