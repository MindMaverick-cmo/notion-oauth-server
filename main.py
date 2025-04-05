from flask import Flask, request, jsonify, send_from_directory
import requests
import os
import json
import base64

app = Flask(__name__)

CLIENT_ID = os.environ.get("NOTION_CLIENT_ID")
CLIENT_SECRET = os.environ.get("NOTION_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI")

TOKEN_FILE = "latest_token.json"

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

    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f)

    return jsonify(token_data)

@app.route("/token/latest", methods=["GET"])
def get_latest_token():
    if not os.path.exists(TOKEN_FILE):
        return jsonify({"error": "No token found"}), 404

    with open(TOKEN_FILE, "r") as f:
        token_data = json.load(f)
    return jsonify({"access_token": token_data.get("access_token")})

@app.route("/token/refresh", methods=["POST"])
def refresh_token():
    if not os.path.exists(TOKEN_FILE):
        return jsonify({"error": "No refresh_token available"}), 404

    with open(TOKEN_FILE, "r") as f:
        token_data = json.load(f)

    refresh_token = token_data.get("refresh_token")
    if not refresh_token:
        return jsonify({"error": "Missing refresh_token"}), 400

    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    headers = {
        "Authorization": "Basic " + base64.b64encode(auth_string.encode()).decode(),
        "Content-Type": "application/json"
    }

    body = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post("https://api.notion.com/v1/oauth/token", headers=headers, json=body)
    if response.status_code != 200:
        return jsonify({"error": "Failed to refresh token", "details": response.text}), 400

    new_token_data = response.json()
    with open(TOKEN_FILE, "w") as f:
        json.dump(new_token_data, f)

    return jsonify(new_token_data)

@app.route('/openapi.yaml')
def serve_openapi():
    return send_from_directory('.', 'openapi.yaml', mimetype='text/yaml')

@app.route('/ai-plugin.json')
def serve_ai_plugin():
    return send_from_directory('.', 'ai-plugin.json', mimetype='application/json')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
