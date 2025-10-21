from flask import Blueprint, render_template
from flask_login import login_required

insights_bp = Blueprint('insights', __name__, url_prefix='/insights')

@insights_bp.route('/')
@login_required
def dashboard():
    return render_template('insights_dashboard_simple.html')
