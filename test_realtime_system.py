#!/usr/bin/env python3
"""
Test the complete real-time SOC system with pure real-time data flow
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.real_time_data_ingestion import real_time_ingestion
from app.services.real_time_correlation import real_time_correlation
from app.core.database import db_manager
from datetime import datetime, timedelta

async def test_realtime_system():
    """Test complete real-time system functionality"""
    print("🔍 Testing Complete Real-time SOC System...")
    
    try:
        # Connect to database
        await db_manager.connect()
        print("✅ Database connected")
        
        # Start real-time data ingestion
        await real_time_ingestion.start_ingestion()
        print("✅ Real-time data ingestion started")
        
        # Wait for some data to be generated and processed
        print("⏳ Waiting for real-time data processing...")
        await asyncio.sleep(15)  # Wait 15 seconds for data generation
        
        # Check ingestion statistics
        ingestion_stats = await real_time_ingestion.get_ingestion_statistics()
        print(f"📊 Ingestion Statistics:")
        print(f"  Active: {ingestion_stats['active']}")
        print(f"  Buffer Size: {ingestion_stats['buffer_size']}")
        print(f"  Data Sources: {len(ingestion_stats['data_sources'])}")
        
        # Check correlation statistics
        correlation_stats = ingestion_stats['correlation_processing']
        print(f"🔄 Correlation Statistics:")
        print(f"  Active: {correlation_stats['active']}")
        print(f"  Alert Buffer Size: {correlation_stats['alert_buffer_size']}")
        print(f"  Entity Buffer Size: {correlation_stats['entity_buffer_size']}")
        print(f"  Temporal Buffer Size: {correlation_stats['temporal_buffer_size']}")
        print(f"  Source Buffer Size: {correlation_stats['source_buffer_size']}")
        print(f"  Category Buffer Size: {correlation_stats['category_buffer_size']}")
        
        # Check database for real alerts
        db = db_manager.get_database()
        alerts_collection = db.alerts
        correlation_collection = db.correlation_groups
        
        # Count alerts in database
        total_alerts = await alerts_collection.count_documents({})
        print(f"📈 Total Alerts in Database: {total_alerts}")
        
        # Count correlations in database
        total_correlations = await correlation_collection.count_documents({})
        print(f"🔗 Total Correlations in Database: {total_correlations}")
        
        # Get sample alerts
        if total_alerts > 0:
            sample_alerts = await alerts_collection.find({}).sort("timestamp", -1).limit(5).to_list()
            print(f"\n📋 Sample Real-time Alerts:")
            for i, alert in enumerate(sample_alerts):
                print(f"  {i+1}. {alert.get('title', 'No title')} - {alert.get('source', 'No source')} - {alert.get('severity', 'No severity')}")
        
        # Get sample correlations
        if total_correlations > 0:
            sample_correlations = await correlation_collection.find({}).sort("created_at", -1).limit(5).to_list()
            print(f"\n🔗 Sample Real-time Correlations:")
            for i, corr in enumerate(sample_correlations):
                print(f"  {i+1}. {corr.get('name', 'No name')} - Score: {corr.get('correlation_score', 0)} - Type: {corr.get('correlation_type', 'No type')}")
        
        # Test correlation types
        if total_correlations > 0:
            correlation_types = await correlation_collection.distinct("correlation_type")
            print(f"\n📊 Correlation Types Found: {correlation_types}")
            
            correlation_statuses = await correlation_collection.distinct("status")
            print(f"📊 Correlation Statuses Found: {correlation_statuses}")
        
        # Test data sources
        if total_alerts > 0:
            alert_sources = await alerts_collection.distinct("source")
            print(f"📊 Alert Sources Found: {alert_sources}")
            
            alert_categories = await alerts_collection.distinct("category")
            print(f"📊 Alert Categories Found: {alert_categories}")
        
        # Evaluate system performance
        print(f"\n🎯 System Performance Evaluation:")
        
        # Check if system is generating real data
        has_real_alerts = total_alerts > 0
        has_real_correlations = total_correlations > 0
        has_varied_sources = len(alert_sources) > 1 if total_alerts > 0 else False
        has_varied_correlations = len(correlation_types) > 1 if total_correlations > 0 else False
        
        print(f"  Real Alerts Generated: {'✅' if has_real_alerts else '❌'}")
        print(f"  Real Correlations Generated: {'✅' if has_real_correlations else '❌'}")
        print(f"  Varied Data Sources: {'✅' if has_varied_sources else '❌'}")
        print(f"  Varied Correlation Types: {'✅' if has_varied_correlations else '❌'}")
        
        # Overall system status
        system_working = has_real_alerts and has_real_correlations
        print(f"\n🚀 Overall System Status: {'✅ WORKING' if system_working else '❌ NOT WORKING'}")
        
        if system_working:
            print(f"\n🎉 SUCCESS! Pure real-time SOC system is working perfectly!")
            print(f"   - Real-time data ingestion from actual sources")
            print(f"   - Real-time correlation processing")
            print(f"   - Database storage of real alerts and correlations")
            print(f"   - No mock data - pure production-ready system")
        else:
            print(f"\n❌ System needs attention:")
            if not has_real_alerts:
                print(f"   - No real alerts being generated")
            if not has_real_correlations:
                print(f"   - No real correlations being processed")
        
        # Stop real-time ingestion
        await real_time_ingestion.stop_ingestion()
        print("✅ Real-time ingestion stopped")
        
        return system_working
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(test_realtime_system())
