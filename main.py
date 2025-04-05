from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__)

CLIENT_ID = os.environ.get("NOTION_CLIENT_ID")
CLIENT_SECRET = os.environ.get("NOTION_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI")

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

    return jsonify(response.json())

# 👇 ЭТО ДОБАВЛЯЕМ 👇
@app.route('/openapi.yaml')
def serve_openapi():
    return send_from_directory('.', 'openapi.yaml', mimetype='text/yaml')

@app.route('/ai-plugin.json')
def serve_ai_plugin():
    return send_from_directory('.', 'ai-plugin.json', mimetype='application/json')
# 👆 ЭТО ДОБАВЛЯЕМ 👆

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
