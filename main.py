import logging
import uuid
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# prod
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
# app.config[
#     "SQLALCHEMY_DATABASE_URI"
# ] = "postgresql://postgres:L91y9IfMgGivvHGNi62p@containers-us-west-50.railway.app:6656/railway"

# dev
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:1111@localhost/bug"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Bug(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
        }


# =======================( GET )===========================


@app.route("/all-bugs", methods=["GET"])
def get_all_bugs():
    try:
        bugs = Bug.query.all()
        return jsonify([bug.serialize() for bug in bugs])
    except SQLAlchemyError as e:
        logging.error(str(e))
        return jsonify({"message": "Database error"}), 500


@app.route("/bug/<string:id>", methods=["GET"])
def get_bug_by_id(id):
    try:
        bug = Bug.query.get(id)
        if bug:
            return jsonify(bug.serialize())
        else:
            return jsonify({"message": "Bug not found"}), 404
    except SQLAlchemyError as e:
        logging.error(str(e))
        return jsonify({"message": "Database error"}), 500


# =======================( POST )===========================


@app.route("/new-bug", methods=["POST"])
def create_new_bug():
    if not request.json:
        abort(400, "No data provided")

    name = request.json.get("name")
    description = request.json.get("description")
    category = request.json.get("category")

    if not name or not description or not category:
        abort(400, "Required fields: 'name', 'description', 'category'")

    new_bug = Bug(name=name, description=description, category=category)
    db.session.add(new_bug)

    try:
        db.session.commit()
        return jsonify({"message": "Bug added successfully"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(str(e))
        return jsonify({"message": "An error occurred during bug creation"}), 500


# =======================( PUT )===========================


@app.route("/bug/<string:id>", methods=["PUT"])
def update_bug_by_id(id):
    bug = Bug.query.get_or_404(id)

    if "name" in request.json:
        bug.name = request.json["name"]
    if "description" in request.json:
        bug.description = request.json["description"]
    if "category" in request.json:
        bug.category = request.json["category"]

    db.session.commit()

    return jsonify({"message": "Bug updated successfully"})


# =======================( DELETE )===========================


@app.route("/bug/<string:id>", methods=["DELETE"])
def delete_bug_by_id(id):
    try:
        bug = Bug.query.get(id)
        if bug:
            db.session.delete(bug)
            db.session.commit()
            return jsonify({"message": "Bug deleted successfully"})
        else:
            return jsonify({"message": "Bug not found"}), 404
    except SQLAlchemyError as e:
        logging.error(str(e))
        return jsonify({"message": "An error occurred during deletion"}), 500


@app.route("/")
def index():
    return jsonify({"Choo Choo": "Welcome to your Flask app 🚅"})


if __name__ == "__main__":
    # initialize table once at the beginning
    # with app.app_context():
    #     db.create_all()
    app.run(host="0.0.0.0", port=os.getenv("PORT"), debug=True)
    # app.run(host="0.0.0.0", port=8000, debug=True)
