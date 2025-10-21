from flask import Blueprint

comprehensive_bp = Blueprint('comprehensive', __name__)

@comprehensive_bp.route('/goals')
def goals():
    """Goals dashboard placeholder"""
    return {'message': 'Goals feature coming soon'}, 200
