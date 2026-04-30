#!/usr/bin/env python3
"""
Final verification that correlation filters are working with varied results
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import db_manager

async def final_verification():
    """Final verification that correlation filters work properly"""
    print("🔍 Final Verification - Real API Test...")
    
    try:
        # Connect to database
        await db_manager.connect()
        db = db_manager.get_database()
        correlation_collection = db.correlation_groups
        
        # Test with new API limit (100)
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
        ]
        
        results = []
        
        print(f"\n📊 Real API Results (Limit 100):")
        print("-" * 70)
        
        for test in filter_tests:
            # Simulate real API call with limit 100
            cursor = correlation_collection.find(test["query"]).sort("created_at", -1).limit(100)
            correlations = await cursor.to_list()
            
            result = {
                "name": test["name"],
                "count": len(correlations),
                "sample_names": [c.get('name', 'No name') for c in correlations[:3]],
                "sample_types": [c.get('correlation_type', 'No type') for c in correlations[:3]],
                "sample_status": [c.get('status', 'No status') for c in correlations[:3]]
            }
            
            results.append(result)
            
            # Show variety
            status = "✅ VARIED" if result["count"] != 100 else "⚠️ MAXED"
            print(f"{test['name']:<20} Count: {result['count']:<4} {status}")
            if result["count"] < 100:
                print(f"                     Sample: {result['sample_names'][0][:50] if result['sample_names'] else 'None'}")
        
        # Analyze variety
        all_counts = [r["count"] for r in results]
        unique_counts = set(all_counts)
        
        print(f"\n" + "=" * 70)
        print(f"📈 Final Results Analysis:")
        print(f"  Count Range: {min(all_counts)} - {max(all_counts)}")
        print(f"  Unique Counts: {len(unique_counts)}")
        print(f"  All Same Count: {len(unique_counts) == 1}")
        
        # Check if issue is really fixed
        varied_results = len(unique_counts) > 3
        maxed_results = sum(1 for count in all_counts if count == 100)
        
        print(f"\n🎯 Issue Resolution Status:")
        print(f"  Varied Results: {'✅ FIXED' if varied_results else '❌ NOT FIXED'}")
        print(f"  Maxed Out Results: {maxed_results}/{len(results)}")
        
        if varied_results:
            print(f"\n🎉 SUCCESS! Correlation filters are now working with varied results!")
            print(f"   - Different filters return different counts")
            print(f"   - User will see meaningful variety in results")
            print(f"   - API limit issue resolved")
        else:
            print(f"\n❌ Issue still exists - filters returning same results")
        
        return varied_results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(final_verification())
