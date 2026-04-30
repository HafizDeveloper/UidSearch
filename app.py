from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# --- KONFIGURASI ASAS ---
VERSION = "OB53"
# Token ini akan disimpan dalam memori server Render. 
# Hafiz kena update guna link /update lepas push ke Render.
current_token = ""

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "Online",
        "region": "Singapore",
        "service": "HafizX Player Search API",
        "version": VERSION
    })

# --- ENDPOINT UTAMA: CARI PLAYER ID ---
@app.route('/gen', methods=['GET'])
def get_player():
    global current_token
    uid = request.args.get('name')
    
    # Check kalau Hafiz lupa letak ?name=UID
    if not uid:
        return jsonify({"status": "Error", "msg": "Sila masukkan ?name=UID"}), 400

    # Header yang diperlukan oleh server Garena
    headers = {
        "Authorization": f"Bearer {current_token}",
        "ReleaseVersion": VERSION,
        "X-GA": "v1 1",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; MSI Build/SKR1.210119.001)"
    }

    try:
        url = "https://clientbp.ggpolarbear.com/GetPlayerBriefInfo"
        
        # Payload dalam format form-urlencoded (Kunci kepada Error 500 tadi)
        payload = {'account_id': str(uid)} 
        
        # Hantar request ke Garena
        res = requests.post(url, data=payload, headers=headers, timeout=10)
        
        # Log untuk Hafiz check kat Dashboard Render kalau ada error
        print(f"DEBUG: UID {uid} | Status {res.status_code} | Response: {res.text}")

        if res.status_code == 200:
            data = res.json()
            nickname = data.get("nickname")

            if nickname:
                return jsonify({
                    "status": "Success",
                    "data": {
                        "uid": uid,
                        "name": nickname,
                        "level": data.get("level", "0"),
                        "exp": data.get("exp", "0"),
                        "region": "Singapore"
                    }
                })
            else:
                return jsonify({
                    "status": "Failed", 
                    "msg": "No Blacklist Account", 
                    "detail": "ID tidak dijumpai di Server SG"
                }), 404
        
        elif res.status_code == 401:
            return jsonify({
                "status": "Error", 
                "msg": "Token basi atau salah. Sila update token baru guna /update."
            }), 401
            
        else:
            return jsonify({
                "status": "Error", 
                "msg": f"Garena Error {res.status_code}",
                "raw_response": res.text
            }), res.status_code

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return jsonify({"status": "Error", "msg": "Server Garena sibuk atau timeout"}), 500

# --- SISTEM UPDATE TOKEN (UNTUK PEMALAS) ---
# Guna link ni: https://apisearchui.onrender.com/update?t=TOKEN_BARU
@app.route('/update', methods=['GET'])
def update():
    global current_token
    new_t = request.args.get('t')
    if new_t:
        current_token = new_t
        return "<h3>Token SG Berjaya Diupdate!</h3><p>Hafiz dah boleh sambung check ID sekarang.</p>"
    return "Hafiz, kau lupa masukkan token kat hujung link tu (?t=TOKEN)"

if __name__ == '__main__':
    # Set host ke 0.0.0.0 supaya Render boleh akses
    app.run(host='0.0.0.0', port=5000)