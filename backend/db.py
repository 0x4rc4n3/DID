# backend/db.py
import sqlite3
import json
import os

class Database:
    def __init__(self, db_path="did_blockchain.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # DID documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS did_documents (
                did TEXT PRIMARY KEY,
                document TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Blockchain table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blockchain (
                block_index INTEGER PRIMARY KEY,
                block_data TEXT NOT NULL,
                block_hash TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_did_document(self, did, document):
        """Save DID document to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT OR REPLACE INTO did_documents (did, document) VALUES (?, ?)',
            (did, json.dumps(document))
        )
        
        conn.commit()
        conn.close()
    
    def get_did_document(self, did):
        """Retrieve DID document from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT document FROM did_documents WHERE did = ?', (did,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    
    def save_block(self, block):
        """Save block to database"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO blockchain (block_index, block_data, block_hash, previous_hash, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                block['index'],
                json.dumps(block['data']),
                block['hash'],
                block['previous_hash'],
                block['timestamp']
            ))
            
            conn.commit()
        except sqlite3.OperationalError as e:
            print(f"Database error in save_block: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def get_blockchain(self):
        """Retrieve entire blockchain from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM blockchain ORDER BY block_index')
        blocks = cursor.fetchall()
        
        conn.close()
        
        return [{
            'index': block[0],
            'data': json.loads(block[1]),
            'hash': block[2],
            'previous_hash': block[3],
            'timestamp': block[4]
        } for block in blocks]
    
    def did_exists(self, did):
        """Check if DID already exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM did_documents WHERE did = ?', (did,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None