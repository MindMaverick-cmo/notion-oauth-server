from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

CLIENT_ID = os.environ.get("NOTION_CLIENT_ID")
CLIENT_SECRET = os.environ.get("NOTION_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI")

# Путь к файлу токена
TOKEN_FILE = "storage/token.json"

def save_token(data):
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f)

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return None

@app.route("/")
def index():
    return "✅ Notion OAuth Redirect Server is running!"

@app.route("/callback")
def oauth_callback():
    code = request.args.get("code")
    if not code:
        return "Missing code", 400

    response = requests.post(
        "https://api.notion.com/v1/oauth/token",
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code != 200:
        return f"Error getting token: {response.text}", 400

    token_data = response.json()
    save_token(token_data)
    return jsonify(token_data)

@app.route("/token/latest", methods=["GET"])
def get_latest_token():
    token = load_token()
    if not token:
        return jsonify({"error": "No token found"}), 404
    return jsonify(token)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    # Это нужно, чтобы gunicorn знал, как запустить приложение
app = app

