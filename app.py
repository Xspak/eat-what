import os
import random
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 高德 Web服务 Key
AMAP_KEY = os.environ.get("AMAP_KEY", "在这里填入你的高德Web服务Key")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/nearby", methods=["POST"])
def nearby():
    data = request.get_json(force=True)
    try:
        lng = float(data["lng"])
        lat = float(data["lat"])
        radius = int(data.get("radius", 2000))
        count = int(data.get("count", 9))
        poi_types = data.get("types", "050100")
    except (KeyError, TypeError, ValueError):
        return jsonify({"ok": False, "error": "参数错误"}), 400

    if not (1 <= count <= 30):
        return jsonify({"ok": False, "error": "数量需在 1~30 之间"}), 400
    if not (100 <= radius <= 50000):
        return jsonify({"ok": False, "error": "半径需在 100~50000 米之间"}), 400

    url = "https://restapi.amap.com/v3/place/around"
    params = {
        "key": AMAP_KEY,
        "location": f"{lng},{lat}",
        "radius": radius,
        "types": poi_types,
        "offset": 25,
        "page": 1,
        "extensions": "base",
        "sortrule": "distance",
    }

    try:
        resp = requests.get(url, params=params, timeout=8)
        result = resp.json()
    except Exception as e:
        return jsonify({"ok": False, "error": f"请求高德失败: {e}"}), 502

    if result.get("status") != "1":
        return jsonify({
            "ok": False,
            "error": result.get("info", "高德接口返回错误")
        }), 502

    pois = result.get("pois", []) or []
    if not pois:
        return jsonify({"ok": False, "error": "附近没搜到餐厅，试试扩大半径或换个类别"}), 404

    seen = set()
    cleaned = []
    for p in pois:
        name = (p.get("name") or "").strip()
        if not name or name in seen:
            continue
        seen.add(name)
        cleaned.append({
            "name": name,
            "address": p.get("address") or "",
            "distance": p.get("distance") or "",
        })

    if not cleaned:
        return jsonify({"ok": False, "error": "附近没搜到有效餐厅"}), 404

    picked = random.sample(cleaned, min(count, len(cleaned)))
    return jsonify({"ok": True, "restaurants": picked})


if __name__ == "__main__":
    # 开启 HTTPS，使用你生成的证书
    ssl_context = ('cert.pem', 'key.pem') if os.path.exists('cert.pem') else None
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        ssl_context=ssl_context
    )