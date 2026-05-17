"""
Main Routes - Page rendering
"""

from flask import Blueprint, render_template, send_from_directory, current_app
from backend.config import config

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/communicate')
def communicate():
    return render_template(
        'communicate.html',
        deployment_mode=config.DEPLOYMENT_MODE
    )


@main_bp.route('/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory(config.VIDEOS_PATH, filename)
