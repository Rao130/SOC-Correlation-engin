from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.file_database import FileDatabase

logger = setup_logging()

class DatabaseManager:
    """Simple file-based database manager"""
    
    def __init__(self):
        self.file_db = FileDatabase()
        self._connected = False
    
    async def connect(self):
        """Connect to file database"""
        try:
            self.file_db = FileDatabase()
            logger.info("Connected to file database successfully")
            self._connected = True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            self.file_db = FileDatabase()
            self._connected = True
            logger.info("Using file database")
    
    async def disconnect(self):
        """Disconnect from database"""
        try:
            # File database doesn't need explicit disconnect
            logger.info("File database disconnected")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
        self._connected = False
    
    def get_database(self):
        """Get database instance"""
        if not self._connected:
            raise RuntimeError("Database not connected")
        return self.file_db
    
    async def health_check(self):
        """Check database health"""
        health_status = {
            "file_database": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        return health_status
    
    async def cleanup_old_data(self):
        """Clean up old data based on retention policies"""
        try:
            # Clean up old alerts (older than 90 days)
            alerts_collection = self.mongodb_db.alerts
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            result = await alerts_collection.delete_many({
                "timestamp": {"$lt": cutoff_date},
                "status": {"$in": ["resolved", "false_positive"]}
            })
            logger.info(f"Cleaned up {result.deleted_count} old alerts")
            
            # Clean up old reputation data (older than 180 days for benign entities)
            reputation_collection = self.mongodb_db.reputation
            cutoff_date = datetime.utcnow() - timedelta(days=180)
            result = await reputation_collection.delete_many({
                "expiresAt": {"$lt": cutoff_date}
            })
            logger.info(f"Cleaned up {result.deleted_count} old reputation entries")
            
        except Exception as e:
            logger.error(f"Error during data cleanup: {e}")

# Global database manager instance
db_manager = DatabaseManager()

async def init_db():
    """Initialize database connections"""
    await db_manager.connect()
    return db_manager

async def get_db():
    """Get database dependency for FastAPI"""
    return db_manager

async def close_db():
    """Close database connections"""
    await db_manager.disconnect()

# Mock classes for demo without database
class MockDatabase:
    """Mock database for demo purposes"""
    
    def __init__(self):
        self.collections = {
            'alerts': MockCollection(),
            'reputation': MockCollection(),
            'correlation_groups': MockCollection()
        }
    
    def __getattr__(self, name):
        if name in self.collections:
            return self.collections[name]
        return MockCollection()

class MockCollection:
    """Mock MongoDB collection for demo purposes"""
    
    def __init__(self):
        self.data = []
    
    async def find(self, query=None):
        return MockCursor(self.data)
    
    async def find_one(self, query=None):
        return self.data[0] if self.data else None
    
    async def insert_one(self, document):
        document['_id'] = f"mock_{len(self.data)}"
        self.data.append(document)
        return MockInsertResult()
    
    async def update_one(self, query, update):
        return MockUpdateResult()
    
    async def delete_one(self, query):
        return MockDeleteResult()
    
    async def count_documents(self, query=None):
        return len(self.data)
    
    async def aggregate(self, pipeline):
        return []
    
    def create_index(self, *args, **kwargs):
        pass

class MockCursor:
    """Mock cursor for database queries"""
    
    def __init__(self, data):
        self.data = data
    
    def sort(self, *args):
        return self
    
    def skip(self, count):
        return MockCursor(self.data[count:])
    
    def limit(self, count):
        return MockCursor(self.data[:count])
    
    async def to_list(self, length=None):
        return self.data[:length] if length else self.data

class MockInsertResult:
    """Mock insert result"""
    def __init__(self):
        self.inserted_id = f"mock_id_{hash('insert')}"

class MockUpdateResult:
    """Mock update result"""
    def __init__(self):
        self.modified_count = 1

class MockDeleteResult:
    """Mock delete result"""
    def __init__(self):
        self.deleted_count = 1

class MockRedis:
    """Mock Redis client for demo purposes"""
    
    async def ping(self):
        return True
    
    async def get(self, key):
        return None
    
    async def set(self, key, value, ex=None):
        return True
    
    async def delete(self, key):
        return True
    
    async def close(self):
        pass
