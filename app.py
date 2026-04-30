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
    
    if not uid:
        return jsonify({"status": "Error", "msg": "Sila masukkan ?name=UID"}), 400

    headers = {
        "Authorization": f"Bearer {current_token}",
        "ReleaseVersion": VERSION,
        "X-GA": "v1 1",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "okhttp/3.12.1"
    }

    try:
        # Ganti dengan endpoint yang Hafiz jumpa tadi
        url = "https://clientbp.ggpolarbear.com/GetAccountInfoByAccountID"
        
        # Cuba hantar payload macam ni (ikut kesesuaian mitmweb)
        payload = f"account_id={uid}"
        
        res = requests.post(url, data=payload, headers=headers, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            # Biasanya Garena guna 'nickname' atau 'nick_name'
            name = data.get("nickname") or data.get("nick_name")

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
                # Kalau status 200 tapi name kosong, mungkin UID tu salah/tak wujud
                return jsonify({"status": "Failed", "msg": "Player tidak dijumpai"}), 404
        
        return jsonify({
            "status": "Error", 
            "msg": f"Garena Error {res.status_code}",
            "raw": res.text
        }), res.status_code

    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500

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