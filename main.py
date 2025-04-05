
from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

CLIENT_ID = os.environ.get("NOTION_CLIENT_ID")
CLIENT_SECRET = os.environ.get("NOTION_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI")
TOKEN_FILE = "storage/token.json"

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return None

@app.route("/")
def index():
    return "✅ Notion OAuth Redirect Server is running!"

@app.route("/token/latest")
def latest_token():
    token_data = load_token()
    if not token_data:
        return jsonify({"error": "No token found"}), 404
    return jsonify(token_data)

@app.route("/create-page", methods=["POST"])
def create_page():
    token_data = load_token()
    if not token_data or "access_token" not in token_data:
        return jsonify({"error": "Access token not found"}), 401

    access_token = token_data["access_token"]
    notion_url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    payload = request.get_json()
    response = requests.post(notion_url, headers=headers, json=payload)

    if response.status_code != 200:
        return jsonify({"error": response.text}), response.status_code

    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
