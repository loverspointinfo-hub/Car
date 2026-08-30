from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

URL = "https://www.smcinsurance.com/central/centralcall/CallReqWithHeader"

HEADERS = {
    "content-type": "application/json;charset=UTF-8",
    "accept": "application/json, text/plain, */*",
    "origin": "https://www.smcinsurance.com",
    "referer": "https://www.smcinsurance.com/rto/vehicle-owner-details",
    "x-requested-with": "XMLHttpRequest",
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/148.0.0.0 Safari/537.36"
    ),
    "cookie": (
        "_gcl_au=1.1.1438248880.1779788708; "
        "_gid=GA1.2.1153916911.1779959297; "
        "_ga=GA1.2.1149128124.1779788709; "
        "MCBC=0VqWZYKix5Xvpi%2BqafMsmM8VEAsoffaCxor1evU5WsU%3D%3A"
        "62f9089e5fd48fc8ff5e8cc44401651e9ae1df4b992a8a046081f29f60afc6ea"
    )
}

@app.route('/vehicle', methods=['GET'])
def vehicle_lookup():
    vehicle_number = request.args.get('number', '').strip().upper()
    if not vehicle_number:
        return jsonify({
            "credit_top": "@HYPERMX7",
            "status": "error",
            "error": "Vehicle number required (e.g., /vehicle?number=DL1ABC1234)",
            "credit_bottom": "@HYPERMX7"
        }), 400

    payload = {
        "URL": "GetVaahanDetailsByVehicleNo",
        "Props": [vehicle_number],
        "Token": ""
    }

    try:
        r = requests.post(URL, headers=HEADERS, json=payload, timeout=30)
        try:
            data = r.json()
        except Exception:
            return jsonify({
                "credit_top": "@HYPERMX7",
                "status": "error",
                "error": "Invalid response from server",
                "credit_bottom": "@HYPERMX7"
            }), 502

        rd = data.get("response", {})
        sc = data.get("statusCode", 500)
        if isinstance(rd, dict):
            rd.pop("transKey", None)

        if sc != 200 or not rd:
            return jsonify({
                "credit_top": "@HYPERMX7",
                "status": "error",
                "error": f"No data found (status {sc}). Check vehicle number.",
                "credit_bottom": "@HYPERMX7"
            }), 404

        # Lowercase keys and remove junk values
        d = {k.lower(): v for k, v in rd.items() if v and str(v).strip() not in ("", "NA", "None", "0", "null")}

        response = {
            "credit_top": "@HYPERMX7",
            "status": "success",
            "vehicle_number": vehicle_number,
            "data": d,
            "credit_bottom": "@HYPERMX7"
        }
        return jsonify(response)

    except requests.exceptions.Timeout:
        return jsonify({
            "credit_top": "@HYPERMX7",
            "status": "error",
            "error": "Request timed out. Server may be slow.",
            "credit_bottom": "@HYPERMX7"
        }), 504
    except requests.exceptions.RequestException as e:
        return jsonify({
            "credit_top": "@HYPERMX7",
            "status": "error",
            "error": f"Network error: {e}",
            "credit_bottom": "@HYPERMX7"
        }), 502
    except Exception as e:
        return jsonify({
            "credit_top": "@HYPERMX7",
            "status": "error",
            "error": str(e),
            "credit_bottom": "@HYPERMX7"
        }), 500

@app.route('/')
def home():
    return jsonify({
        "credit_top": "@HYPERMX7",
        "app": "Vehicle Owner Details API (SMC Insurance)",
        "usage": "/vehicle?number=DL1ABC1234",
        "note": "Cookie may expire; renew from SMC insurance website if needed.",
        "credit_bottom": "@HYPERMX7"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)