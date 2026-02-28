from flask import Flask, jsonify
from py5paisa import FivePaisaClient
from pyotp import TOTP

app = Flask(__name__)

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

client = None

def get_client():
    global client
    if client is None:
        totp = TOTP(totp_secret).now()
        client = FivePaisaClient(cred=credentials)
        client.get_totp_session(client_code, totp, mpin)
        print("✅ 5Paisa Login Successful")
    return client

@app.route("/api/positions", methods=["GET"])
def get_positions():
    try:
        cl = get_client()
        positions_raw = cl.positions()

        processed = []

        for pos in positions_raw:
            netqty = int(pos.get("NetQty", 0))

            buyval = float(pos.get("BuyValue", 0))
            sellval = float(pos.get("SellValue", 0))
            netval = buyval - sellval

            processed.append({
                "id": pos.get("ScripCode"),
                "symbol": pos.get("ScripName"),
                "m2m": float(pos.get("MTOM", 0)),
                "pnl": float(pos.get("BookedPL", 0)),
                "atpnl": float(pos.get("MTOM", 0)),
                "realpl": float(pos.get("BookedPL", 0)),
                "unrealpl": 0,
                "netqty": netqty,
                "ltp": float(pos.get("LTP", 0)),
                "buyqty": pos.get("BuyQty", 0),
                "sellqty": pos.get("SellQty", 0),
                "buyval": buyval,
                "sellval": sellval,
                "netval": netval,   
                "bavg": pos.get("BuyAvgRate", 0),
                "savg": pos.get("SellAvgRate", 0),
                "state": pos.get("PositionType", ""),
                "direction": "LONG" if netqty > 0 else ("SHORT" if netqty < 0 else "NEUTRAL"),
                "type": pos.get("ProductType", ""),
                "category": pos.get("Exchange", ""),
                "broker": "5Paisa",
                "overqty": pos.get("DeliveryQty", 0),
                "multiplier": pos.get("Multiplier", 1),
                "exch": pos.get("Exchange", ""),
                "brexch": pos.get("Exchange", ""),
                "brsymbol": pos.get("ScripName", ""),
                "day": "DAY",
                "platform": "WEB",
                "accid": client_code,
                "pseacc": "Default",
                "trdacc": client_code
            })


        return jsonify(processed)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
