from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from sqlalchemy import inspect, text
from ai import ask_gemini
from flask_cors import CORS

app = Flask(_name_)
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100), nullable=False)
    study_time = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def serialize(self):
        return {
            "id": self.id,
            "topic": self.topic,
            "study_time": self.study_time,
            "date": self.date.isoformat()  # ISO string for JS Date compatibility
        }

    
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/activities", methods=["GET"])
def get_activities():
    activities = Activity.query.order_by(Activity.date.desc()).all()
    return jsonify([activity.serialize() for activity in activities])

# POST a new activity
@app.route("/activities", methods=["POST"])
def add_activity():
    data = request.get_json()
    topic = data.get("topic")
    study_time = data.get("study_time")
    date_str = data.get("date")

    try:
        # Convert string date to datetime object
        date = datetime.fromisoformat(date_str)
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    activity = Activity(topic=topic, study_time=int(study_time), date=date)
    db.session.add(activity)
    db.session.commit()
    return jsonify(activity.serialize()), 201

@app.route("/activities/<int:activity_id>", methods=["DELETE"])
def delete_activity(activity_id):
    activity = Activity.query.get(activity_id)
    if activity:
        db.session.delete(activity)
        db.session.commit()
        return jsonify({"message": "Aktivita bola odstránená"}), 200
    else:
        return jsonify({"error": "Aktivita neexistuje"}), 404


@app.route("/activities", methods=["DELETE"])
def clear_all_activities():
    try:
        num_deleted = Activity.query.delete()
        db.session.commit()
        return jsonify({"message": f"Vymazaných {num_deleted} aktivít"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    activities = data.get("activities", [])

    if not activities:
        return jsonify({"error": "Chýbajú študijné dáta"}), 400

    try:
        response = ask_gemini(activities)
        return jsonify({"recommendation": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/connected")
def check_connection():
    try:
        # Proper way to run raw SQL in SQLAlchemy
        db.session.execute(text("SELECT 1"))

        # Check if the Activity table exists
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        if "activity" in tables:
            return """
                <h2>✅ Database Connection Successful</h2>
                <p>Activity table is present.</p>
            """
        else:
            return """
                <h2>⚠️ Connected to Database</h2>
                <p>But <strong>Activity</strong> table does not exist.</p>
            """
    except Exception as e:
        return f"""
            <h2>❌ Database Connection Failed</h2>
            <p>Error: {str(e)}</p>
        """



if _name_ == "_main_":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5004)), debug=True)

from flask_cors import CORS

