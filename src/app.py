from http import HTTPStatus
from flask import Flask, jsonify, request
from pprint import pprint

from .modules.lunchSearchDemoSDK.lunchSearchDemoSDK import lunchSearchDemoSDK
import unique_sdk

from dotenv import load_dotenv
import os

load_dotenv()
endpoint_secret = os.getenv("ENDPOINT_SECRET")

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World"

@app.route("/webhook", methods=["POST"])
def webhook():
    event = None
    payload = request.data

    sig_header = request.headers.get("X-Unique-Signature")
    timestamp = request.headers.get("X-Unique-Created-At")

    if not sig_header or not timestamp:
        print("⚠️  Webhook signature or timestamp headers missing.")
        return jsonify(success=False), HTTPStatus.BAD_REQUEST

    try:
        event = unique_sdk.Webhook.construct_event(
            payload, sig_header, timestamp, endpoint_secret
        )
    except unique_sdk.SignatureVerificationError as e:
        print("⚠️  Webhook signature verification failed. " + str(e))
        return jsonify(success=False), HTTPStatus.BAD_REQUEST

    pprint(event)

    if event and event["event"] == "unique.chat.external-module.chosen":
        modulePayload = event["payload"]
        pprint(modulePayload)
        if modulePayload["name"] == "LunchSearch":
            lunchSearchDemoSDK(event)
    return "OK", 200
