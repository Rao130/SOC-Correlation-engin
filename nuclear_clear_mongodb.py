import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def nuclear_clear_mongodb():
    """Nuclear option to completely wipe MongoDB"""
    try:
        print("🔥 NUCLEAR CLEAR - COMPLETE MONGODB WIPE")
        print(f"⏰ Started at: {datetime.now()}")
        
        # Try direct MongoDB connection
        await direct_mongodb_wipe()
        
        print("🎉 NUCLEAR CLEAR COMPLETED!")
        print(f"⏰ Completed at: {datetime.now()}")
        
    except Exception as e:
        print(f"❌ Nuclear clear error: {e}")
        import traceback
        traceback.print_exc()

async def direct_mongodb_wipe():
    """Direct MongoDB wipe using motor"""
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        
        print("🔌 Connecting to MongoDB directly...")
        
        # Direct connection to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        
        # Get database
        db = client.soc_correlation_engine
        print(f"📋 Database: soc_correlation_engine")
        
        # List all collections
        collections = await db.list_collection_names()
        print(f"📋 Found collections: {collections}")
        
        # Drop each collection individually
        for collection_name in collections:
            collection = db[collection_name]
            count_before = await collection.count_documents({})
            print(f"🗑️ Dropping collection {collection_name} ({count_before} documents)...")
            
            # Drop the entire collection
            await collection.drop()
            print(f"✅ Dropped {collection_name}")
        
        # Drop the entire database as backup
        print("💥 Dropping entire database...")
        await client.drop_database("soc_correlation_engine")
        print("✅ Database dropped")
        
        # Verify complete wipe
        print("🔍 Verifying complete wipe...")
        try:
            collections_after = await db.list_collection_names()
            print(f"📋 Collections after wipe: {collections_after}")
        except Exception as e:
            print(f"✅ Database completely wiped: {e}")
        
        # Close connection
        client.close()
        print("🔌 MongoDB connection closed")
        
    except Exception as e:
        print(f"❌ Direct MongoDB wipe error: {e}")
        # Try alternative method
        await alternative_wipe()

async def alternative_wipe():
    """Alternative wipe method using our database manager"""
    try:
        from app.core.database import DatabaseManager
        
        print("🔄 Trying alternative wipe method...")
        
        db = DatabaseManager()
        await db.connect()
        
        database = db.get_database()
        db_name = database.name
        print(f"📋 Database: {db_name}")
        
        # Get all collections
        collections = await database.list_collection_names()
        print(f"📋 Collections to wipe: {collections}")
        
        # Delete all documents from each collection
        for collection_name in collections:
            collection = database[collection_name]
            count_before = await collection.count_documents({})
            print(f"🗑️ Deleting all from {collection_name} ({count_before} docs)...")
            
            # Delete all documents
            result = await collection.delete_many({})
            print(f"✅ Deleted {result.deleted_count} from {collection_name}")
            
            # Verify deletion
            count_after = await collection.count_documents({})
            print(f"🔍 Remaining in {collection_name}: {count_after}")
            
            # Drop the collection entirely
            await collection.drop()
            print(f"💥 Dropped collection {collection_name}")
        
        # Drop database
        print("💥 Dropping database...")
        await database.command('dropDatabase')
        print("✅ Database dropped")
        
        await db.disconnect()
        
    except Exception as e:
        print(f"❌ Alternative wipe error: {e}")

if __name__ == "__main__":
    print("🔥 NUCLEAR MONGODB CLEAR - SOC Correlation Engine")
    print("=" * 60)
    print("⚠️  WARNING: This will COMPLETELY WIPE MongoDB!")
    print("=" * 60)
    
    asyncio.run(nuclear_clear_mongodb())
