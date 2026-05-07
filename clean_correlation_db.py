#!/usr/bin/env python3
"""
Clean duplicate correlations from database
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import db_manager

async def clean_correlation_duplicates():
    """Clean duplicate correlations from database"""
    print("🧹 Cleaning Correlation Database...")
    
    try:
        # Connect to database
        await db_manager.connect()
        db = db_manager.get_database()
        correlation_collection = db.correlation_groups
        
        # Get all correlations
        all_correlations = await correlation_collection.find({}).to_list()
        print(f"📊 Total correlations before cleaning: {len(all_correlations)}")
        
        # Group by correlation type and base name
        correlation_groups = {}
        
        for corr in all_correlations:
            name = corr.get('name', 'No name')
            correlation_type = corr.get('correlation_type', 'unknown')
            
            # Extract base name (remove timestamp)
            if ' - ' in name:
                base_name = name.split(' - ')[0]
            else:
                base_name = name
            
            key = f"{correlation_type}:{base_name}"
            
            if key not in correlation_groups:
                correlation_groups[key] = []
            correlation_groups[key].append(corr)
        
        # Find duplicates
        duplicates_to_remove = []
        unique_to_keep = []
        
        for key, correlations in correlation_groups.items():
            if len(correlations) > 1:
                print(f"🔍 Found duplicates for: {key} ({len(correlations)} items)")
                
                # Keep the latest one, remove others
                correlations.sort(key=lambda x: x.get('created_at', ''), reverse=True)
                unique_to_keep.append(correlations[0])
                duplicates_to_remove.extend(correlations[1:])
                
                print(f"  Keeping: {correlations[0].get('name', 'No name')} ({correlations[0].get('created_at', 'No date')})")
                for dup in correlations[1:]:
                    print(f"  Removing: {dup.get('name', 'No name')} ({dup.get('created_at', 'No date')})")
            else:
                unique_to_keep.extend(correlations)
        
        # Remove duplicates
        if duplicates_to_remove:
            print(f"\n🗑️ Removing {len(duplicates_to_remove)} duplicate correlations...")
            
            for dup in duplicates_to_remove:
                await correlation_collection.delete_one({'_id': dup['_id']})
        
        # Get final count
        final_count = await correlation_collection.count_documents({})
        print(f"📊 Total correlations after cleaning: {final_count}")
        print(f"✅ Removed {len(duplicates_to_remove)} duplicates")
        
        # Show sample of remaining correlations
        sample_correlations = await correlation_collection.find({}).limit(5).to_list()
        print(f"\n📋 Sample remaining correlations:")
        for i, corr in enumerate(sample_correlations):
            print(f"  {i+1}. {corr.get('name', 'No name')} ({corr.get('correlation_type', 'No type')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in cleaning: {e}")
        return False
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(clean_correlation_duplicates())
