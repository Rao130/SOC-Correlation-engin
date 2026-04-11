from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.logging import setup_logging

logger = setup_logging()

class DatabaseManager:
    """MongoDB database manager for SOC Correlation Engine"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self._connected = False
        self.mongodb_url = getattr(settings, 'MONGODB_URL', 'mongodb://localhost:27017')
        self.db_name = getattr(settings, 'DATABASE_NAME', 'soc_correlation_engine')
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            # Create MongoDB client
            self.client = AsyncIOMotorClient(
                self.mongodb_url,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                maxPoolSize=10,
                retryWrites=True
            )
            
            # Test connection
            await self.client.admin.command('ping')
            
            # Get database
            self.database = self.client[self.db_name]
            
            # Create indexes for better performance
            await self._create_indexes()
            
            # Initialize collections with sample data if empty
            await self._initialize_collections()
            
            logger.info(f"Connected to MongoDB at {self.mongodb_url}")
            self._connected = True
            
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {e}")
            # Fallback to in-memory or raise exception
            raise Exception(f"Could not connect to MongoDB: {e}")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        try:
            if self.client:
                self.client.close()
                logger.info("MongoDB disconnected")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
        finally:
            self._connected = False
    
    def get_database(self):
        """Get database instance"""
        if not self._connected:
            raise RuntimeError("Database not connected")
        return self.database
    
    def get_mongodb_db(self):
        """Get MongoDB database instance (for compatibility)"""
        return self.get_database()
    
    async def health_check(self):
        """Check database health"""
        health_status = {
            "mongodb": self._connected,
            "timestamp": datetime.utcnow().isoformat(),
            "database": self.db_name,
            "collections": {}
        }
        
        if self._connected and self.database is not None:
            try:
                # Check each collection
                collections = ['alerts', 'correlation_groups', 'reputation', 'logs']
                for collection_name in collections:
                    try:
                        count = await self.database[collection_name].count_documents({})
                        health_status["collections"][collection_name] = {
                            "exists": True,
                            "count": count
                        }
                    except Exception as e:
                        health_status["collections"][collection_name] = {
                            "exists": False,
                            "error": str(e)
                        }
            except Exception as e:
                health_status["collections_error"] = str(e)
        
        return health_status
    
    async def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Alerts collection indexes
            await self.database.alerts.create_index([("timestamp", -1)])
            await self.database.alerts.create_index([("severity", 1)])
            await self.database.alerts.create_index([("status", 1)])
            await self.database.alerts.create_index([("category", 1)])
            await self.database.alerts.create_index([("title", "text"), ("description", "text")])
            
            # Correlation groups indexes
            await self.database.correlation_groups.create_index([("created_at", -1)])
            await self.database.correlation_groups.create_index([("correlation_type", 1)])
            await self.database.correlation_groups.create_index([("status", 1)])
            await self.database.correlation_groups.create_index([("name", "text"), ("description", "text")])
            
            # Reputation collection indexes
            await self.database.reputation.create_index([("entity", 1)])
            await self.database.reputation.create_index([("entity_type", 1)])
            await self.database.reputation.create_index([("risk_level", 1)])
            await self.database.reputation.create_index([("last_checked", -1)])
            
            # Logs collection indexes
            await self.database.logs.create_index([("timestamp", -1)])
            await self.database.logs.create_index([("level", 1)])
            await self.database.logs.create_index([("category", 1)])
            await self.database.logs.create_index([("message", "text")])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Failed to create some indexes: {e}")
    
    async def _initialize_collections(self):
        """Initialize collections with basic structure if empty"""
        try:
            # Check if database is completely empty
            collections = await self.database.list_collection_names()
            
            if not collections:
                logger.info("Database is empty, creating initial collections")
                
                # Create empty collections
                await self.database.create_collection("alerts")
                await self.database.create_collection("correlation_groups")
                await self.database.create_collection("reputation")
                await self.database.create_collection("logs")
                
                logger.info("Initial collections created")
            
        except Exception as e:
            logger.warning(f"Failed to initialize collections: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self._connected or self.database is None:
            return {"error": "Database not connected"}
        
        try:
            stats = {
                "database": self.db_name,
                "collections": {},
                "total_documents": 0
            }
            
            collections = await self.database.list_collection_names()
            for collection_name in collections:
                count = await self.database[collection_name].count_documents({})
                stats["collections"][collection_name] = count
                stats["total_documents"] += count
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {"error": str(e)}

# Singleton instance
db_manager = DatabaseManager()

async def get_db():
    """Dependency function to get database instance"""
    if not db_manager._connected:
        raise RuntimeError("Database not connected")
    return db_manager

async def init_db():
    """Initialize database connection"""
    await db_manager.connect()
    return db_manager
