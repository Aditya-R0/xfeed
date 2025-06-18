from flask import Flask, request, jsonify, send_file
import os
import subprocess
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/run-fetch", methods=["POST"])
def run_fetch():
    try:
        print("[server.py] /run-fetch called")

        if "cookie" not in request.files:
            print("[server.py] No cookie.json uploaded")
            return jsonify({"success": False, "error": "No cookie.json file uploaded"}), 400

        cookie_file = request.files["cookie"]
        cookie_path = os.path.join(os.getcwd(), "cookie.json")
        cookie_file.save(cookie_path)
        print(f"[server.py] cookie.json saved at {cookie_path}")

        print("[server.py] Running main.py with cookie path...")
        result = subprocess.run(["python3", "main.py", cookie_path], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"[server.py] main.py error: {result.stderr}")
            return jsonify({"success": False, "error": result.stderr}), 500

        print("[server.py] main.py finished successfully")
        print(f"[server.py] tweets.json location: {os.path.abspath('tweets.json')}")

        return jsonify({"success": True})

    except Exception as e:
        print(f"[server.py] Exception occurred: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/tweets", methods=["GET"])
def get_tweets():
    try:
        print("[server.py] /tweets called")
        return send_file("tweets.json", mimetype="application/json")
    except Exception as e:
        print(f"[server.py] /tweets error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/")
def home():
    print("[server.py] / called")
    return jsonify({"status": "OK"})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
