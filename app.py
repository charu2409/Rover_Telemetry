import os, json
from flask import Flask, request, jsonify, render_template
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# --- Initialize Firebase Admin using service account JSON path in env var ---
if "FIREBASE_KEY" in os.environ:
    cred_dict = json.loads(os.environ["FIREBASE_KEY"])
    cred = credentials.Certificate(cred_dict)
else:
    # fallback for local testing
    cred = credentials.Certificate("C:\Users\charu\Downloads\rover-telemetry-firebase-adminsdk-fbsvc-6081442c29.json")

firebase_admin.initialize_app(cred)
db = firestore.client()
rover = db.collection("rover")  

@app.route("/")
def home():
    return render_template("index.html")
    
@app.route("/rover/<doc_id>", methods=["GET"])
def get_rover(doc_id):
    doc = rover.document(doc_id.strip()).get()
    if doc.exists:
        return jsonify(doc.to_dict()), 200
    return jsonify({"error": "Rover data not found"}), 404

@app.route("/rover", methods=["POST"])
def create_rover():
    data = request.get_json()
    if not data or not data.get("id"):
        return jsonify({"error": "JSON with 'id' field required"}), 400
    
    doc_id = data["id"].strip()
    doc_ref = rover.document(doc_id)
    
    if doc_ref.get().exists:
        return jsonify({"error": "Rover data with this ID already exists"}), 409
    
    data["timestamp"] = firestore.SERVER_TIMESTAMP
    doc_ref.set(data)
    return jsonify({"message": "Rover data created", "data": data}), 201

@app.route("/update-rover", methods=["PUT"])
def update_rover():
    data = request.get_json()
    if not data or not data.get("id"):
        return jsonify({"error": "JSON with 'id' field required"}), 400
    
    doc_id = data["id"].strip()
    doc_ref = rover.document(doc_id)
    
    if not doc_ref.get().exists:
        return jsonify({"error": "Rover data not found"}), 404
    
    data["timestamp"] = firestore.SERVER_TIMESTAMP
    doc_ref.set(data, merge=True)  # merge=True allows partial update
    return jsonify({"message": "Rover data updated", "data": doc_ref.get().to_dict()}), 200

@app.route("/delete-rover", methods=["POST"])
def delete_rover():
    data = request.get_json()
    if not data or not data.get("id"):
        return jsonify({"error": "JSON with 'id' field required"}), 400
    
    doc_id = data["id"].strip()
    doc_ref = rover.document(doc_id)
    
    if not doc_ref.get().exists:
        return jsonify({"error": "Rover data not found"}), 404
    
    deleted = doc_ref.get().to_dict()
    doc_ref.delete()
    return jsonify({"message": "Rover data deleted", "data": deleted}), 200

@app.route("/rovers", methods=["GET"])
def list_rovers():
    docs = rover.stream()
    all_data = [doc.to_dict() for doc in docs]
    return jsonify(all_data), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
