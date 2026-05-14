import pathlib
import sqlite3

conn = sqlite3.connect(pathlib.Path(__file__).parent/"agent_persistence.db")

cursor = conn.cursor()

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS conversations (
        conversation_id INTEGER PRIMARY KEY NOT NULL,
        summary VARCHAR,
        model VARCHAR NOT NULL,
        total_tokens INT DEFAULT 0,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ended_at TIMESTAMP DEFAULT NULL,
        status TEXT DEFAULT 'active',
        approx_cost REAL DEFAULT 0.0
        )
    '''
    )

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS messages (
        message_id INTEGER PRIMARY KEY NOT NULL,
        conversation_id INTEGER REFERENCES conversations(conversation_id),
        role VARCHAR,
        content VARCHAR NOT NULL,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''
    )