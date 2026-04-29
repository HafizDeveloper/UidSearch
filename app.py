from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# --- AUTH CONFIGURATION ---
ANDROID_ID = "96a2a6c1a6c9dce6"
VERSION = "OB53"
cached_token = None

def get_session():
    global cached_token
    if cached_token:
        return cached_token
    
    # Auto-login engine
    url = "https://loginbp.ggpolarbear.com/MajorLogin"
    payload = {
        "device_id": ANDROID_ID,
        "android_id": ANDROID_ID,
        "release_version": VERSION,
        "client_version": "1.123.10"
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            cached_token = res.json().get("token") or res.json().get("access_token")
            return cached_token
    except:
        return None

# --- HOME INTERFACE (FOLLOWING YOUR SCREENSHOT FORMAT) ---
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "available_regions": ["SG"],
        "endpoint": "/gen?name=UID",
        "message": "HafizX Player Search API",
        "note": "Enter UID to fetch player nickname and basic info."
    })

# --- CORE SEARCH ENGINE ---
@app.route('/gen', methods=['GET'])
def search_id():
    uid = request.args.get('name')
    
    if not uid:
        return jsonify({"status": "Error", "msg": "Please provide a UID"}), 400

    token = get_session()
    headers = {
        "Authorization": f"Bearer {token}",
        "ReleaseVersion": VERSION,
        "X-GA": "v1 1"
    }
    
    try:
        # Target: Fetching nickname and basic data
        api_url = "https://clientbp.ggpolarbear.com/GetPlayerBriefInfo"
        response = requests.post(api_url, data={"account_id": uid}, headers=headers, timeout=5)
        
        if response.status_code == 200:
            p = response.json()
            return jsonify({
                "status": "Success",
                "data": {
                    "uid": uid,
                    "nickname": p.get("nickname", "Not Found"),
                    "level": p.get("level", "0"),
                    "region": "Singapore"
                }
            })
        else:
            return jsonify({"status": "Failed", "msg": "Connection error"}), response.status_code

    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500

if __name__ == '__main__':
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['JSON_SORT_KEYS'] = False
    app.run(host='0.0.0.0', port=5000, debug=True)