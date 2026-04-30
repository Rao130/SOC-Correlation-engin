#!/usr/bin/env python3
"""
Live verification that correlation filters are working properly
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import db_manager
from app.api.routes.correlation import get_correlations
from datetime import datetime, timedelta

async def verify_filters_live():
    """Verify correlation filters are working with live API simulation"""
    print("🔍 Live Verification of Correlation Filters...")
    
    try:
        # Connect to database
        await db_manager.connect()
        db = db_manager.get_database()
        
        # Simulate different filter calls like the API would do
        filter_tests = [
            {"name": "No Filter", "correlation_type": None, "status": None, "search": None},
            {"name": "Entity Based Filter", "correlation_type": "entity_based", "status": None, "search": None},
            {"name": "Temporal Filter", "correlation_type": "temporal", "status": None, "search": None},
            {"name": "Source Based Filter", "correlation_type": "source_based", "status": None, "search": None},
            {"name": "Category Based Filter", "correlation_type": "category_based", "status": None, "search": None},
            {"name": "Severity Based Filter", "correlation_type": "severity_based", "status": None, "search": None},
            {"name": "Active Status Filter", "correlation_type": None, "status": "active", "search": None},
            {"name": "Search Filter", "correlation_type": None, "status": None, "search": "Correlation"},
        ]
        
        results = {}
        
        for test in filter_tests:
            print(f"\n🔍 Testing: {test['name']}")
            
            # Build query like the API does
            query = {}
            if test['correlation_type']:
                query["correlation_type"] = test['correlation_type']
            if test['status']:
                query["status"] = test['status']
            if test['search']:
                query["$or"] = [
                    {"name": {"$regex": test['search'], "$options": "i"}},
                    {"description": {"$regex": test['search'], "$options": "i"}}
                ]
            
            # Execute query like the API
            collection = db.correlation_groups
            cursor = collection.find(query).sort("created_at", -1).limit(10)
            correlations = await cursor.to_list()
            
            # Extract sample data
            sample_names = [c.get('name', 'No name') for c in correlations[:3]]
            sample_types = [c.get('correlation_type', 'No type') for c in correlations[:3]]
            sample_scores = [c.get('correlation_score', 0) for c in correlations[:3]]
            
            results[test['name']] = {
                "count": len(correlations),
                "sample_names": sample_names,
                "sample_types": sample_types,
                "sample_scores": sample_scores
            }
            
            print(f"  Count: {len(correlations)}")
            print(f"  Sample Names: {sample_names}")
            print(f"  Sample Types: {sample_types}")
            print(f"  Sample Scores: {sample_scores}")
        
        # Analyze results for variety
        print(f"\n📈 Filter Variety Analysis:")
        
        all_counts = [result["count"] for result in results.values()]
        all_names = []
        all_types = set()
        
        for result in results.values():
            all_names.extend(result["sample_names"])
            all_types.update(result["sample_types"])
        
        count_variety = len(set(all_counts)) > 3  # Different counts for different filters
        name_variety = len(set(all_names)) > 5
        type_variety = len(all_types) > 2
        
        print(f"  Count Range: {min(all_counts)} - {max(all_counts)}")
        print(f"  Unique Names: {len(set(all_names))}")
        print(f"  Unique Types: {all_types}")
        print(f"  Count Variety: {'✅' if count_variety else '❌'}")
        print(f"  Name Variety: {'✅' if name_variety else '❌'}")
        print(f"  Type Variety: {'✅' if type_variety else '❌'}")
        
        # Check if filters are actually different
        filter_results_different = True
        baseline_count = results["No Filter"]["count"]
        
        for test_name, result in results.items():
            if test_name != "No Filter" and result["count"] == baseline_count:
                print(f"⚠️  Warning: {test_name} returned same count as no filter")
                filter_results_different = False
        
        final_status = count_variety and name_variety and type_variety and filter_results_different
        
        print(f"\n🎯 Final Status: {'✅ FILTERS WORKING PROPERLY' if final_status else '❌ FILTERS HAVE ISSUES'}")
        
        if not final_status:
            print("\n🔧 Issues Found:")
            if not count_variety:
                print("  - Filters returning same counts")
            if not name_variety:
                print("  - Same correlation names across filters")
            if not type_variety:
                print("  - Same correlation types across filters")
            if not filter_results_different:
                print("  - Some filters not filtering properly")
        
        return final_status
        
    except Exception as e:
        print(f"❌ Error in verification: {e}")
        return False
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(verify_filters_live())
