# routes/web_routes.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask import send_from_directory
from flask import current_app
web_bp = Blueprint('web', __name__)

@web_bp.route("/", defaults={"path": ""})
@web_bp.route("/<path:path>")
def frontend(path):
    return send_from_directory(
        current_app.static_folder,
        "index.html"
    )