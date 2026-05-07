"""
System Data Cleanup Script
Clears all memory data and resets system state
"""

import asyncio
import sys
import os
import shutil
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def clear_system_data():
    """Clear all system data and reset state"""
    try:
        print("🗑️ Starting complete system data cleanup...")
        print(f"⏰ Started at: {datetime.now()}")
        
        # 1. Clear database collections
        print("\n📊 Step 1: Clearing database collections...")
        await clear_database()
        
        # 2. Clear log files
        print("\n📝 Step 2: Clearing log files...")
        clear_log_files()
        
        # 3. Clear temporary files
        print("\n🗂️ Step 3: Clearing temporary files...")
        clear_temp_files()
        
        # 4. Reset memory caches
        print("\n🧠 Step 4: Resetting memory caches...")
        reset_memory_caches()
        
        print("\n✅ System data cleanup completed successfully!")
        print(f"⏰ Completed at: {datetime.now()}")
        print("🚀 System is ready for fresh start with new data!")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()

async def clear_database():
    """Clear all database collections"""
    try:
        from app.core.database import DatabaseManager
        
        db = DatabaseManager()
        await db.connect()
        
        database = db.get_database()
        collections = await database.list_collection_names()
        
        for collection_name in collections:
            await database.drop_collection(collection_name)
            print(f"  ✅ Dropped: {collection_name}")
        
        await db.disconnect()
        print("  🎉 Database cleared!")
        
    except Exception as e:
        print(f"  ❌ Database error: {e}")

def clear_log_files():
    """Clear system log files"""
    log_files = [
        'app.log',
        'security.log',
        'correlation.log',
        'system.log'
    ]
    
    for log_file in log_files:
        try:
            if os.path.exists(log_file):
                with open(log_file, 'w') as f:
                    f.write(f"# Log cleared at {datetime.now()}\n")
                print(f"  ✅ Cleared: {log_file}")
        except Exception as e:
            print(f"  ⚠️ Could not clear {log_file}: {e}")

def clear_temp_files():
    """Clear temporary files and caches"""
    temp_dirs = [
        'temp',
        'cache',
        'logs',
        '__pycache__'
    ]
    
    for temp_dir in temp_dirs:
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                os.makedirs(temp_dir, exist_ok=True)
                print(f"  ✅ Cleared: {temp_dir}/")
        except Exception as e:
            print(f"  ⚠️ Could not clear {temp_dir}: {e}")

def reset_memory_caches():
    """Reset in-memory caches and states"""
    try:
        # Clear any pickle files
        import glob
        pickle_files = glob.glob('*.pkl')
        for pkl_file in pickle_files:
            try:
                os.remove(pkl_file)
                print(f"  ✅ Removed: {pkl_file}")
            except Exception as e:
                print(f"  ⚠️ Could not remove {pkl_file}: {e}")
        
        # Clear any JSON cache files
        json_files = glob.glob('*.json')
        for json_file in json_files:
            if json_file not in ['package.json', 'tsconfig.json']:
                try:
                    os.remove(json_file)
                    print(f"  ✅ Removed: {json_file}")
                except Exception as e:
                    print(f"  ⚠️ Could not remove {json_file}: {e}")
        
        print("  🧠 Memory caches reset!")
        
    except Exception as e:
        print(f"  ⚠️ Memory reset error: {e}")

if __name__ == "__main__":
    print("🔧 SOC Correlation Engine - System Data Cleanup")
    print("=" * 50)
    
    asyncio.run(clear_system_data())
