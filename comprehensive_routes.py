from flask import Blueprint
from flask_login import login_required

comprehensive_bp = Blueprint('features', __name__, url_prefix='/features')

@comprehensive_bp.route('/goals')
@login_required
def goals_dashboard():
    return "Goals Dashboard - Working!"

@comprehensive_bp.route('/analytics')
@login_required
def analytics_dashboard():
    return "Analytics Dashboard - Working!"
