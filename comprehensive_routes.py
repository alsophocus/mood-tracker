from flask import Blueprint, render_template
from flask_login import login_required

comprehensive_bp = Blueprint('comprehensive', __name__)

@comprehensive_bp.route('/features/goals')
@login_required
def goals():
    """Goals dashboard"""
    return render_template('goals_dashboard.html')

@comprehensive_bp.route('/features/analytics')
@login_required
def analytics():
    """Analytics dashboard"""
    return render_template('analytics_dashboard.html')
