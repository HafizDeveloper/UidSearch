from flask import Flask, jsonify, request
import requests
import re

app = Flask(__name__)

# --- CONFIG ---
VERSION = "OB53"
current_token = ""

def encode_varint(n):
    """Fungsi untuk tukar UID kepada format Protobuf Varint"""
    data = bytearray()
    while n >= 0x80:
        data.append((n & 0x7f) | 0x80)
        n >>= 7
    data.append(n & 0x7f)
    return data

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "Online",
        "service": "HafizX Search API",
        "mode": "Protobuf Scraper"
    })

@app.route('/gen', methods=['GET'])
def get_player():
    global current_token
    # 1. Define UID dari parameter URL (?name=UID)
    uid = request.args.get('name')
    
    if not uid:
        return jsonify({"status": "Error", "msg": "Sila masukkan ?name=UID"}), 400

    # 2. Headers ikut sebiji data mitmweb kau
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
        
        # 3. Bina Binary Payload (Member 1: account_id)
        # \x08 adalah Tag untuk Field 1 dalam Protobuf
        payload = b'\x08' + encode_varint(int(uid))
        
        # 4. Hantar Request ke Garena
        res = requests.post(url, data=payload, headers=headers, timeout=10)
        
        # Log untuk debug kat Render
        print(f"DEBUG: UID {uid} | Status {res.status_code}")

        if res.status_code == 200:
            raw_data = res.content
            
            # 5. Cari Nickname (Member 3) guna Regex
            # Kita cari pattern: Tag \x1a (Field 3) + Length + Nama
            match = re.search(rb'\x1a.([A-Za-z0-9\s\u1D00-\u1D7F]{3,20})', raw_data)
            
            if match:
                nickname = match.group(1).decode('utf-8', errors='ignore').strip()
                return jsonify({
                    "status": "Success",
                    "data": {
                        "uid": uid,
                        "name": nickname
                    }
                })
            else:
                return jsonify({
                    "status": "Error", 
                    "msg": "Nama tak jumpa dalam data binari",
                    "debug": str(raw_data[:50])
                }), 404
        
        return jsonify({
            "status": "Error", 
            "msg": f"Garena Error {res.status_code}",
            "raw": res.text
        }), res.status_code

    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500

@app.route('/update', methods=['GET'])
def update():
    global current_token
    t = request.args.get('t')
    if t:
        current_token = t
        return "Token Updated!"
    return "Guna: /update?t=TOKEN"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)