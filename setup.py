#!/usr/bin/env python3
"""
Setup script for Pattern Tracking System Backend
Initializes database and creates sample data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from models import Database
from ml_engine import MLEngine

def main():
    print("\n" + "="*60)
    print("🚀 Pattern Tracking System - Backend Setup")
    print("="*60 + "\n")
    
    # Create data directory
    data_dir = os.path.dirname(Config.DATABASE_PATH)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"📁 Created data directory: {data_dir}")
    
    # Initialize database
    print("🗄️  Initializing database...")
    db = Database(Config.DATABASE_PATH)
    print(f"✅ Database created at: {Config.DATABASE_PATH}")
    
    # Check if database is empty
    total_reports = db.get_total_reports()
    print(f"📊 Current reports in database: {total_reports}")
    
    # Ask to seed data
    if total_reports == 0:
        response = input("\n❓ Database is empty. Seed with sample data? (y/n): ")
        if response.lower() == 'y':
            print("\n🌱 Seeding database with 30 sample reports...")
            db.seed_sample_data(num_records=30)
            print("✅ Sample data created successfully")
        else:
            print("⏭️  Skipping sample data generation")
    else:
        print("ℹ️  Database already contains data")
    
    # Initialize ML Engine
    print("\n🧠 Initializing ML Engine...")
    ml_engine = MLEngine(threshold=Config.ANOMALY_THRESHOLD)
    print("✅ ML Engine initialized")
    
    # Test ML analysis
    if total_reports > 0 or response.lower() == 'y':
        print("\n🧪 Testing ML Analysis...")
        symptom_counts = db.get_symptom_counts()
        daily_counts = db.get_daily_counts()
        
        if daily_counts:
            anomalies = ml_engine.detect_anomalies(daily_counts)
            trends = ml_engine.analyze_trends(daily_counts)
            
            print(f"\n📈 Trend: {trends['trend']} ({trends['direction']})")
            print(f"🚨 Anomalies detected: {anomalies['anomalies_detected']}")
            
            if anomalies['anomalies_detected']:
                print(f"   Total anomalies: {anomalies['total_anomalies']}")
    
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print("\n📍 Next Steps:")
    print("   1. Run: python app.py")
    print("   2. Visit: http://localhost:5000")
    print("   3. Test API endpoints")
    print("   4. Connect frontend\n")

if __name__ == '__main__':
    main()
