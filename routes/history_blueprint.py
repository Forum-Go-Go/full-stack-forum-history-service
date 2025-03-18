from flask import Blueprint, request, jsonify
from models import db   # Use the shared db instance
from models.history import History
from datetime import datetime
import json
from decorator import authenticate_user

history_bp = Blueprint("history_bp", __name__)

# add a new histroy (user visit the post in the frontent)
@history_bp.route("/", methods=["POST"], strict_slashes=False)
@authenticate_user()
def add_history_entry(user_id, user_verified, user_role):
    data = request.get_json()
    
    if not data or "postId" not in data:
        return jsonify({"error": "Invalid request, postId required"}), 400  # 这里修正了状态码

    try:
        new_history = History(
            userId=user_id,  # get userId from token 
            postId=data["postId"],
            viewDate=datetime.now()  # get current time
        )

        db.session.add(new_history)
        db.session.commit()

        return jsonify({"message": "History entry added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to add history entry: {str(e)}"}), 500

# get post history of current user
@history_bp.route("/", methods=["GET"])
@authenticate_user()
def get_user_history(user_id, user_verified, user_role):
    history_entries = History.query.filter_by(userId=user_id).order_by(History.viewDate.desc()).all()

    if not history_entries:
        return jsonify({"message": "No history found for this user"}), 200
    
    history_list = []
    for entry in history_entries:
        history_list.append({
            "historyId": entry.historyId,
            "userId": entry.userId,
            "postId": entry.postId,
            "viewDate": entry.viewDate.strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify({"history": history_list}), 200

# clear spedific record
@history_bp.route("/<int:history_id>", methods=["DELETE"])
@authenticate_user()
def delete_history_entry(user_id, user_verified, user_role, history_id):
    history_entry = History.query.get(history_id)

    if not history_entry:
        return jsonify({"error": "History entry not found"}), 404

    # user can only delete their own histroy
    if history_entry.userId != user_id:
        return jsonify({"error": "You are not authorized to delete this history entry"}), 403

    db.session.delete(history_entry)
    db.session.commit()

    return jsonify({"message": "History entry deleted successfully"}), 200
