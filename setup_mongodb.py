#!/usr/bin/env python3
"""
MongoDB Setup Script for SOC Correlation Engine
Helps install and start MongoDB on Windows
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
from pathlib import Path

def check_admin_privileges():
    """Check if running with admin privileges"""
    try:
        return os.getuid() == 0
    except AttributeError:
        # Windows
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def install_mongodb():
    """Install MongoDB Community Edition"""
    print("🔧 Installing MongoDB Community Edition...")
    
    # MongoDB download URL for Windows
    mongodb_url = "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-7.0.5-signed.msi"
    installer_path = "mongodb_installer.msi"
    
    try:
        print(f"📥 Downloading MongoDB from {mongodb_url}")
        urllib.request.urlretrieve(mongodb_url, installer_path)
        
        print("🚀 Running MongoDB installer...")
        # Run installer silently
        result = subprocess.run(
            ["msiexec", "/i", installer_path, "/quiet", "/norestart"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ MongoDB installed successfully!")
            return True
        else:
            print(f"❌ Installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing MongoDB: {e}")
        return False
    finally:
        # Clean up installer
        if os.path.exists(installer_path):
            os.remove(installer_path)

def start_mongodb_service():
    """Start MongoDB service"""
    print("🚀 Starting MongoDB service...")
    
    try:
        # Try to start the service
        result = subprocess.run(
            ["net", "start", "MongoDB"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ MongoDB service started successfully!")
            return True
        else:
            print(f"❌ Failed to start MongoDB service: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting MongoDB service: {e}")
        return False

def setup_mongodb_data_directory():
    """Create MongoDB data directory"""
    data_dir = r"C:\data\db"
    
    try:
        os.makedirs(data_dir, exist_ok=True)
        print(f"✅ Created MongoDB data directory: {data_dir}")
        return True
    except Exception as e:
        print(f"❌ Failed to create data directory: {e}")
        return False

def start_mongodb_manually():
    """Start MongoDB manually using mongod"""
    print("🚀 Starting MongoDB manually...")
    
    # Common MongoDB installation paths
    mongodb_paths = [
        r"C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe",
        r"C:\Program Files\MongoDB\Server\6.0\bin\mongod.exe",
        r"C:\Program Files\MongoDB\Server\5.0\bin\mongod.exe",
        r"C:\mongodb\bin\mongod.exe"
    ]
    
    mongod_path = None
    for path in mongodb_paths:
        if os.path.exists(path):
            mongod_path = path
            break
    
    if not mongod_path:
        print("❌ MongoDB not found in common installation paths")
        print("Please install MongoDB first or provide the path to mongod.exe")
        return False
    
    try:
        # Create data directory
        setup_mongodb_data_directory()
        
        # Start MongoDB in background
        process = subprocess.Popen(
            [mongod_path, "--dbpath", r"C:\data\db"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ MongoDB started manually (PID: {process.pid})")
        print("MongoDB is running in the background")
        return True
        
    except Exception as e:
        print(f"❌ Error starting MongoDB manually: {e}")
        return False

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("🔍 Testing MongoDB connection...")
    
    try:
        # Try to connect using pymongo
        import pymongo
        client = pymongo.MongoClient("mongodb://127.0.0.1:27017", serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("MONGODB SETUP FOR SOC CORRELATION ENGINE")
    print("=" * 60)
    
    # Check if pymongo is available
    try:
        import pymongo
        print("✅ PyMongo driver is available")
    except ImportError:
        print("❌ PyMongo driver not found")
        print("Installing PyMongo...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pymongo"])
    
    # Test current connection
    if test_mongodb_connection():
        print("✅ MongoDB is already running and accessible!")
        return
    
    print("\n🔧 MongoDB is not running. Attempting to start...")
    
    # Try to start MongoDB service
    if start_mongodb_service():
        if test_mongodb_connection():
            print("✅ MongoDB setup completed successfully!")
            return
    
    print("\n🔧 Service start failed. Trying manual start...")
    
    # Try manual start
    if start_mongodb_manually():
        import time
        print("⏳ Waiting for MongoDB to start...")
        time.sleep(5)
        
        if test_mongodb_connection():
            print("✅ MongoDB setup completed successfully!")
            return
    
    print("\n❌ All attempts to start MongoDB failed")
    print("\n🔧 MANUAL SETUP INSTRUCTIONS:")
    print("1. Download MongoDB from: https://www.mongodb.com/try/download/community")
    print("2. Install MongoDB Community Edition")
    print("3. Create data directory: C:\\data\\db")
    print("4. Start MongoDB service: net start MongoDB")
    print("5. Or run manually: mongod --dbpath C:\\data\\db")
    print("6. Alternative - Use Docker: docker run -d -p 27017:27017 mongo")

if __name__ == "__main__":
    main()
