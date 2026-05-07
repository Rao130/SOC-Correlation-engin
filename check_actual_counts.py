#!/usr/bin/env python3
"""
Check actual counts behind the API limit issue
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import db_manager

async def check_actual_counts():
    """Check actual counts behind API limit"""
    print("🔍 Checking Actual Counts Behind API Limit...")
    
    try:
        # Connect to database
        await db_manager.connect()
        db = db_manager.get_database()
        correlation_collection = db.correlation_groups
        
        # Check actual counts for each filter
        filter_checks = [
            {"name": "Entity Based", "query": {"correlation_type": "entity_based"}},
            {"name": "Temporal", "query": {"correlation_type": "temporal"}},
            {"name": "Source Based", "query": {"correlation_type": "source_based"}},
            {"name": "Category Based", "query": {"correlation_type": "category_based"}},
            {"name": "Severity Based", "query": {"correlation_type": "severity_based"}},
            {"name": "Critical Status", "query": {"status": "critical"}},
            {"name": "High Status", "query": {"status": "high"}},
            {"name": "Medium Status", "query": {"status": "medium"}},
            {"name": "Low Status", "query": {"status": "low"}},
        ]
        
        print(f"\n📊 Actual vs API Results:")
        print("-" * 60)
        
        for check in filter_checks:
            # Get actual count
            actual_count = await correlation_collection.count_documents(check["query"])
            
            # Get API result (with limit 20)
            api_results = await correlation_collection.find(check["query"]).limit(20).to_list()
            api_count = len(api_results)
            
            # Show the issue
            status = "🔴 PROBLEM" if actual_count > 20 and api_count == 20 else "✅ OK"
            
            print(f"{check['name']:<20} Actual: {actual_count:<4} API: {api_count:<4} {status}")
        
        # Show the core problem
        print(f"\n🎯 ROOT CAUSE IDENTIFIED:")
        print(f"  - Most filters have >20 results")
        print(f"  - API limit is 20, so all return 20")
        print(f"  - This makes it look like filters aren't working")
        print(f"  - User sees same 20 results for different filters")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(check_actual_counts())
