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

    headers = {
        "Host": "clientbp.ggpolarbear.com",
        "User-Agent": "UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
        "Accept": "*/*",
        "Authorization": f"Bearer {current_token}",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB53",
        "Content-Type": "application/x-protobuf", # Tukar ke protobuf
        "X-Unity-Version": "2022.3.47f1",
        "Connection": "keep-alive"
    }

    try:
        url = "https://clientbp.ggpolarbear.com/GetAccountInfoByAccountID"
        
        # Susunan Protobuf Manual: 
        # \x08 (Field 1, Varint) + Hex UID
        # Ini cara paling dekat nak tiru 'Content-Length: 16' kau
        import struct
        
        def encode_varint(n):
            data = bytearray()
            while n >= 0x80:
                data.append((n & 0x7f) | 0x80)
                n >>= 7
            data.append(n & 0x7f)
            return data

        # Bina payload: Field Number 1 (account_id)
        # Format Protobuf: (field_number << 3) | wire_type
        payload = b'\x08' + encode_varint(int(uid))
        
        # Hantar sebagai data binari mentah
        res = requests.post(url, data=payload, headers=headers, timeout=10)
        
        if res.status_code == 200:
            raw = res.content
            # Guna Regex macam tadi untuk tarik nama dari hasil Protobuf
            import re
            match = re.search(rb'[A-Za-z0-9\s\u1D00-\u1D7F]{3,20}', raw)
            
            if match:
                nickname = match.group().decode('utf-8', errors='ignore').strip()
                return jsonify({
                    "status": "Success",
                    "data": {"uid": uid, "name": nickname}
                })
        
        return jsonify({"status": "Error", "code": res.status_code, "raw": res.text}), res.status_code

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