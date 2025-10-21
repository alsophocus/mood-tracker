"""
Web endpoint for testing migrations directly on deployed Railway app
"""

from flask import Blueprint, jsonify, request
from admin_services import AdminService
import traceback

# Create blueprint for migration testing
migration_bp = Blueprint('migration_test', __name__, url_prefix='/migration-test')

@migration_bp.route('/basic', methods=['GET', 'POST'])
def test_basic_migration():
    """Test basic migration operation via web endpoint"""
    try:
        admin_service = AdminService()
        result = admin_service.run_basic_migration()
        
        response = {
            'success': result.get('success', False),
            'result': result,
            'endpoint': 'basic_migration',
            'method': request.method
        }
        
        if result.get('success'):
            response['message'] = '✅ Migration successful'
            return jsonify(response), 200
        else:
            response['message'] = '❌ Migration failed'
            response['error'] = result.get('error', 'Unknown error')
            return jsonify(response), 500
            
    except Exception as e:
        error_response = {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'traceback': traceback.format_exc(),
            'endpoint': 'basic_migration',
            'method': request.method,
            'message': '❌ Migration exception'
        }
        return jsonify(error_response), 500

@migration_bp.route('/status', methods=['GET'])
def migration_status():
    """Get migration testing status"""
    return jsonify({
        'status': 'Migration testing endpoint active',
        'endpoints': {
            'basic': '/migration-test/basic',
            'status': '/migration-test/status'
        },
        'methods': ['GET', 'POST']
    })
