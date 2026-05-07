#!/usr/bin/env python3
"""
Test script to verify real correlation analysis is working with varied results
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.routes.correlation import perform_correlation_analysis
from app.core.database import db_manager

async def test_real_correlation_analysis():
    """Test real correlation analysis with actual database data"""
    print("🔍 Testing Real Correlation Analysis...")
    
    try:
        # Connect to database
        await db_manager.connect()
        db = db_manager.get_database()
        alerts_collection = db.alerts
        
        # Get recent alerts
        from datetime import datetime, timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        recent_alerts = await alerts_collection.find({
            "timestamp": {"$gte": yesterday}
        }).to_list()
        
        print(f"📊 Found {len(recent_alerts)} recent alerts")
        
        if len(recent_alerts) < 2:
            print("❌ Not enough alerts for correlation analysis")
            return False
        
        # Perform correlation analysis
        correlations = await perform_correlation_analysis(recent_alerts)
        
        print(f"🎯 Generated {len(correlations)} correlations")
        
        # Check for variety in results
        if correlations:
            scores = [c['correlation_score'] for c in correlations]
            confidences = [c['confidence'] for c in correlations]
            types = [c['correlation_type'] for c in correlations]
            
            print(f"\n📈 Analysis Results:")
            print(f"  Score Range: {min(scores):.1f} - {max(scores):.1f}")
            print(f"  Confidence Range: {min(confidences)} - {max(confidences)}")
            print(f"  Unique Types: {set(types)}")
            print(f"  Score Variance: {len(set(scores)) > 1}")
            print(f"  Confidence Variance: {len(set(confidences)) > 1}")
            print(f"  Type Variance: {len(set(types)) > 1}")
            
            # Show sample correlations
            print(f"\n🔍 Sample Correlations:")
            for i, corr in enumerate(correlations[:3]):
                print(f"  {i+1}. {corr['name']}")
                print(f"     Type: {corr['correlation_type']}")
                print(f"     Score: {corr['correlation_score']}")
                print(f"     Confidence: {corr['confidence']}")
                print(f"     Risk Level: {corr['risk_assessment']['risk_level']}")
                print()
            
            # Overall variety check
            has_variety = (
                len(set(scores)) > 1 and 
                len(set(confidences)) > 1 and 
                len(set(types)) > 1
            )
            
            print(f"✅ Variety Test Result: {'PASSED' if has_variety else 'FAILED'}")
            
            if has_variety:
                print("🎉 Real correlation analysis is generating varied results!")
            else:
                print("❌ Real correlation analysis is still returning similar results.")
            
            return has_variety
        else:
            print("❌ No correlations generated")
            return False
            
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(test_real_correlation_analysis())
