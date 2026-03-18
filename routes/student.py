"""
Student routes for Pattern Tracking System API
"""
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

student_bp = Blueprint('student', __name__, url_prefix='/api/student')

@student_bp.route('/submit-report', methods=['POST'])
def submit_report():
    """
    Submit a new symptom report

    Expected JSON:
    {
        "symptoms": ["Fever", "Headache"],
        "additionalSymptoms": "Mild cough",
        "location": "North Hostel",
        "severity": "Moderate"
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('location') or not data.get('severity'):
            return jsonify({
                'success': False,
                'error': 'Location and severity are required'
            }), 400

        symptoms = data.get('symptoms', [])

        # Convert symptoms array to binary flags
        report_data = {
            'fever':               1 if 'Fever' in symptoms else 0,
            'cold_cough':          1 if 'Cold / Cough' in symptoms else 0,
            'headache':            1 if 'Headache' in symptoms else 0,
            'stomach_pain':        1 if 'Stomach Pain' in symptoms else 0,
            'nausea':              1 if 'Nausea' in symptoms else 0,
            'skin_allergy':        1 if 'Skin Allergy' in symptoms else 0,
            'fatigue':             1 if 'Fatigue' in symptoms else 0,
            'body_pain':           1 if 'Body Pain' in symptoms else 0,
            'additional_symptoms': data.get('additionalSymptoms', ''),
            'location':            data.get('location'),
            'severity':            data.get('severity', '').capitalize(),
            'date':                datetime.now().strftime('%Y-%m-%d')
        }

        db = current_app.config['DATABASE']
        report_id = db.insert_report(report_data)

        return jsonify({
            'success': True,
            'message': 'Report submitted successfully',
            'report_id': report_id
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@student_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'student',
        'timestamp': datetime.now().isoformat()
    }), 200