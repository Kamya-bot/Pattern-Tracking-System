"""
Database models and schema for Pattern Tracking System
Supports both PostgreSQL (production) and SQLite (development)
"""
import os
import hashlib
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

DATABASE_URL = os.environ.get('DATABASE_URL')
USE_POSTGRES = bool(DATABASE_URL)

if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras
else:
    import sqlite3


class Database:
    """Database handler — auto-switches between PostgreSQL and SQLite"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path
        self.use_postgres = USE_POSTGRES
        self.init_database()

    # ── Connection ─────────────────────────────────────────────────────────────

    def get_connection(self):
        if self.use_postgres:
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
            return conn
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn

    def _ph(self):
        """Return correct placeholder: %s for Postgres, ? for SQLite"""
        return '%s' if self.use_postgres else '?'

    # ── Init ───────────────────────────────────────────────────────────────────

    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if self.use_postgres:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'admin'
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id SERIAL PRIMARY KEY,
                    fever INTEGER DEFAULT 0,
                    cold_cough INTEGER DEFAULT 0,
                    headache INTEGER DEFAULT 0,
                    stomach_pain INTEGER DEFAULT 0,
                    nausea INTEGER DEFAULT 0,
                    skin_allergy INTEGER DEFAULT 0,
                    fatigue INTEGER DEFAULT 0,
                    body_pain INTEGER DEFAULT 0,
                    additional_symptoms TEXT,
                    location TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics_cache (
                    id SERIAL PRIMARY KEY,
                    cache_key TEXT UNIQUE NOT NULL,
                    cache_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'admin'
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fever INTEGER DEFAULT 0,
                    cold_cough INTEGER DEFAULT 0,
                    headache INTEGER DEFAULT 0,
                    stomach_pain INTEGER DEFAULT 0,
                    nausea INTEGER DEFAULT 0,
                    skin_allergy INTEGER DEFAULT 0,
                    fatigue INTEGER DEFAULT 0,
                    body_pain INTEGER DEFAULT 0,
                    additional_symptoms TEXT,
                    location TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    date TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    cache_data TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL
                )
            ''')

        # Insert default admin if none exists
        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()
        existing = result['count'] if isinstance(result, dict) else result[0]

        if existing == 0:
            default_user = os.environ.get("DEFAULT_ADMIN_USER", "admin")
            default_pass = os.environ.get("DEFAULT_ADMIN_PASS", "changeme")
            hashed = hashlib.sha256(default_pass.encode()).hexdigest()
            ph = self._ph()
            cursor.execute(
                f"INSERT INTO users (username, password, role) VALUES ({ph}, {ph}, 'admin')",
                (default_user, hashed)
            )

        conn.commit()
        conn.close()
        db_type = "PostgreSQL" if self.use_postgres else "SQLite"
        print(f"✅ Database initialized successfully ({db_type})")

    # ── Auth ───────────────────────────────────────────────────────────────────

    def get_user(self, username: str, password: str):
        hashed = hashlib.sha256(password.encode()).hexdigest()
        ph = self._ph()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM users WHERE username={ph} AND password={ph}",
            (username, hashed)
        )
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    # ── Reports ────────────────────────────────────────────────────────────────

    def get_total_reports(self) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM reports")
        result = cursor.fetchone()
        conn.close()
        if isinstance(result, dict):
            return result['count'] or 0
        return result[0] if result else 0

    def get_symptom_counts(self) -> Dict[str, int]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                SUM(fever)         as fever,
                SUM(cold_cough)    as cold_cough,
                SUM(headache)      as headache,
                SUM(stomach_pain)  as stomach_pain,
                SUM(nausea)        as nausea,
                SUM(skin_allergy)  as skin_allergy,
                SUM(fatigue)       as fatigue,
                SUM(body_pain)     as body_pain
            FROM reports
        """)
        row = cursor.fetchone()
        conn.close()
        if not row:
            return {}
        row = dict(row)
        return {k: int(row[k] or 0) for k in ['fever','cold_cough','headache','stomach_pain','nausea','skin_allergy','fatigue','body_pain']}

    def get_location_counts(self) -> Dict[str, int]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT location, COUNT(*) as count FROM reports GROUP BY location")
        rows = cursor.fetchall()
        conn.close()
        return {row['location']: row['count'] for row in rows}

    def get_severity_counts(self) -> Dict[str, int]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT severity, COUNT(*) as count FROM reports GROUP BY severity")
        rows = cursor.fetchall()
        conn.close()
        return {row['severity']: row['count'] for row in rows}

    def get_daily_counts(self, days: int = 14) -> List[Dict]:
        ph = self._ph()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT date, COUNT(*) as count
            FROM reports
            GROUP BY date
            ORDER BY date DESC
            LIMIT {ph}
        """, (days,))
        rows = cursor.fetchall()
        conn.close()
        return [{'date': row['date'], 'count': row['count']} for row in rows]

    def get_reports_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        ph = self._ph()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f'SELECT * FROM reports WHERE date BETWEEN {ph} AND {ph} ORDER BY timestamp DESC',
            (start_date, end_date)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def insert_report(self, report_data: Dict) -> int:
        ph = self._ph()
        conn = self.get_connection()
        cursor = conn.cursor()

        if self.use_postgres:
            cursor.execute(f'''
                INSERT INTO reports (
                    fever, cold_cough, headache, stomach_pain,
                    nausea, skin_allergy, fatigue, body_pain,
                    additional_symptoms, location, severity, date
                ) VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph})
                RETURNING id
            ''', (
                report_data.get('fever', 0),
                report_data.get('cold_cough', 0),
                report_data.get('headache', 0),
                report_data.get('stomach_pain', 0),
                report_data.get('nausea', 0),
                report_data.get('skin_allergy', 0),
                report_data.get('fatigue', 0),
                report_data.get('body_pain', 0),
                report_data.get('additional_symptoms', '')[:500],
                str(report_data.get('location', ''))[:100],
                report_data.get('severity', 'Low').capitalize(),
                report_data.get('date', datetime.now().strftime('%Y-%m-%d'))
            ))
            report_id = cursor.fetchone()['id']
        else:
            cursor.execute(f'''
                INSERT INTO reports (
                    fever, cold_cough, headache, stomach_pain,
                    nausea, skin_allergy, fatigue, body_pain,
                    additional_symptoms, location, severity, date
                ) VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph})
            ''', (
                report_data.get('fever', 0),
                report_data.get('cold_cough', 0),
                report_data.get('headache', 0),
                report_data.get('stomach_pain', 0),
                report_data.get('nausea', 0),
                report_data.get('skin_allergy', 0),
                report_data.get('fatigue', 0),
                report_data.get('body_pain', 0),
                report_data.get('additional_symptoms', '')[:500],
                str(report_data.get('location', ''))[:100],
                report_data.get('severity', 'Low').capitalize(),
                report_data.get('date', datetime.now().strftime('%Y-%m-%d'))
            ))
            report_id = cursor.lastrowid

        conn.commit()
        conn.close()
        self.clear_cache()
        return report_id

    def get_all_reports(self, limit: Optional[int] = None) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        if limit:
            ph = self._ph()
            cursor.execute(
                f'SELECT * FROM reports ORDER BY timestamp DESC LIMIT {ph}',
                (limit,)
            )
        else:
            cursor.execute('SELECT * FROM reports ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def seed_sample_data(self, num_records: int = 30):
        """Seed database with sample data — development only"""
        locations  = ['North Hostel', 'South Hostel', 'East Hostel', 'West Hostel', 'Main Campus']
        severities = ['Low', 'Moderate', 'High']
        symptom_keys = ['fever','cold_cough','headache','stomach_pain','nausea','skin_allergy','fatigue','body_pain']
        ph = self._ph()
        conn = self.get_connection()
        cursor = conn.cursor()

        for i in range(num_records):
            date     = (datetime.now() - timedelta(days=random.randint(0, 14))).strftime('%Y-%m-%d')
            symptoms = {k: random.choice([0, 0, 1]) for k in symptom_keys}
            cursor.execute(f'''
                INSERT INTO reports (
                    fever, cold_cough, headache, stomach_pain,
                    nausea, skin_allergy, fatigue, body_pain,
                    additional_symptoms, location, severity, date
                ) VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph})
            ''', (
                symptoms['fever'], symptoms['cold_cough'],
                symptoms['headache'], symptoms['stomach_pain'],
                symptoms['nausea'], symptoms['skin_allergy'],
                symptoms['fatigue'], symptoms['body_pain'],
                '', random.choice(locations), random.choice(severities), date
            ))

        conn.commit()
        conn.close()
        self.clear_cache()
        print(f"✅ Seeded {num_records} sample records")

    def clear_cache(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM analytics_cache')
        conn.commit()
        conn.close()