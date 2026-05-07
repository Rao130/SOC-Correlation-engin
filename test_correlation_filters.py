#!/usr/bin/env python3
"""
Test correlation filtering to identify same results issue
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import db_manager
from datetime import datetime, timedelta

async def test_correlation_filters():
    """Test correlation filtering with different parameters"""
    print("🔍 Testing Correlation Filters...")
    
    try:
        # Connect to database
        await db_manager.connect()
        db = db_manager.get_database()
        correlation_collection = db.correlation_groups
        
        # Get total count
        total_count = await correlation_collection.count_documents({})
        print(f"📊 Total correlations in database: {total_count}")
        
        if total_count == 0:
            print("❌ No correlations found in database")
            return False
        
        # Test different filters
        filters_to_test = [
            {"name": "No Filter", "query": {}},
            {"name": "Entity Based", "query": {"correlation_type": "entity_based"}},
            {"name": "Temporal", "query": {"correlation_type": "temporal"}},
            {"name": "Source Based", "query": {"correlation_type": "source_based"}},
            {"name": "Category Based", "query": {"correlation_type": "category_based"}},
            {"name": "Severity Based", "query": {"correlation_type": "severity_based"}},
            {"name": "Active Status", "query": {"status": "active"}},
            {"name": "Search 'Correlation'", "query": {"$or": [{"name": {"$regex": "Correlation", "$options": "i"}}]}},
        ]
        
        results = {}
        
        for filter_test in filters_to_test:
            query = filter_test["query"]
            filter_name = filter_test["name"]
            
            # Get count and sample data
            count = await correlation_collection.count_documents(query)
            sample = await correlation_collection.find(query).limit(3).to_list()
            
            results[filter_name] = {
                "count": count,
                "sample_names": [item.get('name', 'No name') for item in sample],
                "sample_types": [item.get('correlation_type', 'No type') for item in sample],
                "sample_scores": [item.get('correlation_score', 0) for item in sample]
            }
            
            print(f"\n🔍 Filter: {filter_name}")
            print(f"  Count: {count}")
            if sample:
                print(f"  Sample Names: {results[filter_name]['sample_names']}")
                print(f"  Sample Types: {results[filter_name]['sample_types']}")
                print(f"  Sample Scores: {results[filter_name]['sample_scores']}")
        
        # Check for variety
        print(f"\n📈 Filter Analysis:")
        
        all_counts = [result["count"] for result in results.values()]
        all_names = []
        all_types = set()
        all_scores = []
        
        for result in results.values():
            all_names.extend(result["sample_names"])
            all_types.update(result["sample_types"])
            all_scores.extend(result["sample_scores"])
        
        print(f"  Count Range: {min(all_counts)} - {max(all_counts)}")
        print(f"  Unique Names: {len(set(all_names))}")
        print(f"  Unique Types: {all_types}")
        print(f"  Score Range: {min(all_scores) if all_scores else 0} - {max(all_scores) if all_scores else 0}")
        
        # Check if filters are working properly
        filter_variety = len(set(all_counts)) > 2  # At least 3 different counts
        name_variety = len(set(all_names)) > 5
        type_variety = len(all_types) > 2
        
        print(f"\n✅ Filter Results:")
        print(f"  Count Variety: {'✅' if filter_variety else '❌'}")
        print(f"  Name Variety: {'✅' if name_variety else '❌'}")
        print(f"  Type Variety: {'✅' if type_variety else '❌'}")
        
        overall_working = filter_variety and name_variety and type_variety
        
        print(f"\n🎯 Overall Filter Status: {'✅ WORKING' if overall_working else '❌ NOT WORKING'}")
        
        if not overall_working:
            print("\n🔧 Potential Issues:")
            if not filter_variety:
                print("  - All filters returning same count (possible duplicate data)")
            if not name_variety:
                print("  - Same correlation names across filters")
            if not type_variety:
                print("  - Same correlation types across filters")
        
        # Check for duplicates
        print(f"\n🔍 Checking for Duplicates...")
        all_correlations = await correlation_collection.find({}).to_list()
        
        name_counts = {}
        for corr in all_correlations:
            name = corr.get('name', 'No name')
            name_counts[name] = name_counts.get(name, 0) + 1
        
        duplicates = {name: count for name, count in name_counts.items() if count > 1}
        
        if duplicates:
            print(f"❌ Found {len(duplicates)} duplicate correlation names:")
            for name, count in list(duplicates.items())[:5]:
                print(f"  - {name}: {count} times")
        else:
            print("✅ No duplicate correlation names found")
        
        return overall_working
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(test_correlation_filters())
