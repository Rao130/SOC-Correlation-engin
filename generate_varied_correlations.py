#!/usr/bin/env python3
"""
Generate new varied correlation data with different status values
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.routes.correlation import perform_correlation_analysis
from app.core.database import db_manager
from datetime import datetime, timedelta

async def generate_varied_correlations():
    """Generate new correlation data with varied status values"""
    print("🔄 Generating New Varied Correlation Data...")
    
    try:
        # Connect to database
        await db_manager.connect()
        db = db_manager.get_database()
        alerts_collection = db.alerts
        
        # Get recent alerts
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_alerts = await alerts_collection.find({
            "timestamp": {"$gte": yesterday}
        }).to_list()
        
        print(f"📊 Found {len(recent_alerts)} recent alerts")
        
        if len(recent_alerts) < 2:
            print("❌ Not enough alerts for correlation analysis")
            return False
        
        # Generate new correlations with varied status
        correlations = await perform_correlation_analysis(recent_alerts)
        
        print(f"🎯 Generated {len(correlations)} new correlations")
        
        if correlations:
            # Analyze status distribution
            status_counts = {}
            type_counts = {}
            
            for corr in correlations:
                status = corr.get('status', 'unknown')
                corr_type = corr.get('correlation_type', 'unknown')
                
                status_counts[status] = status_counts.get(status, 0) + 1
                type_counts[corr_type] = type_counts.get(corr_type, 0) + 1
            
            print(f"\n📈 Status Distribution:")
            for status, count in status_counts.items():
                print(f"  {status}: {count}")
            
            print(f"\n📊 Type Distribution:")
            for corr_type, count in type_counts.items():
                print(f"  {corr_type}: {count}")
            
            # Test filters with new data
            print(f"\n🧪 Testing Filters with New Data:")
            correlation_collection = db.correlation_groups
            
            filter_tests = [
                {"name": "Critical Status", "query": {"status": "critical"}},
                {"name": "High Status", "query": {"status": "high"}},
                {"name": "Medium Status", "query": {"status": "medium"}},
                {"name": "Low Status", "query": {"status": "low"}},
                {"name": "Entity Based", "query": {"correlation_type": "entity_based"}},
                {"name": "Temporal", "query": {"correlation_type": "temporal"}},
                {"name": "Source Based", "query": {"correlation_type": "source_based"}},
            ]
            
            for test in filter_tests:
                count = await correlation_collection.count_documents(test["query"])
                print(f"  {test['name']}: {count}")
            
            # Check if filters now work properly
            all_counts = []
            for test in filter_tests:
                count = await correlation_collection.count_documents(test["query"])
                all_counts.append(count)
            
            count_variety = len(set(all_counts)) > 3
            
            print(f"\n✅ Filter Variety Check: {'PASSED' if count_variety else 'FAILED'}")
            
            if count_variety:
                print("🎉 Filters are now working with varied results!")
            else:
                print("❌ Filters still have variety issues")
            
            return count_variety
        else:
            print("❌ No correlations generated")
            return False
        
    except Exception as e:
        print(f"❌ Error in generation: {e}")
        return False
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(generate_varied_correlations())
