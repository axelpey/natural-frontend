import json

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from natural_frontend.natural_frontend import NaturalFrontend, NaturalFrontendOptions

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///social_network.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    relationships = relationship("Relationship", backref="user", lazy=True)
    pokes = relationship("Poke", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Relationship(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    friend_id = Column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint("user_id", "friend_id", name="_user_friend_uc"),)

    def __repr__(self):
        return f"<Relationship {self.user_id} - {self.friend_id}>"


class Poke(db.Model):
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    receiver_id = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Poke {self.sender_id} -> {self.receiver_id}>"


@app.route("/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Hello, World!"})


@app.route("/user", methods=["POST"])
def create_user():
    data = request.json
    new_user = User(username=data["username"])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created!"}), 201


@app.route("/relationship", methods=["POST"])
def add_relationship():
    data = request.json
    user = User.query.get(data["user_id"])
    if user:
        new_relationship = Relationship(user_id=user.id, friend_id=data["friend_id"])
        db.session.add(new_relationship)
        db.session.commit()
        return jsonify({"message": "Relationship added!"}), 201
    return jsonify({"message": "User not found!"}), 404


@app.route("/relationship/<int:user_id>/<int:friend_id>", methods=["DELETE"])
def remove_relationship(user_id, friend_id):
    relationship = Relationship.query.filter_by(
        user_id=user_id, friend_id=friend_id
    ).first()
    if relationship:
        db.session.delete(relationship)
        db.session.commit()
        return jsonify({"message": "Relationship removed!"})
    return jsonify({"message": "Relationship not found!"}), 404


@app.route("/poke", methods=["POST"])
def send_poke():
    data = request.json
    new_poke = Poke(sender_id=data["sender_id"], receiver_id=data["receiver_id"])
    db.session.add(new_poke)
    db.session.commit()
    return jsonify({"message": "Poke sent!"}), 201


# Open the creds.json
with open("creds.json") as f:
    creds = json.load(f)

app = NaturalFrontend(
    app,
    openai_api_key=creds["key"],
    options=NaturalFrontendOptions(
        frontend_endpoint="frontend",
        personas=[
            {
                "persona": "Social Butterfly",
                "description": "Extrovert, loves connecting and keeping in touch with friends.",
            },
            {
                "persona": "Networking Professional",
                "description": "Career-focused, uses platform for professional connections and growth.",
            },
            {
                "persona": "Casual User",
                "description": "Occasional user, interested in staying connected with close friends.",
            },
        ],
    ),
)
