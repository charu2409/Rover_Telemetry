import os, json
from flask import Flask, request, jsonify, render_template
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
if "FIREBASE_KEY" in os.environ:
    cred_dict = json.loads(os.environ["FIREBASE_KEY"])
    cred = credentials.Certificate(cred_dict)
else:
    cred = credentials.Certificate("C:/Users/charu/Downloads/rover-telemetry-firebase-adminsdk-fbsvc-6081442c29.json")

firebase_admin.initialize_app(cred)
db = firestore.client()
telemetry = db.collection("rover_telemetry")

@app.route("/")
def home():
    return render_template("index.html")

# READ (single document)
@app.route("/data/<doc_id>", methods=["GET"])
def get_data(doc_id):
    doc = telemetry.document(doc_id.strip().lower()).get()
    if doc.exists:
        return jsonify(doc.to_dict()), 200
    return jsonify({"error": "Document not found"}), 404

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

@app.route("/data", methods=["GET"])
def list_data():
    docs = telemetry.stream()
    all_data = [doc.to_dict() for doc in docs]
    return jsonify(all_data), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
