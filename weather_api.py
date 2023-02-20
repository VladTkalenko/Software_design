import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

credentials = open("credentials.txt")
# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = credentials.readline().strip()

# you can get API keys for free here - https://api-docs.pgamerx.com/
RSA_API_KEY = credentials.readline().strip()

app = Flask(__name__)


def generate_weather(json_data):
    url = "http://api.weatherapi.com/v1/current.json?"

    json_data["key"] = RSA_API_KEY
    json_data.pop("token")
    json_data.pop("requested_name")

    for (key, value) in json_data.items():
        url = url + key + "=" + value + "&"
    url = url[:-1]

    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: Python Saas.</h2></p>"


@app.route(
    "/content/api/v1/integration/generate",
    methods=["POST"],
)
def weather_endpoint():
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    requested_name = json_data.get("requested_name")

    response = generate_weather(json_data)
    timestamp = dt.datetime.now()
    date = dt.date.today()
    date = date.strftime("%d/%m/%Y")
    location = response["location"]
    weather = response["current"]


    result = {
        "requested_name": requested_name,
        "timestamp": timestamp,
        "location": location,
        "date": date,
        "weather": weather,
    }

    return result
