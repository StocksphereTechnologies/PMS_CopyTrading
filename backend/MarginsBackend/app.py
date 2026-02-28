from flask import Flask, jsonify
from flask_cors import CORS
from py5paisa import FivePaisaClient
from pyotp import TOTP
import json
import pytz
from datetime import datetime

app = Flask(__name__)
CORS(app)

credentials = {
    "APP_NAME": "5P51289806",
    "APP_SOURCE": "24394",
    "USER_ID": "Az60a0QoDVU",
    "PASSWORD": "281221",
    "USER_KEY": "F6AmHZeeTKlCs1naPDTOcuWGqFSySYyh",
    "ENCRYPTION_KEY": "OAJDcyIUwlIaTnOeFGLQfp3MiEkUp3Rl"
}

totp_secret = "GUYTEOBZHAYDMXZVKBDUWRKZ"
mpin = "281221"
client_code = "51289806"

IST = pytz.timezone("Asia/Kolkata")

totp_key = TOTP(totp_secret).now()
client = FivePaisaClient(cred=credentials)

print("Logging in (READ-ONLY MODE)...")
client.get_totp_session(client_code, totp_key, mpin)
print("Login SUCCESS")

@app.route("/margins", methods=["GET"])
def get_margins():
    funds = client.margin()

    print("RAW FUNDS:", funds) 

    if not funds:
        return jsonify({"error": "No margin data received from 5paisa"})


    if isinstance(funds, str):
        funds = json.loads(funds)

    return jsonify(funds)

if __name__ == "__main__":
    app.run(debug=False)
