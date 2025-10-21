from flask import Blueprint, render_template
from flask_login import login_required, current_user

insights_bp = Blueprint('insights', __name__)

@insights_bp.route('/insights')
@login_required
def dashboard():
    return render_template('insights_dashboard.html', user=current_user)
