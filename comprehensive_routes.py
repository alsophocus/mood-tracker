from flask import Blueprint, render_template
from flask_login import login_required

comprehensive_bp = Blueprint('features', __name__, url_prefix='/features')

@comprehensive_bp.route('/goals')
@login_required
def goals_dashboard():
    return render_template('goals_dashboard.html')

@comprehensive_bp.route('/analytics')
@login_required
def analytics_dashboard():
    return render_template('analytics_dashboard.html')
