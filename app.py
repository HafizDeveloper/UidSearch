from flask import Flask, jsonify, request
import requests
import re

app = Flask(__name__)

# --- CONFIG ---
VERSION = "OB53"
current_token = ""

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "Online",
        "service": "HafizX Binary Search API",
        "version": VERSION
    })

@app.route('/gen', methods=['GET'])
def get_player():
    global current_token
    uid = request.args.get('name')
    
    if not uid:
        return jsonify({"status": "Error", "msg": "Sila masukkan ?name=UID"}), 400

    # Headers yang diikut sebiji dari raw data mitmweb kau
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
        payload = f"account_id={uid}"
        
        # Hantar request
        res = requests.post(url, data=payload, headers=headers, timeout=10)
        
        # Log status untuk debug di Render
        print(f"DEBUG: UID {uid} | Status {res.status_code}")

        if res.status_code == 200:
            # Guna .content untuk data binari (Protobuf)
            raw_data = res.content 
            
            # Teknik "Regex Scraper" untuk cari nickname dalam data jampi
            # Kita cari string yang ada huruf/nombor dan simbol khas nama (3-20 char)
            # Pattern ini akan cuba cari nama seperti 'MᴜᴍᴍʏEᴠᴀTᴇᴀᴍ'
            match = re.search(rb'[A-Za-z0-9\s\u1D00-\u1D7F]{3,20}', raw_data)
            
            if match:
                # Decode data yang dijumpai ke bentuk teks biasa
                nickname = match.group().decode('utf-8', errors='ignore').strip()
                
                return jsonify({
                    "status": "Success",
                    "data": {
                        "uid": uid,
                        "name": nickname,
                        "method": "Binary Extraction"
                    }
                })
            else:
                return jsonify({
                    "status": "Failed", 
                    "msg": "Nickname tidak dapat dikesan dalam data binari",
                    "debug_raw": str(raw_data[:50]) # Tunjuk 50 huruf pertama untuk check
                }), 404
        
        return jsonify({
            "status": "Error", 
            "msg": f"Garena Error {res.status_code}",
            "raw_hex": res.content.hex()[:100]
        }), res.status_code

    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500

# Endpoint untuk update token SG kau
@app.route('/update', methods=['GET'])
def update():
    global current_token
    t = request.args.get('t')
    if t:
        current_token = t
        return "<h3>Token Berjaya Diupdate!</h3>"
    return "Masukkan token: /update?t=TOKEN"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)