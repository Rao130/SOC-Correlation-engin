"""
Clear Memory Data from All Services
Clears in-memory alerts and logs from all services
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def clear_all_memory_data():
    """Clear all in-memory data from services"""
    try:
        print("🧠 Clearing all in-memory data...")
        
        # Clear RealDataGenerator memory
        print("\n📊 Clearing RealDataGenerator...")
        await clear_data_generator_memory()
        
        # Clear NetworkMonitor memory
        print("\n🌐 Clearing NetworkMonitor...")
        await clear_network_monitor_memory()
        
        # Clear LogStreamer memory
        print("\n📝 Clearing LogStreamer...")
        await clear_log_streamer_memory()
        
        # Clear any other service memory
        print("\n🔄 Clearing other services...")
        await clear_other_services_memory()
        
        print("\n✅ All memory data cleared!")
        
    except Exception as e:
        print(f"❌ Error clearing memory data: {e}")
        import traceback
        traceback.print_exc()

async def clear_data_generator_memory():
    """Clear RealDataGenerator memory"""
    try:
        from app.services.real_data_generator import data_generator
        
        # Clear generated alerts
        if hasattr(data_generator, 'generated_alerts'):
            data_generator.generated_alerts.clear()
            print("  ✅ Cleared data_generator.generated_alerts")
        
        # Clear any other memory attributes
        if hasattr(data_generator, 'alert_history'):
            data_generator.alert_history.clear()
            print("  ✅ Cleared data_generator.alert_history")
        
        # Reset any counters
        if hasattr(data_generator, 'alert_counter'):
            data_generator.alert_counter = 0
            print("  ✅ Reset data_generator.alert_counter")
        
        print("  🎉 RealDataGenerator memory cleared!")
        
    except Exception as e:
        print(f"  ❌ Error clearing data_generator: {e}")

async def clear_network_monitor_memory():
    """Clear NetworkMonitor memory"""
    try:
        from app.services.network_monitor import network_monitor
        
        # Clear memory alerts
        if hasattr(network_monitor, 'memory_alerts'):
            network_monitor.memory_alerts.clear()
            print("  ✅ Cleared network_monitor.memory_alerts")
        
        # Clear suspicious IPs
        if hasattr(network_monitor, 'suspicious_ips'):
            network_monitor.suspicious_ips.clear()
            print("  ✅ Cleared network_monitor.suspicious_ips")
        
        # Clear previous connections
        if hasattr(network_monitor, 'previous_connections'):
            network_monitor.previous_connections.clear()
            print("  ✅ Cleared network_monitor.previous_connections")
        
        # Reset any counters
        if hasattr(network_monitor, 'alert_counter'):
            network_monitor.alert_counter = 0
            print("  ✅ Reset network_monitor.alert_counter")
        
        print("  🎉 NetworkMonitor memory cleared!")
        
    except Exception as e:
        print(f"  ❌ Error clearing network_monitor: {e}")

async def clear_log_streamer_memory():
    """Clear LogStreamer memory"""
    try:
        from app.services.log_streamer import log_streamer
        
        # Clear generated logs
        if hasattr(log_streamer, 'generated_logs'):
            log_streamer.generated_logs.clear()
            print("  ✅ Cleared log_streamer.generated_logs")
        
        # Clear any other memory attributes
        if hasattr(log_streamer, 'log_history'):
            log_streamer.log_history.clear()
            print("  ✅ Cleared log_streamer.log_history")
        
        # Reset any counters
        if hasattr(log_streamer, 'log_counter'):
            log_streamer.log_counter = 0
            print("  ✅ Reset log_streamer.log_counter")
        
        print("  🎉 LogStreamer memory cleared!")
        
    except Exception as e:
        print(f"  ❌ Error clearing log_streamer: {e}")

async def clear_other_services_memory():
    """Clear memory from other services"""
    try:
        # Clear correlation engine memory
        try:
            from app.services.correlation_engine import correlation_engine
            if hasattr(correlation_engine, 'correlation_cache'):
                correlation_engine.correlation_cache.clear()
                print("  ✅ Cleared correlation_engine.correlation_cache")
        except:
            pass
        
        # Clear advanced correlation memory
        try:
            from app.services.advanced_correlation import correlation_engine
            if hasattr(correlation_engine, 'correlation_results'):
                correlation_engine.correlation_results.clear()
                print("  ✅ Cleared advanced_correlation.correlation_results")
        except:
            pass
        
        # Clear threat scoring memory
        try:
            from app.services.threat_scoring import threat_scoring_engine
            if hasattr(threat_scoring_engine, 'score_cache'):
                threat_scoring_engine.score_cache.clear()
                print("  ✅ Cleared threat_scoring.score_cache")
        except:
            pass
        
        # Clear anomaly detection memory
        try:
            from app.services.anomaly_detection import anomaly_detection_engine
            if hasattr(anomaly_detection_engine, 'detection_history'):
                anomaly_detection_engine.detection_history.clear()
                print("  ✅ Cleared anomaly_detection.detection_history")
        except:
            pass
        
        # Clear attack chain mapper memory
        try:
            from app.services.attack_chain_mapper import attack_chain_mapper
            if hasattr(attack_chain_mapper, 'active_chains'):
                attack_chain_mapper.active_chains.clear()
                print("  ✅ Cleared attack_chain_mapper.active_chains")
        except:
            pass
        
        # Clear autonomous response memory
        try:
            from app.services.autonomous_response import autonomous_response_engine
            if hasattr(autonomous_response_engine, 'response_history'):
                autonomous_response_engine.response_history.clear()
                print("  ✅ Cleared autonomous_response.response_history")
        except:
            pass
        
        print("  🎉 Other services memory cleared!")
        
    except Exception as e:
        print(f"  ❌ Error clearing other services: {e}")

if __name__ == "__main__":
    print("🧠 Memory Data Clear - SOC Correlation Engine")
    print("=" * 50)
    
    asyncio.run(clear_all_memory_data())
