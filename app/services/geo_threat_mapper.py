"""
Geographic Threat Mapping Service
Maps security threats to geographic locations for visualization
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.core.logging import logger
from app.services.real_data_generator import data_generator

class GeoThreatMapper:
    """Maps security threats to geographic locations"""
    
    def __init__(self):
        self.threat_locations = self._initialize_threat_locations()
        self.active_threats = []
        self.threat_history = []
        self.active = False
        
    def _initialize_threat_locations(self) -> Dict[str, Dict[str, Any]]:
        """Initialize realistic threat locations with coordinates"""
        return {
            # Major threat actor locations
            "russia": {
                "country": "Russia",
                "latitude": 55.7558,
                "longitude": 37.6173,
                "cities": {
                    "moscow": {"lat": 55.7558, "lon": 37.6173},
                    "st_petersburg": {"lat": 59.9343, "lon": 30.3351},
                    "novosibirsk": {"lat": 55.0084, "lon": 82.9357}
                }
            },
            "china": {
                "country": "China",
                "latitude": 39.9042,
                "longitude": 116.4074,
                "cities": {
                    "beijing": {"lat": 39.9042, "lon": 116.4074},
                    "shanghai": {"lat": 31.2304, "lon": 121.4737},
                    "shenzhen": {"lat": 22.5431, "lon": 114.0579}
                }
            },
            "north_korea": {
                "country": "North Korea",
                "latitude": 39.0392,
                "longitude": 125.7625,
                "cities": {
                    "pyongyang": {"lat": 39.0392, "lon": 125.7625}
                }
            },
            "iran": {
                "country": "Iran",
                "latitude": 35.6961,
                "longitude": 51.4231,
                "cities": {
                    "tehran": {"lat": 35.6961, "lon": 51.4231},
                    "mashhad": {"lat": 36.2605, "lon": 59.6168}
                }
            },
            "usa": {
                "country": "United States",
                "latitude": 39.8283,
                "longitude": -98.5795,
                "cities": {
                    "washington_dc": {"lat": 38.9072, "lon": -77.0369},
                    "san_francisco": {"lat": 37.7749, "lon": -122.4194},
                    "new_york": {"lat": 40.7128, "lon": -74.0060},
                    "los_angeles": {"lat": 34.0522, "lon": -118.2437},
                    "seattle": {"lat": 47.6062, "lon": -122.3321}
                }
            },
            "germany": {
                "country": "Germany",
                "latitude": 51.1657,
                "longitude": 10.4515,
                "cities": {
                    "berlin": {"lat": 52.5200, "lon": 13.4050},
                    "frankfurt": {"lat": 50.1109, "lon": 8.6821},
                    "munich": {"lat": 48.1351, "lon": 11.5820}
                }
            },
            "uk": {
                "country": "United Kingdom",
                "latitude": 55.3781,
                "longitude": -3.4360,
                "cities": {
                    "london": {"lat": 51.5074, "lon": -0.1278},
                    "manchester": {"lat": 53.4808, "lon": -2.2426}
                }
            },
            "brazil": {
                "country": "Brazil",
                "latitude": -14.2350,
                "longitude": -51.9253,
                "cities": {
                    "sao_paulo": {"lat": -23.5505, "lon": -46.6333},
                    "rio_de_janeiro": {"lat": -22.9068, "lon": -43.1729}
                }
            },
            "india": {
                "country": "India",
                "latitude": 20.5937,
                "longitude": 78.9629,
                "cities": {
                    "new_delhi": {"lat": 28.6139, "lon": 77.2090},
                    "mumbai": {"lat": 19.0760, "lon": 72.8777},
                    "bangalore": {"lat": 12.9716, "lon": 77.5946}
                }
            },
            "japan": {
                "country": "Japan",
                "latitude": 36.2048,
                "longitude": 138.2529,
                "cities": {
                    "tokyo": {"lat": 35.6762, "lon": 139.6503},
                    "osaka": {"lat": 34.6937, "lon": 135.5023}
                }
            }
        }
    
    def _get_random_location(self) -> Dict[str, Any]:
        """Get random threat location"""
        country_key = random.choice(list(self.threat_locations.keys()))
        country_data = self.threat_locations[country_key]
        
        # Pick random city in that country
        cities = country_data["cities"]
        city_key = random.choice(list(cities.keys()))
        city_data = cities[city_key]
        
        # Add some random offset to make it more realistic
        lat_offset = random.uniform(-0.5, 0.5)
        lon_offset = random.uniform(-0.5, 0.5)
        
        return {
            "country": country_data["country"],
            "city": city_key.replace("_", " ").title(),
            "latitude": city_data["lat"] + lat_offset,
            "longitude": city_data["lon"] + lon_offset,
            "country_code": country_key.upper()[:2]
        }
    
    def _generate_threat_data(self) -> Dict[str, Any]:
        """Generate realistic threat data for geographic mapping"""
        location = self._get_random_location()
        
        threat_types = [
            "malware", "phishing", "ddos", "data_breach", "ransomware",
            "apt_attack", "sql_injection", "xss", "command_injection", "zero_day"
        ]
        
        threat_actors = {
            "russia": ["APT28", "Fancy Bear", "Cozy Bear", "Energetic Bear"],
            "china": ["APT10", "APT41", "Lotus Panda", "Temp. Perseus"],
            "north_korea": ["Lazarus Group", "Andariel", "Kimsuky"],
            "iran": ["APT33", "APT35", "MuddyWater", "Charming Kitten"],
            "usa": ["Lone Wolf", "Hacktivist", "Insider Threat"],
            "germany": ["Gamaredon Group", "TA505"],
            "uk": ["Lizard Squad", "Anonymous"],
            "brazil": ["Lazarus Group Brazil", "Brazilian Gangs"],
            "india": ["Indian APT Groups", "Local Cybercrime"],
            "japan": ["Japanese APT", "Local Hackers"]
        }
        
        country_key = None
        for key, data in self.threat_locations.items():
            if data["country"] == location["country"]:
                country_key = key
                break
        
        threat_actor = random.choice(threat_actors.get(country_key, ["Unknown"]))
        threat_type = random.choice(threat_types)
        severity = random.choices(
            ["critical", "high", "medium", "low"],
            weights=[15, 25, 40, 20]
        )[0]
        
        # Generate target information
        targets = [
            "Financial Institutions", "Healthcare Systems", "Government Agencies",
            "Critical Infrastructure", "Educational Institutions", "E-commerce Platforms",
            "Social Media", "Cloud Services", "Telecommunications", "Energy Sector"
        ]
        
        target = random.choice(targets)
        
        # Generate confidence and impact scores
        confidence = random.randint(60, 95)
        impact_score = random.randint(1, 10)
        
        # Create threat data
        threat_data = {
            "id": f"threat_{int(datetime.utcnow().timestamp() * 1000)}_{random.randint(1000, 9999)}",
            "location": location,
            "threat_actor": threat_actor,
            "threat_type": threat_type,
            "severity": severity,
            "target": target,
            "confidence": confidence,
            "impact_score": impact_score,
            "description": f"{threat_type} attack detected from {location['city']}, {location['country']} targeting {target}",
            "first_seen": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat(),
            "status": "active",
            "indicators": self._generate_indicators(threat_type),
            "mitigation_status": random.choice(["none", "partial", "complete"]),
            "affected_assets": random.randint(1, 50)
        }
        
        return threat_data
    
    def _generate_indicators(self, threat_type: str) -> List[Dict[str, Any]]:
        """Generate threat indicators based on threat type"""
        indicators = []
        
        if threat_type in ["malware", "ransomware"]:
            indicators.append({
                "type": "file_hash",
                "value": f"{random.choice(['md5', 'sha256'])}:{''.join(random.choices('0123456789abcdef', k=32))}",
                "confidence": random.randint(70, 90)
            })
        
        if threat_type in ["phishing", "apt_attack"]:
            indicators.append({
                "type": "domain",
                "value": f"malicious-{random.randint(1000, 9999)}.com",
                "confidence": random.randint(60, 85)
            })
        
        indicators.append({
            "type": "ip_address",
            "value": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "confidence": random.randint(50, 80)
        })
        
        return indicators
    
    async def generate_threat_burst(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate a burst of geographic threats"""
        threats = []
        for _ in range(count):
            threat_data = self._generate_threat_data()
            threats.append(threat_data)
            self.active_threats.append(threat_data)
            self.threat_history.append(threat_data)
        
        # Keep only last 200 threats in memory
        if len(self.active_threats) > 200:
            self.active_threats = self.active_threats[-200:]
        
        if len(self.threat_history) > 1000:
            self.threat_history = self.threat_history[-1000:]
        
        logger.info(f"Generated {count} geographic threats")
        return threats
    
    def get_active_threats(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get currently active threats"""
        return sorted(self.active_threats, key=lambda x: x.get('first_seen', ''), reverse=True)[:limit]
    
    def get_threat_heatmap_data(self, hours: int = 24) -> Dict[str, Any]:
        """Get threat data formatted for heatmap visualization"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_threats = [
            threat for threat in self.active_threats
            if datetime.fromisoformat(threat.get('first_seen', '').replace('Z', '+00:00')) > cutoff_time
        ]
        
        # Aggregate by location
        location_aggregates = {}
        for threat in recent_threats:
            loc = threat.get('location', {})
            key = f"{loc.get('latitude', 0):.4f},{loc.get('longitude', 0):.4f}"
            
            if key not in location_aggregates:
                location_aggregates[key] = {
                    "latitude": loc.get('latitude', 0),
                    "longitude": loc.get('longitude', 0),
                    "country": loc.get('country', 'Unknown'),
                    "city": loc.get('city', 'Unknown'),
                    "threat_count": 0,
                    "severity_counts": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                    "threat_types": set(),
                    "threat_actors": set()
                }
            
            agg = location_aggregates[key]
            agg["threat_count"] += 1
            agg["severity_counts"][threat.get('severity', 'low')] += 1
            agg["threat_types"].add(threat.get('threat_type', 'unknown'))
            agg["threat_actors"].add(threat.get('threat_actor', 'unknown'))
        
        # Convert sets to lists for JSON serialization
        for agg in location_aggregates.values():
            agg["threat_types"] = list(agg["threat_types"])
            agg["threat_actors"] = list(agg["threat_actors"])
            agg["intensity"] = min(agg["threat_count"] / 10, 1.0)  # Normalize intensity
        
        return {
            "locations": list(location_aggregates.values()),
            "total_threats": len(recent_threats),
            "time_range_hours": hours,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def get_threat_statistics(self) -> Dict[str, Any]:
        """Get comprehensive threat statistics"""
        if not self.active_threats:
            return {"total": 0, "by_country": {}, "by_type": {}, "by_severity": {}}
        
        # Statistics by country
        country_counts = {}
        # Statistics by threat type
        type_counts = {}
        # Statistics by severity
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for threat in self.active_threats:
            # Country stats
            country = threat.get('location', {}).get('country', 'Unknown')
            country_counts[country] = country_counts.get(country, 0) + 1
            
            # Type stats
            threat_type = threat.get('threat_type', 'unknown')
            type_counts[threat_type] = type_counts.get(threat_type, 0) + 1
            
            # Severity stats
            severity = threat.get('severity', 'low')
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        return {
            "total": len(self.active_threats),
            "by_country": dict(sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "by_type": dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "by_severity": severity_counts,
            "last_hour": len([t for t in self.active_threats 
                             if datetime.fromisoformat(t.get('first_seen', '').replace('Z', '+00:00')) > 
                             datetime.utcnow() - timedelta(hours=1)])
        }
    
    def get_top_threat_actors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top threat actors by activity"""
        actor_counts = {}
        
        for threat in self.active_threats:
            actor = threat.get('threat_actor', 'Unknown')
            if actor not in actor_counts:
                actor_counts[actor] = {
                    "name": actor,
                    "threat_count": 0,
                    "countries": set(),
                    "threat_types": set(),
                    "max_severity": "low"
                }
            
            actor_counts[actor]["threat_count"] += 1
            actor_counts[actor]["countries"].add(threat.get('location', {}).get('country', 'Unknown'))
            actor_counts[actor]["threat_types"].add(threat.get('threat_type', 'unknown'))
            
            # Update max severity
            severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            current_severity = threat.get('severity', 'low')
            if severity_order.get(current_severity, 0) > severity_order.get(actor_counts[actor]["max_severity"], 0):
                actor_counts[actor]["max_severity"] = current_severity
        
        # Convert sets to lists and sort
        actor_list = []
        for actor_data in actor_counts.values():
            actor_data["countries"] = list(actor_data["countries"])
            actor_data["threat_types"] = list(actor_data["threat_types"])
            actor_list.append(actor_data)
        
        return sorted(actor_list, key=lambda x: x["threat_count"], reverse=True)[:limit]
    
    def _generate_geo_threat(self) -> Dict[str, Any]:
        """Generate a realistic geographic threat"""
        # Select random location
        location_keys = list(self.threat_locations.keys())
        location_key = random.choice(location_keys)
        location_data = self.threat_locations[location_key]
        
        # Select random city in that country
        cities = list(location_data["cities"].keys())
        city_key = random.choice(cities)
        city_coords = location_data["cities"][city_key]
        
        # Generate threat details
        threat_types = ["malware", "phishing", "ddos", "data_breach", "ransomware", "apt", "botnet"]
        threat_actors = {
            "russia": ["APT28", "Fancy Bear", "Cozy Bear", "Turla"],
            "china": ["APT10", "Cloud Hopper", "Winnti Group", "Lucky Mouse"],
            "north_korea": ["Lazarus Group", "Hidden Cobra", "Andariel"],
            "iran": ["APT33", "ElFin", "Charming Kitten"],
            "usa": ["Unknown", "Insider Threat", "Criminal Group"],
            "uk": ["Unknown", "Insider Threat", "Cyber Criminal"],
            "germany": ["Unknown", "Hacktivist", "Cyber Criminal"],
            "france": ["Unknown", "APT", "Cyber Criminal"]
        }
        
        actors = threat_actors.get(location_key, ["Unknown"])
        
        threat = {
            "id": f"geo_{int(datetime.utcnow().timestamp() * 1000)}_{random.randint(1000, 9999)}",
            "location": {
                "country": location_data["country"],
                "city": city_key.title(),
                "latitude": city_coords["lat"] + random.uniform(-5, 5),  # Add some randomness
                "longitude": city_coords["lon"] + random.uniform(-5, 5)
            },
            "threat_type": random.choice(threat_types),
            "threat_actor": random.choice(actors),
            "severity": random.choices(["critical", "high", "medium", "low"], weights=[10, 25, 40, 25])[0],
            "confidence": random.randint(60, 95),
            "affected_assets": random.randint(1, 50),
            "first_seen": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        return threat
    
    def generate_threat_burst(self, count: int = 1) -> List[Dict[str, Any]]:
        """Generate multiple geographic threats"""
        threats = []
        for _ in range(count):
            threat = self._generate_geo_threat()
            self.active_threats.append(threat)
            self.threat_history.append(threat)
            threats.append(threat)
        
        # Keep only last 100 active threats
        if len(self.active_threats) > 100:
            self.active_threats = self.active_threats[-100:]
        
        # Keep only last 500 in history
        if len(self.threat_history) > 500:
            self.threat_history = self.threat_history[-500:]
        
        logger.info(f"Generated {count} geographic threats")
        return threats
    
    async def start_continuous_generation(self):
        """Start continuous geographic threat generation"""
        self.active = True
        logger.info("Starting continuous geographic threat generation...")
        
        while self.active:
            try:
                # Generate 1-3 threats every 8-15 seconds
                threat_count = random.randint(1, 3)
                await self.generate_threat_burst(threat_count)
                
                # Random delay between generations
                delay = random.randint(8, 15)
                await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error in continuous geo threat generation: {e}")
                await asyncio.sleep(5)
    
    def stop_generation(self):
        """Stop continuous generation"""
        self.active = False
        logger.info("Stopping geographic threat generation...")

# Global instance
geo_threat_mapper = GeoThreatMapper()
