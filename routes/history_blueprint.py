from flask import Blueprint, request, jsonify
from models import db   # Use the shared db instance
from models.history import History
import json

history_bp = Blueprint("history_bp", __name__)

