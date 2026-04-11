#!/usr/bin/env python3

import asyncio
from app.core.database import db_manager

async def test_mongodb():
    try:
        print("Testing MongoDB connection...")
        await db_manager.connect()
        print("✅ MongoDB connected successfully!")
        
        # Test database operations
        db = db_manager.get_database()
        
        # Test health check
        if db_manager.database is not None:
            health = await db_manager.health_check()
            print(f"📊 Database Health: {health}")
        
        # Test stats
        if db_manager.database is not None:
            stats = await db_manager.get_stats()
            print(f"📈 Database Stats: {stats}")
        
        # Test basic operations
        if db_manager.database is not None:
            test_doc = {"test": "mongodb_connection", "timestamp": "2026-04-07"}
            result = await db_manager.database.test_collection.insert_one(test_doc)
            print(f"📝 Inserted test document: {result.inserted_id}")
            
            # Query test
            found = await db_manager.database.test_collection.find_one({"test": "mongodb_connection"})
            print(f"🔍 Found document: {found}")
            
            # Cleanup
            await db_manager.database.test_collection.delete_one({"test": "mongodb_connection"})
            print("🧹 Test cleanup completed")
        
        await db_manager.disconnect()
        print("✅ MongoDB test completed successfully!")
        
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_mongodb())
