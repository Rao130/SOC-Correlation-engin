#!/usr/bin/env python3
"""
Test correlation API endpoints directly to identify the actual issue
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import db_manager
from app.api.routes.correlation import get_correlations
from datetime import datetime, timedelta

async def test_api_direct():
    """Test correlation API endpoints directly like the frontend would call"""
    print("🔍 Direct API Test - Simulating Frontend Calls...")
    
    try:
        # Connect to database
        await db_manager.connect()
        db = db_manager.get_database()
        
        # Simulate different API calls like the frontend would make
        api_calls = [
            {"name": "Default Call", "skip": 0, "limit": 100, "correlation_type": None, "status": None, "search": None},
            {"name": "Entity Filter", "skip": 0, "limit": 100, "correlation_type": "entity_based", "status": None, "search": None},
            {"name": "Temporal Filter", "skip": 0, "limit": 100, "correlation_type": "temporal", "status": None, "search": None},
            {"name": "Source Filter", "skip": 0, "limit": 100, "correlation_type": "source_based", "status": None, "search": None},
            {"name": "Category Filter", "skip": 0, "limit": 100, "correlation_type": "category_based", "status": None, "search": None},
            {"name": "Severity Filter", "skip": 0, "limit": 100, "correlation_type": "severity_based", "status": None, "search": None},
            {"name": "Critical Status", "skip": 0, "limit": 100, "correlation_type": None, "status": "critical", "search": None},
            {"name": "High Status", "skip": 0, "limit": 100, "correlation_type": None, "status": "high", "search": None},
            {"name": "Medium Status", "skip": 0, "limit": 100, "correlation_type": None, "status": "medium", "search": None},
            {"name": "Low Status", "skip": 0, "limit": 100, "correlation_type": None, "status": "low", "search": None},
            {"name": "Active Status", "skip": 0, "limit": 100, "correlation_type": None, "status": "active", "search": None},
            {"name": "Search Filter", "skip": 0, "limit": 100, "correlation_type": None, "status": None, "search": "Correlation"},
        ]
        
        results = []
        
        print(f"\n📊 API Call Results (Like Frontend Would See):")
        print("-" * 80)
        
        for call in api_calls:
            # Simulate the API call exactly as it would happen
            try:
                # Build query like the API does
                query = {}
                if call["correlation_type"]:
                    query["correlation_type"] = call["correlation_type"]
                if call["status"]:
                    query["status"] = call["status"]
                if call["search"]:
                    query["$or"] = [
                        {"name": {"$regex": call["search"], "$options": "i"}},
                        {"description": {"$regex": call["search"], "$options": "i"}}
                    ]
                
                # Execute query like the API
                collection = db.correlation_groups
                cursor = collection.find(query).sort("created_at", -1).skip(call["skip"]).limit(call["limit"])
                correlations = await cursor.to_list()
                
                # Convert ObjectId to string like the API does
                def convert_objectid(obj):
                    if hasattr(obj, '__iter__') and not isinstance(obj, str):
                        if isinstance(obj, dict):
                            return {k: convert_objectid(v) for k, v in obj.items()}
                        elif isinstance(obj, list):
                            return [convert_objectid(item) for item in obj]
                    elif hasattr(obj, '__str__') and 'ObjectId' in str(type(obj)):
                        return str(obj)
                    return obj
                
                correlations = [convert_objectid(correlation) for correlation in correlations]
                
                # Extract key info
                result = {
                    "name": call["name"],
                    "count": len(correlations),
                    "sample_names": [c.get('name', 'No name') for c in correlations[:3]],
                    "sample_types": [c.get('correlation_type', 'No type') for c in correlations[:3]],
                    "sample_status": [c.get('status', 'No status') for c in correlations[:3]],
                    "sample_scores": [c.get('correlation_score', 0) for c in correlations[:3]]
                }
                
                results.append(result)
                
                print(f"{call['name']:<20} Count: {result['count']:<3} Names: {result['sample_names'][0][:50] if result['sample_names'] else 'None'}")
                
            except Exception as e:
                print(f"{call['name']:<20} ERROR: {e}")
                results.append({"name": call["name"], "count": 0, "error": str(e)})
        
        # Analyze the results
        print(f"\n" + "=" * 80)
        print(f"📈 API Results Analysis:")
        
        all_counts = [r["count"] for r in results if "error" not in r]
        all_names = []
        all_types = set()
        all_status = set()
        
        for result in results:
            if "error" not in result:
                all_names.extend(result["sample_names"])
                all_types.update(result["sample_types"])
                all_status.update(result["sample_status"])
        
        print(f"  Count Range: {min(all_counts) if all_counts else 0} - {max(all_counts) if all_counts else 0}")
        print(f"  Unique Names: {len(set(all_names))}")
        print(f"  Unique Types: {all_types}")
        print(f"  Unique Status: {all_status}")
        
        # Check if filters are working
        count_variety = len(set(all_counts)) > 2
        
        print(f"\n🔍 Filter Working Check:")
        print(f"  Count Variety: {'✅' if count_variety else '❌'}")
        
        # Check specific issues
        if len(all_counts) > 0:
            max_count = max(all_counts)
            same_as_max = sum(1 for count in all_counts if count == max_count)
            
            if same_as_max > len(all_counts) * 0.7:
                print(f"  ⚠️  Warning: {same_as_max}/{len(all_counts)} calls returning max count ({max_count})")
                print(f"  ⚠️  This suggests filters are not working properly!")
        
        # Final assessment
        final_status = count_variety and len(all_types) > 2
        
        print(f"\n🎯 Final API Assessment: {'✅ WORKING' if final_status else '❌ NOT WORKING'}")
        
        if not final_status:
            print(f"\n🔧 Issues Found:")
            if not count_variety:
                print(f"  - API calls returning same counts")
            if len(all_types) <= 2:
                print(f"  - Not enough correlation type variety")
            
            print(f"\n💡 This is likely what the user is experiencing!")
        
        return final_status
        
    except Exception as e:
        print(f"❌ Error in API test: {e}")
        return False
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(test_api_direct())
