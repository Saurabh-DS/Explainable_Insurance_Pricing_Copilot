import sqlite3
import os

def init_telemetry_db():
    db_path = 'database/quotes.db'
    os.makedirs('database', exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create telemetry table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        request_id TEXT,
        endpoint TEXT,
        total_latency_ms REAL,
        pricing_latency_ms REAL,
        guidelines_latency_ms REAL,
        similarity_latency_ms REAL,
        llm_latency_ms REAL,
        status TEXT,
        input_data TEXT
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Telemetry table initialized in database/quotes.db")

if __name__ == "__main__":
    init_telemetry_db()
