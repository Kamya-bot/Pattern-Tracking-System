"""
Demo Data Generator
Generates 500-1000 realistic synthetic health records with patterns, outbreaks, and clusters
"""

import sqlite3
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any


class HealthDataGenerator:
    """Generates realistic health report data"""

    SYMPTOM_CATEGORIES = {
        'respiratory': ['Cough', 'Sore Throat', 'Shortness of Breath', 'Nasal Congestion', 'Runny Nose'],
        'fever': ['Fever', 'Chills', 'Night Sweats'],
        'digestive': ['Nausea', 'Vomiting', 'Diarrhea', 'Stomach Pain', 'Loss of Appetite'],
        'pain': ['Headache', 'Body Aches', 'Muscle Pain', 'Joint Pain'],
        'fatigue': ['Fatigue', 'Weakness', 'Dizziness'],
        'skin': ['Rash', 'Skin Irritation', 'Itching'],
        'other': ['Loss of Taste', 'Loss of Smell', 'Eye Irritation']
    }

    LOCATIONS = {
        'Main Library': 0.85,
        'Student Dormitory A': 0.70,
        'Student Dormitory B': 0.65,
        'Cafeteria': 0.80,
        'Gymnasium': 0.60,
        'Lecture Hall': 0.75,
        'Computer Lab': 0.55,
        'Campus Hospital': 0.90
    }

    OUTBREAK_PATTERNS = [
        {
            'name': 'Flu Outbreak',
            'symptoms': ['Fever', 'Cough', 'Body Aches', 'Fatigue', 'Headache'],
            'severity_range': (6, 9),
            'duration_days': 7,
            'peak_locations': ['Student Dormitory A', 'Cafeteria']
        },
        {
            'name': 'Common Cold',
            'symptoms': ['Runny Nose', 'Sore Throat', 'Cough', 'Nasal Congestion'],
            'severity_range': (3, 6),
            'duration_days': 5,
            'peak_locations': ['Main Library', 'Lecture Hall']
        },
        {
            'name': 'Food Poisoning',
            'symptoms': ['Nausea', 'Vomiting', 'Diarrhea', 'Stomach Pain'],
            'severity_range': (7, 10),
            'duration_days': 2,
            'peak_locations': ['Cafeteria']
        }
    ]

    def __init__(self, num_records: int = 1000):
        self.num_records = num_records
        self.generated_reports = []
        self.start_date = datetime.now() - timedelta(days=60)

    def generate_random_symptoms(self, outbreak_pattern: Dict = None) -> List[str]:
        if outbreak_pattern:
            base = outbreak_pattern['symptoms']
            return random.sample(base, random.randint(2, len(base)))
        else:
            category = random.choice(list(self.SYMPTOM_CATEGORIES.values()))
            return random.sample(category, random.randint(1, min(4, len(category))))

    def generate_severity(self, outbreak_pattern=None):
        if outbreak_pattern:
            return random.randint(*outbreak_pattern['severity_range'])
        return max(1, min(10, int(random.gauss(5, 2))))

    def generate_location(self, outbreak_pattern=None):
        if outbreak_pattern and random.random() < 0.7:
            return random.choice(outbreak_pattern['peak_locations'])
        return random.choices(
            list(self.LOCATIONS.keys()),
            weights=list(self.LOCATIONS.values())
        )[0]

    def simulate_outbreak(self, pattern, start_day, num_cases):
        for _ in range(num_cases):
            day_offset = int(random.gauss(pattern['duration_days']/2, 2))
            report_date = self.start_date + timedelta(days=start_day + day_offset)

            if report_date > datetime.now():
                continue

            self.generated_reports.append({
                'symptoms': self.generate_random_symptoms(pattern),
                'severity': self.generate_severity(pattern),
                'location': self.generate_location(pattern),
                'notes': pattern['name'],
                'date': report_date.strftime('%Y-%m-%d')
            })

    def generate_baseline_reports(self, num_reports):
        for _ in range(num_reports):
            report_date = self.start_date + timedelta(days=random.randint(0, 59))

            self.generated_reports.append({
                'symptoms': self.generate_random_symptoms(),
                'severity': self.generate_severity(),
                'location': self.generate_location(),
                'notes': 'Normal case',
                'date': report_date.strftime('%Y-%m-%d')
            })

    def generate_all_data(self):
        print(f"Generating {self.num_records} records...")

        outbreaks = random.randint(3, 5)
        outbreak_cases = int(self.num_records * 0.4)
        baseline = self.num_records - outbreak_cases

        for _ in range(outbreaks):
            pattern = random.choice(self.OUTBREAK_PATTERNS)
            self.simulate_outbreak(pattern, random.randint(0, 50), outbreak_cases // outbreaks)

        self.generate_baseline_reports(baseline)

        print(f"Generated {len(self.generated_reports)} reports")
        return self.generated_reports

    def map_symptoms(self, symptoms):
        return (
            1 if 'Fever' in symptoms else 0,
            1 if 'Cough' in symptoms else 0,
            1 if 'Headache' in symptoms else 0,
            1 if 'Stomach Pain' in symptoms else 0,
            1 if 'Nausea' in symptoms else 0,
            1 if 'Rash' in symptoms else 0,
            1 if 'Fatigue' in symptoms else 0,
            1 if 'Body Aches' in symptoms else 0,
        )

    def save_to_database(self, db_path='database.db'):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("Clearing old data...")
        cursor.execute("DELETE FROM reports")

        print("Inserting new data...")

        for r in self.generated_reports:
            fever, cough, headache, stomach, nausea, skin, fatigue, body = self.map_symptoms(r['symptoms'])

            cursor.execute("""
                INSERT INTO reports (
                    fever, cold_cough, headache, stomach_pain,
                    nausea, skin_allergy, fatigue, body_pain,
                    additional_symptoms, location, severity, date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fever, cough, headache, stomach,
                nausea, skin, fatigue, body,
                ", ".join(r['symptoms']),
                r['location'],
                str(r['severity']),
                r['date']
            ))

        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM reports")
        count = cursor.fetchone()[0]

        conn.close()

        print(f"Saved {count} records to DB")
        return count


def main():
    print("🚀 DATA GENERATOR STARTED")

    generator = HealthDataGenerator(1000)
    generator.generate_all_data()
    generator.save_to_database()

    print("✅ DONE!")


if __name__ == "__main__":
    main()