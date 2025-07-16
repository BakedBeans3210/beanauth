from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import json
import os

cred_json = json.loads(os.environ["FIREBASE_CREDENTIALS"])
cred = credentials.Certificate(cred_json)

firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

# 🚪 Create or login to user account
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data["username"]
    password_hash = data["password"]

    user_ref = db.collection("users").document(username)
    user_doc = user_ref.get()

    if user_doc.exists:
        if user_doc.to_dict()["password"] == password_hash:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Invalid password"})
    else:
        user_ref.set({"password": password_hash})
        return jsonify({"success": True, "created": True})

# 🧱 Set any key-value under a specified app
@app.route("/set_app_value", methods=["POST"])
def set_app_value():
    data = request.json
    username = data["username"]
    app = data["app"]
    key = data["key"]
    value = data["value"]

    field_path = f"{app}.{key}"
    db.collection("users").document(username).update({field_path: value})
    return jsonify({"success": True})

# 📁 Get all values for an app
@app.route("/get_app_data", methods=["POST"])
def get_app_data():
    data = request.json
    username = data["username"]
    app = data["app"]

    doc = db.collection("users").document(username).get()
    if not doc.exists:
        return jsonify({"error": "User not found"})

    app_data = doc.to_dict().get(app, {})
    return jsonify({"app": app, "data": app_data})

# 📍 Get specific key from an app
@app.route("/get_app_value", methods=["POST"])
def get_app_value():
    data = request.json
    username = data["username"]
    app = data["app"]
    key = data["key"]

    doc = db.collection("users").document(username).get()
    if not doc.exists:
        return jsonify({"error": "User not found"})

    value = doc.to_dict().get(app, {}).get(key, None)
    return jsonify({"app": app, "key": key, "value": value})