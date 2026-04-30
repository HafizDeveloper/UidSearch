from flask import Flask, jsonify, request
import requests
import re
import struct

app = Flask(__name__)

# --- CONFIG ---
VERSION = "OB53"
current_token = ""

def encode_varint(n):
    data = bytearray()
    while n >= 0x80:
        data.append((n & 0x7f) | 0x80)
        n >>= 7
    data.append(n & 0x7f)
    return data

@app.route('/gen', methods=['GET'])
def get_player():
    global current_token
    uid = request.args.get('name')
    
    if not uid:
        return jsonify({"status": "Error", "msg": "Sila masukkan ?name=UID"}), 400

    # HEADERS: Susunan sangat penting untuk Garena
    headers = {
        "Host": "clientbp.ggpolarbear.com",
        "User-Agent": "UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
        "Accept": "*/*",
        "Authorization": f"Bearer {current_token}",
        "X-GA": "v1 1",
        "ReleaseVersion": VERSION,
        "Content-Type": "application/x-www-form-urlencoded", # Kadang-kadang dia nak ni tapi data binari
        "X-Unity-Version": "2022.3.47f1",
        "Connection": "keep-alive"
    }

    try:
        url = "https://clientbp.ggpolarbear.com/GetAccountInfoByAccountID"
        
        # Bina Protobuf Payload: Field 1 (account_id)
        # Garena perlukan format binari yang tepat
        payload = b'\x08' + encode_varint(int(uid))
        
        # Paksa hantar sebagai bytes mentah
        res = requests.post(url, data=payload, headers=headers, timeout=10, verify=True)
        
        print(f"DEBUG: Status {res.status_code} | Raw: {res.content[:20]}")

        if res.status_code == 200:
            raw_data = res.content
            # Guna Regex untuk cari nama dalam jampi
            match = re.search(rb'[A-Za-z0-9\s\u1D00-\u1D7F]{3,20}', raw_data)
            
            if match:
                nickname = match.group().decode('utf-8', errors='ignore').strip()
                return jsonify({
                    "status": "Success",
                    "data": {"uid": uid, "name": nickname}
                })
            else:
                return jsonify({"status": "Error", "msg": "Berhasil tembus tapi nama tak jumpa", "hex": raw_data.hex()[:50]})
        
        # Kalau masih 500, kita return raw data untuk Hafiz check
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
    return "No Token"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)