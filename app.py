from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# --- KONFIGURASI ---
VERSION = "OB53"
current_token = "Bearer eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ.eyJhY2NvdW50X2lkIjoxNTQyODE1NTE2Niwibmlja25hbWUiOiJmeXBUV2xzSld3SlVEbFZXIiwibm90aV9yZWdpb24iOiJTRyIsImxvY2tfcmVnaW9uIjoiU0ciLCJleHRlcm5hbF9pZCI6ImZiYjE4YTY2MTBjNDRlNjY0NWRkZWI0MDVlMTVlY2JjIiwiZXh0ZXJuYWxfdHlwZSI6NCwicGxhdF9pZCI6MSwiY2xpZW50X3ZlcnNpb24iOiIxLjEyMy4xMCIsImVtdWxhdG9yX3Njb3JlIjoxMDAsImlzX2VtdWxhdG9yIjp0cnVlLCJjb3VudHJ5X2NvZGUiOiJNWSIsImV4dGVybmFsX3VpZCI6NDcyNzEwMzM4OCwicmVnX2F2YXRhciI6MTAyMDAwMDA3LCJzb3VyY2UiOjQsImxvY2tfcmVnaW9uX3RpbWUiOjE3NzY0NDM3NzcsImNsaWVudF90eXBlIjoyLCJzaWduYXR1cmVfbWQ1IjoiMWFjNGI4MGVjZjA0NzhhNDQyMDNiZjhmYWM2MTIwZjUiLCJ1c2luZ192ZXJzaW9uIjoxLCJyZWxlYXNlX2NoYW5uZWwiOiIzcmRfcGFydHkiLCJyZWxlYXNlX3ZlcnNpb24iOiJPQjUzIiwiZXhwIjoxNzc3NTQ1Njc4fQ.gixuhEwe_TfsENv4tQrHNlSQdDAa_UiDAXSFvMdFAWU"

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "Online",
        "region": "Singapore",
        "service": "Player ID Search"
    })

# --- ENDPOINT CARI PLAYER (SG ONLY) ---
@app.route('/gen', methods=['GET'])
def get_player():
    global current_token
    uid = request.args.get('name')
    
    if not uid:
        return jsonify({"status": "Error", "msg": "Sila masukkan ?name=UID"}), 400

    headers = {
        "Authorization": f"Bearer {current_token}",
        "ReleaseVersion": VERSION,
        "X-GA": "v1 1",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        # Request ke Garena Singapore
        url = "https://clientbp.ggpolarbear.com/GetPlayerBriefInfo"
        res = requests.post(url, data=f"account_id={uid}", headers=headers, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            name = data.get("nickname")

            if name:
                return jsonify({
                    "status": "Success",
                    "data": {
                        "uid": uid,
                        "name": name,
                        "level": data.get("level", "0"),
                        "region": "Singapore"
                    }
                })
            else:
                return jsonify({"status": "Failed", "msg": "ID tidak dijumpai di Server SG"}), 404
        
        elif res.status_code == 401:
            return jsonify({"status": "Error", "msg": "Token sudah basi. Sila update token baru."}), 401
        else:
            return jsonify({"status": "Error", "msg": f"Garena Error {res.status_code}"}), res.status_code

    except Exception as e:
        return jsonify({"status": "Error", "msg": "Connection timeout"}), 500

# --- PINTU RAHSIA UPDATE TOKEN ---
@app.route('/update', methods=['GET'])
def update():
    global current_token
    new_t = request.args.get('t')
    if new_t:
        current_token = new_t
        return "Token Updated, Hafiz! Dah boleh test cari ID balik."
    return "Masukkan token kat ?t="

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)