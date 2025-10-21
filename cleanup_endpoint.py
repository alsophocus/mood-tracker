#!/usr/bin/env python3
"""
Simple Flask endpoint to trigger database cleanup
Add this route to the main app temporarily
"""
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from datetime import date
from database import Database

cleanup_bp = Blueprint('cleanup', __name__)

@cleanup_bp.route('/admin/cleanup-until-oct19')
@login_required
def cleanup_until_oct19():
    """Admin endpoint to delete mood data until October 19, 2025"""
    target_date = date(2025, 10, 19)
    
    try:
        db = Database()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count records first
            cursor.execute('SELECT COUNT(*) FROM moods WHERE date <= %s', (target_date,))
            count = cursor.fetchone()[0]
            
            if count == 0:
                return jsonify({
                    'success': True,
                    'message': 'No records to delete',
                    'deleted': 0,
                    'remaining': 0
                })
            
            # Delete mood entries until target date
            cursor.execute('DELETE FROM moods WHERE date <= %s', (target_date,))
            deleted_moods = cursor.rowcount
            
            conn.commit()
            
            # Get remaining count
            cursor.execute('SELECT COUNT(*) FROM moods')
            remaining = cursor.fetchone()[0]
            
            return jsonify({
                'success': True,
                'message': f'Successfully deleted {deleted_moods} mood entries until {target_date}',
                'deleted': deleted_moods,
                'remaining': remaining,
                'target_date': str(target_date)
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
