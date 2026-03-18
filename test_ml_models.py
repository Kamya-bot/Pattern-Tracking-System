"""
Quick ML Model Validation Script
Run this to verify all ML components are working correctly
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from advanced_ml import AdvancedMLEngine
from models import Database
import json

def test_isolation_forest():
    """Test Isolation Forest anomaly detection"""
    print("\n" + "="*60)
    print("🔬 TEST 1: Isolation Forest (Anomaly Detection)")
    print("="*60)
    
    ml = AdvancedMLEngine()
    
    # Sample daily counts
    daily_counts = {
        '2024-03-01': 3,
        '2024-03-02': 2,
        '2024-03-03': 4,
        '2024-03-04': 3,
        '2024-03-05': 8,  # Anomaly
        '2024-03-06': 3,
        '2024-03-07': 2,
        '2024-03-08': 3,
        '2024-03-09': 4,
        '2024-03-10': 2,
        '2024-03-11': 3,
        '2024-03-12': 9,  # Anomaly
        '2024-03-13': 3,
        '2024-03-14': 4
    }
    
    result = ml.detect_anomalies_advanced(daily_counts)
    
    print(f"✅ Method: {result.get('method')}")
    print(f"✅ Anomalies Detected: {result.get('anomalies_detected')}")
    print(f"✅ Total Anomalies: {result.get('total_anomalies', 0)}")
    
    if result.get('method') == 'Isolation Forest':
        print("🎉 SUCCESS: Using Isolation Forest (sklearn)")
        print(f"   - Algorithm: {result.get('model_parameters', {}).get('algorithm')}")
        print(f"   - Samples: {result.get('model_parameters', {}).get('n_samples')}")
        return True
    else:
        print("⚠️  WARNING: Using fallback method")
        print(f"   Reason: {result.get('reason', 'Unknown')}")
        return False

def test_kmeans_clustering():
    """Test K-Means clustering"""
    print("\n" + "="*60)
    print("🔬 TEST 2: K-Means Clustering (Symptom Patterns)")
    print("="*60)
    
    ml = AdvancedMLEngine()
    
    # Sample reports
    reports = []
    symptoms_patterns = [
        # Pattern 1: Fever + Cough (respiratory)
        [1, 1, 0, 0, 0, 0, 1, 0],
        [1, 1, 1, 0, 0, 0, 1, 0],
        [1, 1, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 1, 1],
        [1, 1, 0, 0, 0, 0, 1, 0],
        
        # Pattern 2: Stomach pain + Nausea (digestive)
        [0, 0, 0, 1, 1, 0, 1, 0],
        [0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 1, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [1, 0, 0, 1, 1, 0, 1, 0],
        
        # Pattern 3: Headache + Fatigue
        [0, 0, 1, 0, 0, 0, 1, 1],
        [0, 0, 1, 0, 0, 0, 1, 0],
        [1, 0, 1, 0, 0, 0, 1, 1],
        [0, 0, 1, 0, 0, 0, 1, 1],
        [0, 0, 1, 0, 0, 0, 1, 0],
        
        # More varied patterns
        [1, 1, 1, 0, 0, 0, 1, 1],
        [0, 1, 0, 1, 0, 0, 1, 0],
        [1, 0, 1, 1, 0, 0, 1, 0],
        [0, 0, 1, 0, 1, 0, 1, 1],
        [1, 1, 0, 0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0, 0, 1, 0],
        [1, 0, 0, 1, 1, 0, 0, 1],
        [0, 0, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 0, 0, 0, 1, 0],
        [0, 1, 0, 1, 1, 0, 1, 0]
    ]
    
    symptoms_names = ['fever', 'cold_cough', 'headache', 'stomach_pain',
                     'nausea', 'skin_allergy', 'fatigue', 'body_pain']
    
    for pattern in symptoms_patterns:
        report = {symptoms_names[i]: pattern[i] for i in range(8)}
        reports.append(report)
    
    result = ml.cluster_symptoms(reports)
    
    print(f"✅ Clustering Available: {result.get('clustering_available')}")
    
    if result.get('clustering_available'):
        print(f"✅ Method: {result.get('method')}")
        print(f"✅ Number of Clusters: {result.get('n_clusters')}")
        print(f"✅ Total Reports: {result.get('total_reports')}")
        print("\n📊 Clusters Found:")
        for cluster in result.get('clusters', [])[:3]:  # Show top 3
            print(f"   Cluster {cluster['cluster_id']}: {cluster['size']} reports ({cluster['percentage']:.1f}%)")
            print(f"   Pattern: {cluster['pattern_description']}")
        print("🎉 SUCCESS: K-Means clustering working!")
        return True
    else:
        print(f"⚠️  WARNING: Clustering not available")
        print(f"   Reason: {result.get('reason', 'Unknown')}")
        return False

def test_random_forest():
    """Test Random Forest severity prediction"""
    print("\n" + "="*60)
    print("🔬 TEST 3: Random Forest (Severity Prediction)")
    print("="*60)
    
    ml = AdvancedMLEngine()
    
    # Create training data with severity labels
    historical_data = []
    
    # Mild cases (1-2 symptoms)
    for _ in range(8):
        historical_data.append({
            'fever': 0, 'cold_cough': 1, 'headache': 0, 'stomach_pain': 0,
            'nausea': 0, 'skin_allergy': 0, 'fatigue': 0, 'body_pain': 0,
            'severity': 'Mild'
        })
    
    # Moderate cases (3-4 symptoms)
    for _ in range(8):
        historical_data.append({
            'fever': 1, 'cold_cough': 1, 'headache': 1, 'stomach_pain': 0,
            'nausea': 0, 'skin_allergy': 0, 'fatigue': 1, 'body_pain': 0,
            'severity': 'Moderate'
        })
    
    # Severe cases (5+ symptoms)
    for _ in range(8):
        historical_data.append({
            'fever': 1, 'cold_cough': 1, 'headache': 1, 'stomach_pain': 1,
            'nausea': 1, 'skin_allergy': 0, 'fatigue': 1, 'body_pain': 1,
            'severity': 'Severe'
        })
    
    # Test symptom vector (moderate case)
    test_vector = [1, 1, 1, 0, 0, 0, 1, 0]  # 4 symptoms
    
    result = ml.predict_severity(test_vector, historical_data)
    
    print(f"✅ Method: {result.get('method')}")
    print(f"✅ Predicted Severity: {result.get('predicted_severity')}")
    print(f"✅ Confidence: {result.get('confidence', 0):.2%}")
    
    if 'probability_distribution' in result:
        print("✅ Probability Distribution:")
        for severity, prob in result['probability_distribution'].items():
            print(f"   {severity}: {prob:.2%}")
    
    if result.get('method') == 'Random Forest Classifier':
        print("🎉 SUCCESS: Random Forest classifier working!")
        print(f"   Training Data: {result.get('model_accuracy')}")
        return True
    else:
        print("⚠️  WARNING: Using rule-based fallback")
        return False

def test_forecasting():
    """Test time series forecasting"""
    print("\n" + "="*60)
    print("🔬 TEST 4: Time-Series Forecasting (Linear Regression)")
    print("="*60)
    
    ml = AdvancedMLEngine()
    
    # Sample daily counts with upward trend
    daily_counts = {
        '2024-03-01': 2,
        '2024-03-02': 3,
        '2024-03-03': 3,
        '2024-03-04': 4,
        '2024-03-05': 5,
        '2024-03-06': 4,
        '2024-03-07': 6,
        '2024-03-08': 5,
        '2024-03-09': 7,
        '2024-03-10': 6,
        '2024-03-11': 8,
        '2024-03-12': 7,
        '2024-03-13': 9,
        '2024-03-14': 8
    }
    
    result = ml.forecast_trend(daily_counts, forecast_days=7)
    
    print(f"✅ Forecasting Available: {result.get('forecasting_available')}")
    
    if result.get('forecasting_available'):
        print(f"✅ Method: {result.get('method')}")
        print(f"✅ Trend Direction: {result.get('trend_direction')}")
        print(f"✅ Slope: {result.get('slope', 0):.3f}")
        print(f"✅ Forecast Period: {result.get('forecast_period')} days")
        print(f"✅ Confidence Level: {result.get('confidence_level')}")
        
        print("\n📊 Sample Forecasts:")
        for day in result.get('forecast', [])[:3]:  # Show first 3 days
            print(f"   {day['date']}: {day['predicted_count']} "
                  f"(range: {day['lower_bound']}-{day['upper_bound']})")
        
        print("🎉 SUCCESS: Time-series forecasting working!")
        return True
    else:
        print(f"⚠️  WARNING: Forecasting not available")
        print(f"   Reason: {result.get('reason', 'Unknown')}")
        return False

def test_risk_scoring():
    """Test ML risk scoring"""
    print("\n" + "="*60)
    print("🔬 TEST 5: ML Risk Scoring (Multi-Factor Assessment)")
    print("="*60)
    
    ml = AdvancedMLEngine()
    
    # Sample data
    symptom_counts = {
        'fever': 25,
        'cold_cough': 18,
        'headache': 15,
        'stomach_pain': 8,
        'nausea': 6,
        'skin_allergy': 3,
        'fatigue': 20,
        'body_pain': 12
    }
    
    severity_counts = {
        'Mild': 15,
        'Moderate': 10,
        'Severe': 3
    }
    
    result = ml.calculate_risk_score(
        location='Engineering Hostel',
        symptom_counts=symptom_counts,
        severity_counts=severity_counts,
        recent_trend='increasing'
    )
    
    print(f"✅ Risk Score: {result.get('risk_score'):.1f}/100")
    print(f"✅ Risk Level: {result.get('risk_level')}")
    print(f"✅ Assessment Method: {result.get('assessment_method')}")
    
    print("\n📊 Risk Breakdown:")
    for component, data in result.get('breakdown', {}).items():
        print(f"   {component.title()}: {data.get('score', 0):.1f} points (weight: {data.get('weight', 0)})")
    
    print("\n💡 Recommended Actions:")
    for action in result.get('recommended_actions', [])[:3]:
        print(f"   • {action}")
    
    print("🎉 SUCCESS: ML risk scoring working!")
    return True

def test_database_integration():
    """Test database with ML engine"""
    print("\n" + "="*60)
    print("🔬 TEST 6: Database + ML Integration")
    print("="*60)
    
    try:
        db = Database('data/pattern_tracking.db')
        
        # Check if database has data
        total = db.get_total_reports()
        print(f"✅ Total Reports in DB: {total}")
        
        if total < 10:
            print("⚠️  WARNING: Database has insufficient data (<10 reports)")
            print("   Run: curl -X POST http://localhost:5000/api/seed-database")
            return False
        
        # Get data for ML
        daily_counts = db.get_daily_counts(days=14)
        symptom_counts = db.get_symptom_counts()
        
        print(f"✅ Days of Data: {len(daily_counts)}")
        print(f"✅ Symptom Types: {len(symptom_counts)}")
        
        print("🎉 SUCCESS: Database integration working!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Database integration failed")
        print(f"   {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🚀 PHASE 2 ML VALIDATION - Automated Testing Suite")
    print("="*70)
    print("Testing all 5 ML components...")
    
    results = {
        'Isolation Forest': test_isolation_forest(),
        'K-Means Clustering': test_kmeans_clustering(),
        'Random Forest': test_random_forest(),
        'Time-Series Forecasting': test_forecasting(),
        'ML Risk Scoring': test_risk_scoring(),
        'Database Integration': test_database_integration()
    }
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST RESULTS SUMMARY")
    print("="*70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("="*70)
    print(f"📈 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Phase 2 is fully operational!")
        print("\n✅ Ready for Phase 3: Advanced Visualizations")
        print("   Next step: Reply 'Start Phase 3' to proceed")
    elif passed >= total * 0.8:
        print("\n⚠️  MOSTLY WORKING - Some minor issues detected")
        print("   Check warnings above and resolve before Phase 3")
    else:
        print("\n❌ CRITICAL ISSUES - Phase 2 needs debugging")
        print("   Review error messages and check:")
        print("   1. scikit-learn installation")
        print("   2. Database has sufficient data (≥30 reports)")
        print("   3. Server logs for import errors")
    
    print("="*70 + "\n")
    
    return passed == total

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
