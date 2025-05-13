from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from sqlalchemy import inspect, text
import subprocess
import threading
import time


app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/counters_db")
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

# Streamlit Integration
def run_streamlit():
    """
    Runs the Streamlit app as a subprocess.
    """
    try:
        subprocess.Popen(["streamlit", "run", "study.py", "--server.enableCORS=false", "--server.enableXsrfProtection=false"], 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print(f"Error running Streamlit: {e}")

@app.route("/visualization")
def visualization():
    """
    1. Export current activities to CSV
    2. Start Streamlit visualization (if not already running)
    3. Redirect to Streamlit UI
    """
    # Export CSV
    try:
        activities = Activity.query.order_by(Activity.date.desc()).all()
        if not activities:
            return "<h3>❌ Žiadne dáta na exportovanie</h3>", 404

        import csv
        with open("activities.csv", mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["id", "topic", "study_time", "date"])  # header
            for activity in activities:
                writer.writerow([
                    activity.id,
                    activity.topic,
                    activity.study_time,
                    activity.date.isoformat()
                ])
    except Exception as e:
        return f"<h3>❌ Chyba pri exporte CSV: {str(e)}</h3>", 500

    # Run Streamlit if not already running
    if not hasattr(app, 'streamlit_thread') or not app.streamlit_thread.is_alive():
        def run_streamlit():
            subprocess.Popen([
                "streamlit", "run", "study.py",
                "--server.enableCORS=false",
                "--server.enableXsrfProtection=false"
            ])

        app.streamlit_thread = threading.Thread(target=run_streamlit)
        app.streamlit_thread.daemon = True
        app.streamlit_thread.start()
        time.sleep(2)  # give streamlit time to start

    # Redirect to Streamlit interface
    return redirect("http://localhost:8501")

@app.route("/export_csv", methods=["GET"])
def export_csv():
    activities = Activity.query.order_by(Activity.date.desc()).all()
    if not activities:
        return jsonify({"error": "No data to export"}), 404

    import csv
    from io import StringIO
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["id", "topic", "study_time", "date"])  # Header

    for activity in activities:
        writer.writerow([activity.id, activity.topic, activity.study_time, activity.date.isoformat()])

    output = si.getvalue()
    return output, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=activities.csv'
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
