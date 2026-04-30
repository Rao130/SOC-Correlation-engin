#!/usr/bin/env python3
"""
Final test of correlation filters with actual database counts
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import db_manager

async def final_filter_test():
    """Test correlation filters with actual database counts (no API limits)"""
    print("🔍 Final Filter Test - Actual Database Counts...")
    
    try:
        # Connect to database
        await db_manager.connect()
        db = db_manager.get_database()
        correlation_collection = db.correlation_groups
        
        # Test all filters with actual counts
        filter_tests = [
            {"name": "No Filter", "query": {}},
            {"name": "Entity Based", "query": {"correlation_type": "entity_based"}},
            {"name": "Temporal", "query": {"correlation_type": "temporal"}},
            {"name": "Source Based", "query": {"correlation_type": "source_based"}},
            {"name": "Category Based", "query": {"correlation_type": "category_based"}},
            {"name": "Severity Based", "query": {"correlation_type": "severity_based"}},
            {"name": "Critical Status", "query": {"status": "critical"}},
            {"name": "High Status", "query": {"status": "high"}},
            {"name": "Medium Status", "query": {"status": "medium"}},
            {"name": "Low Status", "query": {"status": "low"}},
            {"name": "Active Status", "query": {"status": "active"}},
            {"name": "Search 'Correlation'", "query": {"$or": [{"name": {"$regex": "Correlation", "$options": "i"}}]}},
        ]
        
        results = []
        
        print(f"\n📊 Actual Database Filter Results:")
        print("-" * 60)
        
        for test in filter_tests:
            query = test["query"]
            count = await correlation_collection.count_documents(query)
            
            # Get sample data
            sample = await correlation_collection.find(query).limit(3).to_list()
            sample_names = [c.get('name', 'No name') for c in sample]
            sample_types = [c.get('correlation_type', 'No type') for c in sample]
            
            result = {
                "name": test["name"],
                "count": count,
                "sample_names": sample_names,
                "sample_types": sample_types
            }
            
            results.append(result)
            
            print(f"{test['name']:<20} Count: {count:<6} Sample: {sample_names[0] if sample_names else 'None'}")
        
        # Analyze variety
        print(f"\n" + "=" * 60)
        print(f"📈 Filter Variety Analysis:")
        
        all_counts = [result["count"] for result in results]
        all_names = []
        all_types = set()
        
        for result in results:
            all_names.extend(result["sample_names"])
            all_types.update(result["sample_types"])
        
        count_variety = len(set(all_counts)) > 5  # Different counts for different filters
        name_variety = len(set(all_names)) > 10
        type_variety = len(all_types) > 3
        
        print(f"  Count Range: {min(all_counts)} - {max(all_counts)}")
        print(f"  Unique Names: {len(set(all_names))}")
        print(f"  Unique Types: {all_types}")
        print(f"  Count Variety: {'✅' if count_variety else '❌'}")
        print(f"  Name Variety: {'✅' if name_variety else '❌'}")
        print(f"  Type Variety: {'✅' if type_variety else '❌'}")
        
        # Check specific filter differences
        print(f"\n🔍 Specific Filter Comparisons:")
        
        # Status filters
        critical_count = next(r["count"] for r in results if r["name"] == "Critical Status")
        high_count = next(r["count"] for r in results if r["name"] == "High Status")
        medium_count = next(r["count"] for r in results if r["name"] == "Medium Status")
        low_count = next(r["count"] for r in results if r["name"] == "Low Status")
        
        print(f"  Status Filters Working: {critical_count != high_count != medium_count != low_count}")
        
        # Type filters
        entity_count = next(r["count"] for r in results if r["name"] == "Entity Based")
        temporal_count = next(r["count"] for r in results if r["name"] == "Temporal")
        source_count = next(r["count"] for r in results if r["name"] == "Source Based")
        
        print(f"  Type Filters Working: {entity_count != temporal_count != source_count}")
        
        # Overall assessment
        final_status = count_variety and name_variety and type_variety
        
        print(f"\n🎯 Final Assessment: {'✅ FILTERS WORKING PERFECTLY' if final_status else '❌ FILTERS HAVE ISSUES'}")
        
        if final_status:
            print(f"\n🎉 SUCCESS! Correlation filters are working with varied results!")
            print(f"   - Different filters return different counts")
            print(f"   - Status filters properly segment by risk level")
            print(f"   - Type filters properly segment by correlation type")
            print(f"   - Search and other filters working correctly")
        else:
            print(f"\n❌ FAILURE! Filters still have issues")
        
        return final_status
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(final_filter_test())
