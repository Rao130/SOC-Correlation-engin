import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def verify_mongodb_status():
    try:
        from app.core.database import DatabaseManager
        
        print('🔍 Verifying MongoDB status...')
        
        db = DatabaseManager()
        await db.connect()
        
        # Get database and check collections
        database = db.get_database()
        db_name = database.name
        print(f'📋 Database: {db_name}')
        
        # List all collections
        collections = await database.list_collection_names()
        print(f'📋 Collections: {collections}')
        
        # Check each collection count
        for collection_name in collections:
            collection = database[collection_name]
            count = await collection.count_documents({})
            print(f'  📊 {collection_name}: {count} documents')
            
            # Get sample documents to see timestamps
            if count > 0:
                sample = await collection.find_one({})
                if sample and 'timestamp' in sample:
                    print(f'    ⏰ Sample timestamp: {sample["timestamp"]}')
        
        await db.disconnect()
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_mongodb_status())
