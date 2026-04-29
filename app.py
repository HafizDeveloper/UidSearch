from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
ANDROID_ID = "96a2a6c1a6c9dce6"
VERSION = "OB53"
cached_token = None

def get_session_token():
    global cached_token
    if cached_token:
        return cached_token
    
    # Automatic login using your Android ID
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

# --- HOME PAGE (MATCHING YOUR IMAGE FORMAT) ---
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "available_regions": ["SG"],
        "endpoint": "/check?name=UID",
        "message": "Enter Uid ",
        "note": "Real-time Garena Singapore database synchronization enabled."
    })

# --- SEARCH ENDPOINT ---
@app.route('/gen', methods=['GET'])
def search_player():
    target_uid = request.args.get('name')
    
    if not target_uid:
        return jsonify({
            "status": "Error", 
            "msg": "Missing parameter: please use ?name=UID"
        }), 400

    token = get_session_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "ReleaseVersion": VERSION,
        "X-GA": "v1 1"
    }
    
    try:
        # Fetch player info from Garena SG
        api_url = "https://clientbp.ggpolarbear.com/GetPlayerBriefInfo"
        response = requests.post(api_url, data=f"account_id={target_uid}", headers=headers, timeout=7)
        
        # Handle Expired Session
        if response.status_code == 401:
            global cached_token
            cached_token = None # Clear cache to force re-login on next try
            return jsonify({"status": "Failed", "msg": "Session expired, please refresh"}), 401

        if response.status_code == 200:
            data = response.json()
            return jsonify({
                "status": "Success",
                "data": {
                    "uid": target_uid,
                    "nickname": data.get("nickname", "Not Found"),
                    "level": data.get("level", "0"),
                    "region": "Singapore"
                }
            })
        else:
            return jsonify({"status": "Failed", "msg": "Garena Server Error"}), response.status_code

    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500

if __name__ == '__main__':
    # Pretty-print JSON like in your screenshot
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['JSON_SORT_KEYS'] = False
    app.run(host='0.0.0.0', port=5000, debug=True)