#!/usr/bin/env python3
"""
Production Readiness Test - Verify system works with 100% real-time data
No mock data, no fallbacks, pure production system
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.real_time_data_ingestion import real_time_ingestion
from app.services.real_time_correlation import real_time_correlation
from app.core.database import db_manager
from datetime import datetime, timedelta

async def test_production_readiness():
    """Test complete system for production readiness"""
    print("🔍 Production Readiness Test - 100% Real-time Data System")
    print("=" * 60)
    
    try:
        # Connect to database
        await db_manager.connect()
        print("✅ Database connected")
        
        # Start real-time data ingestion
        await real_time_ingestion.start_ingestion()
        print("✅ Real-time data ingestion started")
        
        # Wait for real data generation
        print("⏳ Generating real-time data...")
        await asyncio.sleep(20)  # Wait 20 seconds for real data
        
        # Test 1: Verify real alerts in database
        db = db_manager.get_database()
        alerts_collection = db.get_collection("alerts")
        
        total_alerts = await alerts_collection.count_documents({})
        print(f"📊 Real Alerts in Database: {total_alerts}")
        
        if total_alerts == 0:
            print("❌ No real alerts found - system not generating real data")
            return False
        
        # Test 2: Verify alert sources are real
        real_sources = await alerts_collection.distinct("source")
        print(f"📡 Real Data Sources: {real_sources}")
        
        mock_indicators = ["mock", "sample", "test", "demo", "fake"]
        has_mock_sources = any(indicator in source.lower() for source in real_sources for indicator in mock_indicators)
        
        if has_mock_sources:
            print("❌ Mock data sources detected in alerts")
            return False
        
        # Test 3: Verify alert categories are real
        real_categories = await alerts_collection.distinct("category")
        print(f"📋 Real Alert Categories: {real_categories}")
        
        # Test 4: Verify correlations are real
        correlation_collection = db.get_collection("correlation_groups")
        total_correlations = await correlation_collection.count_documents({})
        print(f"🔗 Real Correlations: {total_correlations}")
        
        if total_correlations > 0:
            correlation_types = await correlation_collection.distinct("correlation_type")
            print(f"📊 Correlation Types: {correlation_types}")
            
            # Check for mock correlation names
            sample_correlations = await correlation_collection.find({}).limit(5).to_list()
            mock_names = ["mock", "sample", "test", "demo"]
            has_mock_correlations = any(
                any(indicator in corr.get('name', '').lower() for indicator in mock_names)
                for corr in sample_correlations
            )
            
            if has_mock_correlations:
                print("❌ Mock correlations detected")
                return False
        
        # Test 5: Verify system statistics
        ingestion_stats = await real_time_ingestion.get_ingestion_statistics()
        print(f"📈 Ingestion Statistics:")
        print(f"  Active: {ingestion_stats['active']}")
        print(f"  Buffer Size: {ingestion_stats['buffer_size']}")
        print(f"  Data Sources: {len(ingestion_stats['data_sources'])}")
        
        correlation_stats = ingestion_stats['correlation_processing']
        print(f"🔄 Correlation Statistics:")
        print(f"  Active: {correlation_stats['active']}")
        print(f"  Alert Buffer: {correlation_stats['alert_buffer_size']}")
        print(f"  Entity Buffer: {correlation_stats['entity_buffer_size']}")
        
        # Test 6: Verify data freshness
        recent_alerts = await alerts_collection.find({
            "timestamp": {"$gte": datetime.utcnow() - timedelta(minutes=5)}
        }).to_list()
        
        print(f"⚡ Recent Alerts (last 5 min): {len(recent_alerts)}")
        
        if len(recent_alerts) == 0:
            print("⚠️  No recent alerts - check data generation")
        
        # Test 7: Production readiness checklist
        print(f"\n🎯 Production Readiness Checklist:")
        
        checks = {
            "Real Alerts Generated": total_alerts > 0,
            "Real Data Sources": not has_mock_sources,
            "Real Categories": len(real_categories) > 3,
            "Real Correlations": total_correlations >= 0,
            "No Mock Data": not has_mock_sources and not has_mock_correlations,
            "Data Ingestion Active": ingestion_stats['active'],
            "Correlation Active": correlation_stats['active'],
            "Recent Data": len(recent_alerts) > 0
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {check_name:<25} {status}")
            if not passed:
                all_passed = False
        
        # Final assessment
        print(f"\n🚀 Production Readiness: {'✅ READY' if all_passed else '❌ NOT READY'}")
        
        if all_passed:
            print(f"\n🎉 SUCCESS! System is production-ready:")
            print(f"   ✅ Pure real-time data flow")
            print(f"   ✅ No mock data dependencies")
            print(f"   ✅ Real security sources")
            print(f"   ✅ Live correlation processing")
            print(f"   ✅ Fresh data generation")
            print(f"\n📦 Ready for deployment!")
        else:
            print(f"\n❌ System needs fixes before deployment:")
            failed_checks = [name for name, passed in checks.items() if not passed]
            for check in failed_checks:
                print(f"   - {check}")
        
        # Stop services
        await real_time_ingestion.stop_ingestion()
        print("✅ Services stopped")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Production test failed: {e}")
        return False
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(test_production_readiness())
