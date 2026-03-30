"""
Admin routes for Pattern Tracking System API
"""
from flask import Blueprint, request, jsonify, session, current_app
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# 🔒 Helper: check admin login
def require_login():
    if not session.get('admin_logged_in'):
        return jsonify({
            'success': False,
            'error': 'Unauthorized'
        }), 401
    return None


# ✅ LOGIN
@admin_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400

        db = current_app.config['DATABASE']
        user = db.get_user(username, password)

        if user:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return jsonify({'success': True, 'message': 'Login successful', 'username': username}), 200
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ✅ LOGOUT
@admin_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200


# ✅ ANALYTICS — no session required (frontend uses localStorage auth)
@admin_bp.route('/analytics', methods=['GET'])
def get_analytics():
    try:
        db = current_app.config['DATABASE']
        ml_engine = current_app.config['ML_ENGINE']

        total_reports   = db.get_total_reports()
        symptom_counts  = db.get_symptom_counts()
        location_counts = db.get_location_counts()
        severity_counts = db.get_severity_counts()
        daily_counts_list = db.get_daily_counts(days=14)
        daily_counts = {item['date']: item['count'] for item in daily_counts_list}

        ml_analysis = ml_engine.comprehensive_analysis(
            daily_counts=daily_counts,
            symptom_counts=symptom_counts,
            location_counts=location_counts,
            severity_counts=severity_counts
        )

        active_symptoms     = sum(1 for count in symptom_counts.values() if count > 0)
        most_common_symptom = max(symptom_counts, key=symptom_counts.get) if symptom_counts else 'None'
        top_location        = max(location_counts, key=location_counts.get) if location_counts else 'None'

        return jsonify({
            'success': True,
            'data': {
                'overview': {
                    'total_reports':       total_reports,
                    'active_symptoms':     active_symptoms,
                    'most_common_symptom': most_common_symptom,
                    'peak_location':       top_location
                },
                'symptom_counts':  symptom_counts,
                'location_counts': location_counts,
                'severity_counts': severity_counts,
                'daily_counts':    daily_counts_list,
                'ml_analysis':     ml_analysis,
                'timestamp':       datetime.now().isoformat()
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ✅ REPORTS — no session required (frontend uses localStorage auth)
@admin_bp.route('/reports', methods=['GET'])
def get_reports():
    try:
        db = current_app.config['DATABASE']

        limit      = request.args.get('limit', 100, type=int)
        start_date = request.args.get('start_date')
        end_date   = request.args.get('end_date')

        if start_date and end_date:
            reports = db.get_reports_by_date_range(start_date, end_date)
        else:
            reports = db.get_all_reports(limit=limit)

        formatted_reports = []
        for report in reports:
            symptoms = []
            if report['fever']:        symptoms.append('Fever')
            if report['cold_cough']:   symptoms.append('Cold / Cough')
            if report['headache']:     symptoms.append('Headache')
            if report['stomach_pain']: symptoms.append('Stomach Pain')
            if report['nausea']:       symptoms.append('Nausea')
            if report['skin_allergy']: symptoms.append('Skin Allergy')
            if report['fatigue']:      symptoms.append('Fatigue')
            if report['body_pain']:    symptoms.append('Body Pain')

            formatted_reports.append({
                'id':                 report['id'],
                'symptoms':           symptoms,
                'additional_symptoms': report['additional_symptoms'],
                'location':           report['location'],
                'severity':           report['severity'],
                'date':               report['date'],
                'timestamp':          report['timestamp']
            })

        return jsonify({
            'success': True,
            'data':    formatted_reports,
            'count':   len(formatted_reports)
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ✅ PUBLIC ANALYTICS (alias — same as analytics, kept for compatibility)
@admin_bp.route('/public/analytics', methods=['GET'])
def public_analytics():
    return get_analytics()


# ✅ STATS — no session required
@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        db = current_app.config['DATABASE']
        return jsonify({
            'success': True,
            'data': {
                'total_reports':  db.get_total_reports(),
                'symptom_counts': db.get_symptom_counts(),
                'location_counts': db.get_location_counts(),
                'severity_counts': db.get_severity_counts()
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ✅ HEALTH
@admin_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status':    'healthy',
        'service':   'admin',
        'timestamp': datetime.now().isoformat()
    }), 200


# ✅ ADVANCED ML ANALYTICS
@admin_bp.route('/ml/advanced-analytics', methods=['GET'])
def get_advanced_analytics():
    try:
        db          = current_app.config['DATABASE']
        advanced_ml = current_app.config.get('ADVANCED_ML_ENGINE')

        if not advanced_ml:
            return jsonify({'success': False, 'error': 'Advanced ML not initialized'}), 503

        daily_counts    = db.get_daily_counts(days=30)
        symptom_counts  = db.get_symptom_counts()
        severity_counts = db.get_severity_counts()
        location_counts = db.get_location_counts()
        all_reports     = db.get_all_reports(limit=500)

        results = {}
        results['anomaly_detection'] = (
            advanced_ml.detect_anomalies_advanced(daily_counts)
            if len(daily_counts) >= 10 else {'available': False}
        )
        results['symptom_clusters'] = (
            advanced_ml.cluster_symptoms(all_reports)
            if len(all_reports) >= 10 else {'available': False}
        )
        results['forecast'] = (
            advanced_ml.forecast_trend(daily_counts, 7)
            if len(daily_counts) >= 7 else {'available': False}
        )

        return jsonify({'success': True, 'data': results}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ✅ PREDICT SEVERITY
@admin_bp.route('/ml/predict-severity', methods=['POST'])
def predict_severity():
    try:
        data        = request.get_json() or {}
        advanced_ml = current_app.config.get('ADVANCED_ML_ENGINE')

        if not advanced_ml:
            return jsonify({'success': False, 'error': 'ML not initialized'}), 503

        all_symptoms = [
            'fever', 'cold_cough', 'headache', 'stomach_pain',
            'nausea', 'skin_allergy', 'fatigue', 'body_pain'
        ]
        symptom_vector   = [1 if s in data.get('symptoms', []) else 0 for s in all_symptoms]
        db               = current_app.config['DATABASE']
        historical_data  = db.get_all_reports(limit=500)
        prediction       = advanced_ml.predict_severity(symptom_vector, historical_data)

        return jsonify({'success': True, 'data': prediction}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500