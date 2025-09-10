import os, json
from flask import Flask, request, jsonify, render_template
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# --- Firebase Service Account JSON (directly embedded) ---
firebase_config = {
  "type": "service_account",
  "project_id": "rover-telemetry",
  "private_key_id": "6081442c29c64514c98d7623e09b6608bc4e46ea",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCtBxN7RfjhvbTI\niSZkWJBKoKp20yDEWgsObmWgjWqhUJN9djk6J/nGiq/+vvcPTsk/YBFnhAioFOTH\nsfT5dC5twWuqY5gAPT5+azPG+DjdEvUg+mCs22XRorzpcFmN+AvFoxj0wQdZnGKM\nM3e2UXZ/EHkrFkg7Mb5QQPwUzQSazKpVGmQbMkLQkN3iSH9rk7+IoI9L70Pl5Uh8\nhGRLxnANcGu3/3woPoJiibuqM0Qldrkc5Z3Kwl73+rhB69W3xY7P2LXvhezWmgfO\nFzlKFszGJtlhBYLlWu6uWUnAIHURrAKEt8tQsYvwDFeMDvkkz9Pu7d+UBJPdZAfp\npH6lQ1nDAgMBAAECggEASEeJctiTFDH8QD1SxV5dwF8HdqXRrVR0A+5IE96faY3Q\nXvuxAkNKyw6KYJ+Dc2iVFx1Zh+WW/CfmPilvzXkkIANJp579EzSCU6sSsQ5mKqvN\nrJ4LHop0KTOTOO0O7AhvWns8ZJnyKRPz8t9ZJdc36fKGu2IOgHPSLZJH+6R9RPCD\nfE/4zLNyNN43aexNAbgNEgQz4toG6f+wJcsdgCNX7Bs0vCZ40Z0JBeFMqoK2fF+x\nptdwa5I92va3CdBF1BucglSd+XQMCayzm6a4Vr7YKZUpZEw32TzyLJvEddzxMQGn\nGl+iIQf3Pu8LvOamviLsSyLN4WuYJBh2GVw6pPEMmQKBgQDpWu5dQAG8n/79xPxx\nXmwlt+CS/JEzM6jtaUcQRFlVGW8wv8YqXmC/bU4z+x9TeB2jYoEgHXg6q5xGYvnU\n4D7Yy6rbRaycG0RuSKSBK33Vm1lzgVZ4dpMwQCINWnuLQMvqWCCrdUlAOBEyQSWT\nX84reMOc3gYXFYCAs6h7zACr5wKBgQC90Xj3DmSSfhqJU8mcO1tlxIHNi6wcMpcT\ntFgRsPWxi6DyCduYdkLWyF0kNeyER9Bm/eyLVqgTvGWbiv/O/3qC+sVa1fdfu7X6\nGB+eI2lZ+9H/s40TrTCvcfdNlmVmw2lYnHBoLh/tLCnWfjKlhq0ovwktSS6yC+k6\n+9/wjB5HxQKBgGKxyLq7xYBHkws1cydnrgnN2TeRhr/HC51Nt3aT0cyCM1rE4UUu\nIXEVA8xMW5Vr6e0eTkqM7Dq0NiY22j9EkJAUo7CVqUlk5u5V3u2avV/Ikm6dtzq/\nu8Teewh2ymW9BAGbQEYEFvUIQY2lrATGsmYEb4c7CAxfVbgZRBsHzwjlAoGAKTBk\nLE/+ON+OSJBa5kDnE00x0XVmcnPz3n26wpQArHcdBIhpE0tOM6cktu/Qk9+1dDPT\neWTjcezmq3rdCYDch8F8w7o8RJTJ5ywG6FzMxo7jQbYnfcaOEvQK8tYYyNTMbkL8\nDU889E0qAvY9bTetKXNSvXXs4Qu+n2L6dAsjovUCgYBTTArPA2SyQfeiggO4RgyB\n89cCT4P7PnJ+20FSYTLlWF7anD+gNb2glQ7feigF2P7/eYTDpu9VRlRe6s+L0/qM\noUHi3/xMazjoqqOIM99tIeOk0M4Nrwii0Hsfcy2ERHIi1hpwDxYrr1CbQlpMToXI\nqpkgjgYOxIzJ98TGu/EFSA==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@rover-telemetry.iam.gserviceaccount.com",
  "client_id": "110083843526091903868",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40rover-telemetry.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}


# Initialize Firebase directly with dict
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Use collection for rover telemetry
telemetry = db.collection("rover_telemetry")

@app.route("/ui")
def ui():
    return render_template("index.html")

@app.route("/")
def home():
    return "Rover Telemetry API — endpoints: GET /data/<id>, POST /data, PUT /update-data, POST /delete-data, GET /data"

# READ (single doc)
@app.route("/data/<doc_id>", methods=["GET"])
def get_data(doc_id):
    doc = telemetry.document(doc_id.strip().lower()).get()
    if doc.exists:
        return jsonify(doc.to_dict()), 200
    return jsonify({"error": "Document not found"}), 404

# CREATE
@app.route("/data", methods=["POST"])
def create_data():
    data = request.get_json()
    if not data or not data.get("id"):
        return jsonify({"error": "JSON with 'id' field required"}), 400
    doc_id = data["id"].strip().lower()
    doc_ref = telemetry.document(doc_id)
    if doc_ref.get().exists:
        return jsonify({"error": "Document already exists"}), 409
    doc_ref.set(data)
    return jsonify({"message": "Data created", "data": data}), 201

# UPDATE
@app.route("/update-data", methods=["PUT"])
def update_data():
    data = request.get_json()
    if not data or not data.get("id"):
        return jsonify({"error": "JSON with 'id' field required"}), 400
    doc_id = data["id"].strip().lower()
    doc_ref = telemetry.document(doc_id)
    if not doc_ref.get().exists:
        return jsonify({"error": "Document not found"}), 404
    doc_ref.set(data, merge=True)
    return jsonify({"message": "Data updated", "data": doc_ref.get().to_dict()}), 200

# DELETE
@app.route("/delete-data", methods=["POST"])
def delete_data():
    data = request.get_json()
    if not data or not data.get("id"):
        return jsonify({"error": "JSON with 'id' field required"}), 400
    doc_id = data["id"].strip().lower()
    doc_ref = telemetry.document(doc_id)
    if not doc_ref.get().exists:
        return jsonify({"error": "Document not found"}), 404
    deleted = doc_ref.get().to_dict()
    doc_ref.delete()
    return jsonify({"message": "Data deleted", "data": deleted}), 200

# LIST ALL
@app.route("/data", methods=["GET"])
def list_data():
    docs = telemetry.stream()
    all_data = [doc.to_dict() for doc in docs]
    return jsonify(all_data), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
