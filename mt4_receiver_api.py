from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/receive-signal", methods=["GET"])
def receive_signal():
    signal = {
        "type": request.args.get("type"),
        "symbol": request.args.get("symbol"),
        "entry": request.args.get("entry"),
        "sl": request.args.get("sl"),
        "tp": request.args.get("tp")
    }
    print("📥 Nhận tín hiệu:", signal)
    return jsonify({"status": "success", "data": signal}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
