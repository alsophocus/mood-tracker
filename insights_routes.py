from flask import Blueprint
from flask_login import login_required

insights_bp = Blueprint('insights', __name__, url_prefix='/insights')

@insights_bp.route('/')
@login_required
def dashboard():
    return "Insights Dashboard - Working!"
