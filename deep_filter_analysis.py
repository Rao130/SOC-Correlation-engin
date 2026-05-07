#!/usr/bin/env python3
"""
Deep analysis of correlation filter issues
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import db_manager

async def deep_filter_analysis():
    """Deep analysis of why filters are not working properly"""
    print("🔍 Deep Analysis of Correlation Filter Issues...")
    
    try:
        # Connect to database
        await db_manager.connect()
        db = db_manager.get_database()
        correlation_collection = db.correlation_groups
        
        # Get all correlations and analyze
        all_correlations = await correlation_collection.find({}).to_list()
        print(f"📊 Total correlations in database: {len(all_correlations)}")
        
        # Analyze correlation types distribution
        type_counts = {}
        for corr in all_correlations:
            corr_type = corr.get('correlation_type', 'unknown')
            type_counts[corr_type] = type_counts.get(corr_type, 0) + 1
        
        print(f"\n📈 Correlation Type Distribution:")
        for corr_type, count in type_counts.items():
            print(f"  {corr_type}: {count}")
        
        # Check status distribution
        status_counts = {}
        for corr in all_correlations:
            status = corr.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n📊 Status Distribution:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
        # Sample correlations by type
        print(f"\n🔍 Sample Correlations by Type:")
        for corr_type in type_counts.keys():
            sample = await correlation_collection.find({"correlation_type": corr_type}).limit(3).to_list()
            print(f"\n  {corr_type} ({len(sample)} shown):")
            for i, corr in enumerate(sample):
                print(f"    {i+1}. {corr.get('name', 'No name')} - Score: {corr.get('correlation_score', 0)}")
        
        # Test actual filter queries
        print(f"\n🧪 Testing Actual Filter Queries:")
        
        filters = [
            {"correlation_type": "entity_based"},
            {"correlation_type": "temporal"},
            {"correlation_type": "source_based"},
            {"correlation_type": "category_based"},
            {"correlation_type": "severity_based"},
            {"status": "active"},
            {"$or": [{"name": {"$regex": "Correlation", "$options": "i"}}]}
        ]
        
        for i, filter_query in enumerate(filters):
            count = await correlation_collection.count_documents(filter_query)
            print(f"  Filter {i+1}: {filter_query} -> Count: {count}")
        
        # Check if there are issues with correlation types
        print(f"\n🔍 Checking for Type Issues:")
        
        # Check if correlations have proper types
        missing_types = [c for c in all_correlations if not c.get('correlation_type')]
        print(f"  Correlations missing type: {len(missing_types)}")
        
        # Check if correlations have proper status
        missing_status = [c for c in all_correlations if not c.get('status')]
        print(f"  Correlations missing status: {len(missing_status)}")
        
        # Check if all correlations are active
        active_count = len([c for c in all_correlations if c.get('status') == 'active'])
        print(f"  Active correlations: {active_count}/{len(all_correlations)}")
        
        # Identify the problem
        print(f"\n🎯 Problem Analysis:")
        
        if len(type_counts) <= 2:
            print("  ❌ Not enough correlation type variety")
        
        if active_count == len(all_correlations):
            print("  ❌ All correlations have same status (active)")
        
        if len(set(c.get('correlation_score', 0) for c in all_correlations[:10])) <= 3:
            print("  ❌ Similar scores in correlations")
        
        # Check if we need to generate new varied correlations
        needs_new_data = (
            len(type_counts) <= 3 or 
            active_count == len(all_correlations) or
            len(all_correlations) < 50
        )
        
        print(f"\n💡 Solution Needed: {'YES' if needs_new_data else 'NO'}")
        
        if needs_new_data:
            print("  Need to generate new varied correlation data")
        
        return needs_new_data
        
    except Exception as e:
        print(f"❌ Error in analysis: {e}")
        return False
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(deep_filter_analysis())
