import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.logging import logger

class DatabaseManager:
    """MongoDB database manager for SOC Correlation Engine"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self._connected = False
        self.mongodb_url = getattr(settings, 'MONGODB_URL', 'mongodb://127.0.0.1:27017')
        self.db_name = getattr(settings, 'DATABASE_NAME', 'soc_correlation_engine_new')
        self.connection_id = None
        self.host = getattr(settings, 'MONGODB_HOST', '127.0.0.1')
        self.port = getattr(settings, 'MONGODB_PORT', 27017)
    
    async def connect(self):
        """Connect to MongoDB with fresh connection"""
        # Force disconnect any existing connection
        await self.disconnect()
        
        max_retries = 5
        retry_delay = 2
        
        # Generate unique connection ID for this session
        import uuid
        self.connection_id = str(uuid.uuid4())[:8]
        
        logger.info(f"Attempting to connect to MongoDB at {self.host}:{self.port}")
        logger.info("If connection fails, please ensure MongoDB is running:")
        logger.info("1. Install MongoDB: https://www.mongodb.com/try/download/community")
        logger.info("2. Start MongoDB service: net start MongoDB")
        logger.info("3. Or use Docker: docker run -d -p 27017:27017 mongo")
        
        for attempt in range(max_retries):
            try:
                # Create MongoDB client with enhanced settings
                self.client = AsyncIOMotorClient(
                    self.mongodb_url,
                    serverSelectionTimeoutMS=5000,  # Reduced timeout for faster feedback
                    connectTimeoutMS=5000,
                    maxPoolSize=20,
                    retryWrites=True,
                    retryReads=True,
                    socketTimeoutMS=10000,
                    heartbeatFrequencyMS=10000
                )
                
                # Test connection with timeout
                await asyncio.wait_for(self.client.admin.command('ping'), timeout=15)
                
                # Get database
                self.database = self.client[self.db_name]
                
                # Create indexes for better performance
                await self._create_indexes()
                
                # Initialize collections with sample data if empty
                await self._initialize_collections()
                
                logger.info(f"Successfully connected to MongoDB at {self.mongodb_url} (Connection ID: {self.connection_id})")
                logger.info(f"Using database: {self.db_name}")
                self._connected = True
                return
                
            except (ConnectionFailure, asyncio.TimeoutError) as e:
                logger.warning(f"MongoDB connection attempt {attempt + 1} failed: {e}")
                if "Connection refused" in str(e) or "ECONNREFUSED" in str(e):
                    logger.error("MongoDB is not running or not accessible!")
                    logger.error("Please start MongoDB service or install MongoDB")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"Failed to connect to MongoDB after {max_retries} attempts")
                    logger.error("System will continue in fallback mode without database persistence")
                    # Set up in-memory fallback mode
                    self._setup_fallback_mode()
                    return
                    
            except Exception as e:
                logger.error(f"Database initialization failed: {e}")
                self._setup_fallback_mode()
                return
    
    def _setup_fallback_mode(self):
        """Set up fallback mode when database is unavailable"""
        logger.warning("Operating in fallback mode - database features will be limited")
        self._connected = False
        self.fallback_mode = True
        
        # Create in-memory storage for fallback mode
        self._memory_storage = {}
        
        # Create mock database with basic collection methods
        class FallbackCollection:
            def __init__(self, name, memory_storage):
                self.name = name
                self._storage = memory_storage
                if name not in self._storage:
                    self._storage[name] = []
            
            async def insert_one(self, document):
                if '_id' not in document:
                    document['_id'] = f"fallback_{len(self._storage[self.name])}"
                self._storage[self.name].append(document)
                return type('InsertResult', (), {'inserted_id': document['_id']})()
            
            async def insert_many(self, documents):
                results = []
                for doc in documents:
                    result = await self.insert_one(doc)
                    results.append(result)
                return type('InsertManyResult', (), {'inserted_ids': [r.inserted_id for r in results]})()
            
            async def find(self, filter=None):
                return FallbackCursor(self._storage[self.name])
            
            async def find_one(self, filter=None):
                docs = self._storage[self.name]
                if docs:
                    return docs[0]
                return None
            
            async def count_documents(self, filter=None):
                return len(self._storage[self.name])
            
            async def delete_many(self, filter=None):
                self._storage[self.name] = []
                return type('DeleteResult', (), {'deleted_count': len(self._storage[self.name])})()
            
            async def drop(self):
                self._storage[self.name] = []
        
        class FallbackCursor:
            def __init__(self, documents):
                self.documents = documents
                self.index = 0
            
            def __aiter__(self):
                return self
            
            async def __anext__(self):
                if self.index >= len(self.documents):
                    raise StopAsyncIteration
                doc = self.documents[self.index]
                self.index += 1
                return doc
            
            async def to_list(self, length=None):
                if length:
                    return self.documents[:length]
                return self.documents
        
        # Create mock database with collections
        class FallbackDatabase:
            def __init__(self, memory_storage):
                self._storage = memory_storage
                self._collections = {}
            
            def __getitem__(self, name):
                if name not in self._collections:
                    self._collections[name] = FallbackCollection(name, self._storage)
                return self._collections[name]
            
            def __getattr__(self, name):
                return self[name]
        
        self.database = FallbackDatabase(self._memory_storage)
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        try:
            if self.client:
                self.client.close()
                logger.info(f"MongoDB disconnected (Connection ID: {self.connection_id})")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
        finally:
            self._connected = False
            self.connection_id = None
    
    def get_database(self):
        """Get database instance"""
        if not self._connected:
            # Return fallback database instead of raising error
            if not hasattr(self, 'fallback_mode'):
                self._setup_fallback_mode()
            return self.database
        return self.database
    
    def get_mongodb_db(self):
        """Get MongoDB database instance (for compatibility)"""
        return self.get_database()
    
    def get_collection(self, collection_name: str):
        """Get collection from database"""
        db = self.get_database()
        if hasattr(db, 'get_collection'):
            return db.get_collection(collection_name)
        elif hasattr(db, collection_name):
            return getattr(db, collection_name)
        else:
            # Fallback to creating collection if it doesn't exist
            if hasattr(db, '__getitem__'):
                return db[collection_name]
            else:
                raise AttributeError(f"Collection '{collection_name}' not found in database")
    
    async def health_check(self):
        """Check database health"""
        health_status = {
            "mongodb": self._connected,
            "timestamp": datetime.utcnow().isoformat(),
            "database": self.db_name,
            "collections": {},
            "fallback_mode": getattr(self, 'fallback_mode', False)
        }
        
        if self._connected and self.database is not None and not getattr(self, 'fallback_mode', False):
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
        elif getattr(self, 'fallback_mode', False):
            health_status["status"] = "fallback_mode"
            health_status["message"] = "Operating in fallback mode - using in-memory storage"
        
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
        # Try to connect if not connected
        try:
            await db_manager.connect()
        except Exception as e:
            logger.warning(f"Database connection failed: {e}")
            # Return fallback database
            return db_manager
    return db_manager

async def init_db():
    """Initialize database connection"""
    await db_manager.connect()
    return db_manager
