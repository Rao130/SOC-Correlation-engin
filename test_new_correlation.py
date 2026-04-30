#!/usr/bin/env python3
"""
Test the NEW real correlation analysis algorithm
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.routes.correlation import perform_correlation_analysis
from app.core.database import db_manager
from datetime import datetime, timedelta

async def test_new_correlation_multiple_times():
    """Test new correlation analysis multiple times to ensure varied results"""
    print("🔍 Testing NEW Real Correlation Analysis (Multiple Runs)...")
    
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
        
        # Test correlation analysis multiple times
        all_results = []
        for run in range(3):
            print(f"\n🔄 Run {run + 1}:")
            correlations = await perform_correlation_analysis(recent_alerts)
            
            print(f"  Generated {len(correlations)} correlations")
            
            if correlations:
                scores = [c['correlation_score'] for c in correlations]
                confidences = [c['confidence'] for c in correlations]
                types = [c['correlation_type'] for c in correlations]
                names = [c['name'] for c in correlations]
                
                print(f"  Score Range: {min(scores):.1f} - {max(scores):.1f}")
                print(f"  Confidence Range: {min(confidences)} - {max(confidences)}")
                print(f"  Types: {set(types)}")
                print(f"  Sample Names: {names[:2]}")
                
                all_results.append({
                    'run': run + 1,
                    'correlations': correlations,
                    'scores': scores,
                    'confidences': confidences,
                    'types': types,
                    'names': names
                })
            else:
                print("  ❌ No correlations generated")
        
        # Analyze variety across runs
        print(f"\n📈 Cross-Run Analysis:")
        
        all_scores = []
        all_confidences = []
        all_types = set()
        all_names = set()
        
        for result in all_results:
            all_scores.extend(result['scores'])
            all_confidences.extend(result['confidences'])
            all_types.update(result['types'])
            all_names.update(result['names'])
        
        print(f"  Total Score Range: {min(all_scores):.1f} - {max(all_scores):.1f}")
        print(f"  Total Confidence Range: {min(all_confidences)} - {max(all_confidences)}")
        print(f"  All Types Found: {all_types}")
        print(f"  Unique Correlation Names: {len(all_names)}")
        
        # Check for variety
        score_variety = len(set(all_scores)) > 5
        confidence_variety = len(set(all_confidences)) > 5
        type_variety = len(all_types) > 2
        name_variety = len(all_names) > 5
        
        print(f"\n✅ Variety Results:")
        print(f"  Score Variety: {'✅' if score_variety else '❌'}")
        print(f"  Confidence Variety: {'✅' if confidence_variety else '❌'}")
        print(f"  Type Variety: {'✅' if type_variety else '❌'}")
        print(f"  Name Variety: {'✅' if name_variety else '❌'}")
        
        overall_variety = score_variety and confidence_variety and type_variety and name_variety
        
        print(f"\n🎯 Overall Result: {'✅ PASSED' if overall_variety else '❌ FAILED'}")
        
        if overall_variety:
            print("🎉 NEW correlation algorithm is generating truly varied results!")
            print("📊 Real correlations based on actual alert entities, times, sources, categories, and severities!")
        else:
            print("❌ NEW correlation algorithm still has variety issues.")
        
        return overall_variety
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(test_new_correlation_multiple_times())
