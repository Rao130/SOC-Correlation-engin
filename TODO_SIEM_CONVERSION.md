# SIEM Conversion Plan

## Task List
- [x] 1. Enhance Network Monitor with more real threat detection (already implemented)
- [x] 2. Configure disable mock generation (ENABLE_DATA_GENERATION=false)
- [x] 3. Update entity-network endpoint with real data
- [ ] 4. Remove remaining mock data from analytics API
- [ ] 5. Test all features work without errors

## Implementation Status: MOSTLY COMPLETE

## Changes Made

### ✅ 1. Configuration (ENABLE_DATA_GENERATION=false)
- Set `ENABLE_DATA_GENERATION: bool = False` in app/core/config.py
- Data generator only runs when explicitly enabled

### ✅ 2. Network Monitor (using real psutil data)
- Uses psutil library for real network connections
- Uses netifaces for network interface information
- Detects suspicious ports, connections, port scanning

### ✅ 3. Data Generator Safety
- Added config check before starting generation
- Only activates when `settings.ENABLE_DATA_GENERATION=True`

### ✅ 4. Analytics API Updates
- entity-network now extracts from network_monitor memory_alerts
- Returns empty array when no real data available

## Remaining Work
- pattern-analysis endpoint
- compliance-matrix endpoint
- performance-metrics endpoint
- threat-lifecycle endpoint

## SIEM Mode Summary
- To enable test data: `ENABLE_DATA_GENERATION=true`
- Production SIEM: `ENABLE_DATA_GENERATION=false` (default)
