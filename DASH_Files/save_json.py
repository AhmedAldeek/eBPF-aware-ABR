from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

SAVE_PATH = "/home/kali/session_metrics.json"

@app.route('/save_metrics', methods=['POST'])
def save_metrics():
    data = request.json

    try:
        with open(SAVE_PATH, "w") as f:
            json.dump(data, f, indent=2)
        return jsonify({"status": "saved", "path": SAVE_PATH})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    print(f"📥 JSON Saver listening on http://0.0.0.0:9100")
    print(f"📄 Saving to: {SAVE_PATH}")
    app.run(host="0.0.0.0", port=9100)
