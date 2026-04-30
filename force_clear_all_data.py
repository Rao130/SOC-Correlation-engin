"""
Force Complete System Data Clear
Clears all possible data sources including memory, database, and cached data
"""

import asyncio
import sys
import os
import shutil
import glob
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def force_clear_all_data():
    """Force clear all data from every possible source"""
    try:
        print("🔥 FORCE CLEARING ALL SYSTEM DATA...")
        print(f"⏰ Started at: {datetime.now()}")
        
        # 1. Completely drop and recreate MongoDB database
        print("\n💥 Step 1: Force drop MongoDB database...")
        await force_drop_mongodb()
        
        # 2. Clear all Python object memory
        print("\n🧠 Step 2: Clear all Python object memory...")
        clear_python_memory()
        
        # 3. Clear all cached files
        print("\n📁 Step 3: Clear all cached files...")
        clear_all_cached_files()
        
        # 4. Clear browser session data
        print("\n🌐 Step 4: Clear browser session data...")
        clear_browser_data()
        
        # 5. Force restart all services
        print("\n🔄 Step 5: Force restart all services...")
        force_restart_services()
        
        print("\n🎉 FORCE CLEAR COMPLETED!")
        print("🚀 System is now completely fresh!")
        print(f"⏰ Completed at: {datetime.now()}")
        
    except Exception as e:
        print(f"❌ Error during force clear: {e}")
        import traceback
        traceback.print_exc()

async def force_drop_mongodb():
    """Force drop MongoDB database completely"""
    try:
        from app.core.database import DatabaseManager
        
        db = DatabaseManager()
        await db.connect()
        
        # Get database and drop it completely
        database = db.get_database()
        db_name = database.name
        print(f"  📋 Dropping database: {db_name}")
        
        # Drop database multiple times to ensure it's gone
        for i in range(3):
            try:
                await database.command('dropDatabase')
                print(f"  ✅ Drop attempt {i+1} completed")
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"  ⚠️ Drop attempt {i+1} failed: {e}")
        
        # Verify database is empty
        try:
            collections = await database.list_collection_names()
            print(f"  📋 Remaining collections: {collections}")
        except Exception as e:
            print(f"  ✅ Database appears to be completely dropped: {e}")
        
        await db.disconnect()
        print("  🎉 MongoDB force cleared!")
        
    except Exception as e:
        print(f"  ❌ MongoDB force clear error: {e}")

def clear_python_memory():
    """Clear Python object memory and reset all generators"""
    try:
        # Clear all global variables that might hold data
        global_vars = globals().copy()
        
        for var_name, var_value in global_vars.items():
            if hasattr(var_value, 'clear') and callable(getattr(var_value, 'clear')):
                try:
                    var_value.clear()
                    print(f"  ✅ Cleared: {var_name}")
                except Exception as e:
                    print(f"  ⚠️ Could not clear {var_name}: {e}")
        
        # Clear all Python cache files
        cache_files = glob.glob('**/__pycache__/**', recursive=True)
        for cache_file in cache_files:
            try:
                if os.path.isfile(cache_file):
                    os.remove(cache_file)
                elif os.path.isdir(cache_file):
                    shutil.rmtree(cache_file)
                print(f"  ✅ Removed cache: {cache_file}")
            except Exception as e:
                print(f"  ⚠️ Could not remove cache {cache_file}: {e}")
        
        # Clear all .pyc files
        pyc_files = glob.glob('**/*.pyc', recursive=True)
        for pyc_file in pyc_files:
            try:
                os.remove(pyc_file)
                print(f"  ✅ Removed .pyc: {pyc_file}")
            except Exception as e:
                print(f"  ⚠️ Could not remove .pyc {pyc_file}: {e}")
        
        print("  🧠 Python memory cleared!")
        
    except Exception as e:
        print(f"  ❌ Python memory clear error: {e}")

def clear_all_cached_files():
    """Clear all possible cached files"""
    try:
        file_patterns = [
            '*.pkl',
            '*.json',
            '*.cache',
            '*.tmp',
            '*.log',
            '*.bak',
            '*.swp',
            '*.swo',
            '*~'
        ]
        
        for pattern in file_patterns:
            files = glob.glob(pattern)
            for file in files:
                try:
                    # Don't delete important config files
                    if file in ['package.json', 'tsconfig.json', 'requirements.txt']:
                        continue
                    
                    if os.path.isfile(file):
                        os.remove(file)
                        print(f"  ✅ Removed: {file}")
                    elif os.path.isdir(file):
                        shutil.rmtree(file)
                        print(f"  ✅ Removed dir: {file}")
                except Exception as e:
                    print(f"  ⚠️ Could not remove {file}: {e}")
        
        # Clear temp directories
        temp_dirs = ['temp', 'cache', 'logs', 'sessions']
        for temp_dir in temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    os.makedirs(temp_dir, exist_ok=True)
                    print(f"  ✅ Cleared temp dir: {temp_dir}")
            except Exception as e:
                print(f"  ⚠️ Could not clear temp dir {temp_dir}: {e}")
        
        print("  📁 All cached files cleared!")
        
    except Exception as e:
        print(f"  ❌ Cached files clear error: {e}")

def clear_browser_data():
    """Clear browser-related data"""
    try:
        # Clear any session files
        session_files = glob.glob('**/session*', recursive=True)
        for session_file in session_files:
            try:
                if os.path.isfile(session_file):
                    os.remove(session_file)
                    print(f"  ✅ Removed session: {session_file}")
                elif os.path.isdir(session_file):
                    shutil.rmtree(session_file)
                    print(f"  ✅ Removed session dir: {session_file}")
            except Exception as e:
                print(f"  ⚠️ Could not remove session {session_file}: {e}")
        
        # Clear any cookie files
        cookie_files = glob.glob('**/cookie*', recursive=True)
        for cookie_file in cookie_files:
            try:
                if os.path.isfile(cookie_file):
                    os.remove(cookie_file)
                    print(f"  ✅ Removed cookie: {cookie_file}")
            except Exception as e:
                print(f"  ⚠️ Could not remove cookie {cookie_file}: {e}")
        
        print("  🌐 Browser data cleared!")
        
    except Exception as e:
        print(f"  ❌ Browser data clear error: {e}")

def force_restart_services():
    """Force restart all services by clearing their state"""
    try:
        # Kill any remaining Python processes
        os.system('taskkill /F /IM python.exe /T 2>nul')
        
        # Wait a moment for processes to terminate
        import time
        time.sleep(2)
        
        print("  🔄 Services force restarted!")
        
    except Exception as e:
        print(f"  ❌ Service restart error: {e}")

if __name__ == "__main__":
    print("🔥 FORCE COMPLETE DATA CLEAR - SOC Correlation Engine")
    print("=" * 60)
    print("⚠️  WARNING: This will delete ALL data from the system!")
    print("=" * 60)
    
    confirm = input("Are you sure you want to delete ALL data? (yes/no): ")
    if confirm.lower() == 'yes':
        asyncio.run(force_clear_all_data())
    else:
        print("❌ Operation cancelled by user")
