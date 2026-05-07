import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def force_delete_mongodb():
    try:
        from app.core.database import DatabaseManager
        
        print('🔥 FORCE DELETING MONGODB DATA...')
        
        db = DatabaseManager()
        await db.connect()
        
        # Get database
        database = db.get_database()
        db_name = database.name
        print(f'📋 Database: {db_name}')
        
        # List all collections
        collections = await database.list_collection_names()
        print(f'📋 Collections to delete: {collections}')
        
        # Delete each collection individually
        for collection_name in collections:
            collection = database[collection_name]
            count_before = await collection.count_documents({})
            print(f'  🗑️ Deleting {collection_name} ({count_before} documents)...')
            
            # Delete all documents
            result = await collection.delete_many({})
            print(f'  ✅ Deleted {result.deleted_count} documents from {collection_name}')
            
            # Verify deletion
            count_after = await collection.count_documents({})
            print(f'  🔍 Remaining in {collection_name}: {count_after}')
        
        # Drop the entire database as backup
        print(f'💥 Dropping entire database: {db_name}')
        try:
            result = await database.command('dropDatabase')
            print(f'  ✅ Database drop result: {result}')
        except Exception as e:
            print(f'  ⚠️ Database drop error: {e}')
        
        # Verify everything is gone
        try:
            remaining_collections = await database.list_collection_names()
            print(f'📋 Remaining collections: {remaining_collections}')
            
            # If collections still exist, delete them again
            if remaining_collections:
                print('🔄 Collections still exist, deleting again...')
                for collection_name in remaining_collections:
                    collection = database[collection_name]
                    await collection.drop()
                    print(f'  ✅ Dropped collection: {collection_name}')
        except Exception as e:
            print(f'✅ Database appears to be completely cleared: {e}')
        
        await db.disconnect()
        
        print('🎉 MongoDB force deletion completed!')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(force_delete_mongodb())
