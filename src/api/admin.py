from flask import Blueprint, render_template

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/import', methods=['GET', 'POST'])
def import_users():
    return "Import Users Placeholder"

@admin_bp.route('/import/academic', methods=['GET', 'POST'])
def import_academic():
    return "Import Academic Placeholder"
