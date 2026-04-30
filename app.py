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

    # HEADERS: Copy sebiji macam raw data yang kau bagi
    headers = {
        "Host": "clientbp.ggpolarbear.com",
        "User-Agent": "UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
        "Accept": "*/*",
        "Authorization": f"Bearer {current_token}",
        "X-GA": "v1 1",
        "ReleaseVersion": VERSION,
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Unity-Version": "2022.3.47f1",
        "Connection": "keep-alive"
    }

    try:
        url = "https://clientbp.ggpolarbear.com/GetAccountInfoByAccountID"
        
        # Payload format: account_id=UID
        payload = f"account_id={uid}"
        
        res = requests.post(url, data=payload, headers=headers, timeout=10)
        
        # Log untuk check kat Render
        print(f"DEBUG: UID {uid} | Status {res.status_code} | Res: {res.text}")

        if res.status_code == 200:
            data = res.json()
            # Garena bagi data dalam json, kita tarik nickname
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
                return jsonify({"status": "Failed", "msg": "ID Tak Jumpa"}), 404
        
        return jsonify({
            "status": "Error", 
            "msg": f"Garena Error {res.status_code}",
            "raw": res.text
        }), res.status_code

    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500

# Update token guna link: /update?t=TOKEN
@app.route('/update', methods=['GET'])
def update():
    global current_token
    t = request.args.get('t')
    if t:
        current_token = t
        return "Token Updated!"
    return "No Token"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)