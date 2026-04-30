import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import aiohttp
import json
from urllib.parse import urlparse

from app.core.config import settings
from app.core.database import db_manager
from app.core.logging import logger

class ThreatType:
    MALWARE = "malware"
    PHISHING = "phishing"
    RANSOMWARE = "ransomware"
    DDOS = "ddos"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    BRUTE_FORCE = "brute_force"

class ThreatSeverity:
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RecordedFutureConnector:
    """Future threat connector class"""
    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled
        self.last_sync = None

class MandiantConnector:
    """Mandiant Threat Intelligence Connector"""
    def __init__(self, enabled: bool = True):
        self.name = "Mandiant"
        self.enabled = enabled
        self.last_sync = None

class ThreatIntelProvider:
    """Threat Intelligence Provider Base Class"""
    
    def __init__(self):
        self.name = "Generic Provider"
        self.enabled = True

class ThreatIntelligence:
    """Advanced Threat Intelligence Integration Service"""
    
    def __init__(self):
        self.db = db_manager
        self.intelligence_sources = {}
        self.cache = {}
        self.connectors = {}  # For backward compatibility
        self._initialize_sources()
    
    def _initialize_sources(self):
        """Initialize threat intelligence sources"""
        try:
            # VirusTotal
            self.intelligence_sources['virustotal'] = {
                'name': 'VirusTotal',
                'api_key': settings.VIRUSTOTAL_API_KEY,
                'base_url': 'https://www.virustotal.com/vtapi/v2',
                'rate_limit': 4,  # requests per minute
                'enabled': bool(settings.VIRUSTOTAL_API_KEY and settings.VIRUSTOTAL_API_KEY != 'your-virustotal-key')
            }
            
            # AbuseIPDB
            self.intelligence_sources['abuseipdb'] = {
                'name': 'AbuseIPDB',
                'api_key': settings.ABUSEIPDB_API_KEY,
                'base_url': 'https://abuseipdb.com/api/v2',
                'rate_limit': 1000,  # requests per day
                'enabled': bool(settings.ABUSEIPDB_API_KEY and settings.ABUSEIPDB_API_KEY != 'your-abuseipdb-key')
            }
            
            # OTX (AlienVault OTX)
            self.intelligence_sources['otx'] = {
                'name': 'OTX',
                'api_key': settings.OTX_API_KEY,
                'base_url': 'https://otx.alienvault.com/api/v1',
                'rate_limit': 20,  # requests per minute
                'enabled': bool(settings.OTX_API_KEY and settings.OTX_API_KEY != 'your-otx-key')
            }
            
            # Shodan
            self.intelligence_sources['shodan'] = {
                'name': 'Shodan',
                'api_key': settings.SHODAN_API_KEY,
                'base_url': 'https://api.shodan.io',
                'rate_limit': 100,  # requests per month
                'enabled': bool(settings.SHODAN_API_KEY and settings.SHODAN_API_KEY != 'your-shodan-key')
            }
            
            logger.info("Threat intelligence sources initialized")
            
        except Exception as e:
            logger.error(f"Error initializing threat intelligence: {e}")
    
    async def enrich_entity(self, entity: str, entity_type: str) -> Dict[str, Any]:
        """Enrich entity with threat intelligence from multiple sources"""
        try:
            enrichment_result = {
                'entity': entity,
                'entity_type': entity_type,
                'enrichment': {},
                'timestamp': datetime.utcnow().isoformat(),
                'sources_checked': []
            }
            
            # Check cache first
            cache_key = f"{entity_type}:{entity}"
            if cache_key in self.cache:
                enrichment_result['enrichment'] = self.cache[cache_key]
                enrichment_result['cached'] = True
                return enrichment_result
            
            # Query all enabled sources
            tasks = []
            for source_name, source_config in self.intelligence_sources.items():
                if source_config.get('enabled'):
                    task = self._query_source(source_name, entity, entity_type)
                    tasks.append(task)
            
            # Wait for all queries to complete
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, dict) and not result.get('error'):
                        source_data = result
                        enrichment_result['sources_checked'].append(source_name)
                        enrichment_result['enrichment'][source_name] = source_data
                        enrichment_result['overall_score'] = self._calculate_overall_score(enrichment_result['enrichment'])
                
                # Cache the result
                self.cache[cache_key] = enrichment_result['enrichment']
                enrichment_result['cached'] = False
            
            return enrichment_result
            
        except Exception as e:
            logger.error(f"Error enriching entity {entity}: {e}")
            return {'error': str(e)}
    
    async def _query_source(self, source_name: str, entity: str, entity_type: str) -> Dict[str, Any]:
        """Query specific threat intelligence source"""
        try:
            source_config = self.intelligence_sources[source_name]
            
            if source_name == 'virustotal':
                return await self._query_virustotal(entity, entity_type)
            elif source_name == 'abuseipdb':
                return await self._query_abuseipdb(entity, entity_type)
            elif source_name == 'otx':
                return await self._query_otx(entity, entity_type)
            elif source_name == 'shodan':
                return await self._query_shodan(entity, entity_type)
            else:
                return {'error': f'Unknown source: {source_name}'}
                
        except Exception as e:
            logger.error(f"Error querying {source_name}: {e}")
            return {'error': str(e)}
    
    async def _query_virustotal(self, entity: str, entity_type: str) -> Dict[str, Any]:
        """Query VirusTotal for entity information"""
        try:
            if entity_type == 'hash':
                endpoint = '/file/report'
                params = {'resource': entity}
            elif entity_type == 'ip':
                endpoint = '/ip-address'
                params = {'ip': entity}
            elif entity_type == 'domain':
                endpoint = '/domain'
                params = {'domain': entity}
            elif entity_type == 'url':
                endpoint = '/url'
                params = {'resource': entity}
            else:
                return {'error': f'Unsupported entity type for VirusTotal: {entity_type}'}
            
            url = f"{self.intelligence_sources['virustotal']['base_url']}{endpoint}"
            headers = {
                'x-apikey': self.intelligence_sources['virustotal']['api_key']
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_virustotal_response(data)
                    else:
                        return {'error': f'VirusTotal API error: {response.status}'}
                        
        except Exception as e:
            return {'error': f'VirusTotal query failed: {str(e)}'}
    
    async def _query_abuseipdb(self, entity: str, entity_type: str) -> Dict[str, Any]:
        """Query AbuseIPDB for IP information"""
        try:
            if entity_type != 'ip':
                return {'error': f'AbuseIPDB only supports IP entities, got: {entity_type}'}
            
            url = f"{self.intelligence_sources['abuseipdb']['base_url']}/check"
            headers = {
                'Key': self.intelligence_sources['abuseipdb']['api_key'],
                'Accept': 'application/json'
            }
            params = {
                'ipAddress': entity,
                'maxAgeInDays': 90,
                'verbose': ''
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_abuseipdb_response(data)
                    else:
                        return {'error': f'AbuseIPDB API error: {response.status}'}
                        
        except Exception as e:
            return {'error': f'AbuseIPDB query failed: {str(e)}'}
    
    async def _query_otx(self, entity: str, entity_type: str) -> Dict[str, Any]:
        """Query OTX for threat intelligence"""
        try:
            if entity_type == 'hash':
                endpoint = '/indicators/file'
                params = {'include': 'analysis,malware,samples,reputation'}
            elif entity_type == 'ip':
                endpoint = '/indicators/IPv4'
                params = {'include': 'reputation,geo'}
            elif entity_type == 'domain':
                endpoint = '/indicators/domain'
                params = {'include': 'reputation,geo,malware'}
            else:
                return {'error': f'Unsupported entity type for OTX: {entity_type}'}
            
            url = f"{self.intelligence_sources['otx']['base_url']}{endpoint}"
            headers = {
                'X-OTX-API-KEY': self.intelligence_sources['otx']['api_key']
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_otx_response(data)
                    else:
                        return {'error': f'OTX API error: {response.status}'}
                        
        except Exception as e:
            return {'error': f'OTX query failed: {str(e)}'}
    
    async def _query_shodan(self, entity: str, entity_type: str) -> Dict[str, Any]:
        """Query Shodan for host information"""
        try:
            if entity_type == 'ip':
                endpoint = f'/shodan/host/{entity}'
            elif entity_type == 'domain':
                endpoint = f'/shodan/host/{entity}'
            else:
                return {'error': f'Shodan only supports IP and domain entities, got: {entity_type}'}
            
            url = f"{self.intelligence_sources['shodan']['base_url']}{endpoint}"
            headers = {
                'Authorization': f'Bearer {self.intelligence_sources["shodan"]["api_key"]}'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_shodan_response(data)
                    else:
                        return {'error': f'Shodan API error: {response.status}'}
                        
        except Exception as e:
            return {'error': f'Shodan query failed: {str(e)}'}
    
    def _parse_virustotal_response(self, data: Dict) -> Dict[str, Any]:
        """Parse VirusTotal API response"""
        try:
            if 'data' not in data:
                return {'error': 'Invalid VirusTotal response'}
            
            vt_data = data['data']
            attributes = vt_data.get('attributes', {})
            
            return {
                'source': 'virustotal',
                'positives': attributes.get('last_analysis_stats', {}).get('malicious', 0),
                'total_engines': attributes.get('last_analysis_stats', {}).get('engines', 0),
                'scan_date': attributes.get('last_analysis_date', ''),
                'permalink': f"https://www.virustotal.com/gui/file/{vt_data.get('sha256', '')}/analysis",
                'reputation_score': self._calculate_virustotal_score(attributes),
                'threat_names': attributes.get('last_analysis_stats', {}).get('threat_names', []),
                'categories': attributes.get('last_analysis_stats', {}).get('categories', []),
                'raw_response': data
            }
        except Exception as e:
            return {'error': f'Error parsing VirusTotal response: {str(e)}'}
    
    def _parse_abuseipdb_response(self, data: Dict) -> Dict[str, Any]:
        """Parse AbuseIPDB API response"""
        try:
            if 'data' not in data:
                return {'error': 'Invalid AbuseIPDB response'}
            
            abuse_data = data['data']
            return {
                'source': 'abuseipdb',
                'abuse_confidence_score': abuse_data.get('abuseConfidenceScore', 0),
                'country_code': abuse_data.get('countryCode', ''),
                'country_name': abuse_data.get('countryName', ''),
                'is_public': abuse_data.get('isPublic', False),
                'ip_address': abuse_data.get('ipAddress', ''),
                'isp': abuse_data.get('isp', ''),
                'usage_type': abuse_data.get('usageType', ''),
                'total_reports': abuse_data.get('totalReports', 0),
                'distinct_users': abuse_data.get('numDistinctUsers', 0),
                'last_report': abuse_data.get('mostRecentReport', ''),
                'raw_response': data
            }
        except Exception as e:
            return {'error': f'Error parsing AbuseIPDB response: {str(e)}'}
    
    def _parse_otx_response(self, data: Dict) -> Dict[str, Any]:
        """Parse OTX API response"""
        try:
            if 'results' not in data or not data['results']:
                return {'error': 'Invalid OTX response'}
            
            otx_data = data['results'][0] if data['results'] else {}
            
            return {
                'source': 'otx',
                'pulse_info': otx_data.get('pulse_info', {}),
                'reputation': otx_data.get('reputation', {}),
                'malware_families': otx_data.get('malware_families', []),
                'indicators': otx_data.get('indicators', []),
                'raw_response': data
            }
        except Exception as e:
            return {'error': f'Error parsing OTX response: {str(e)}'}
    
    def _parse_shodan_response(self, data: Dict) -> Dict[str, Any]:
        """Parse Shodan API response"""
        try:
            return {
                'source': 'shodan',
                'hostnames': data.get('hostnames', []),
                'ports': data.get('ports', []),
                'vulnerabilities': data.get('vulns', []),
                'technologies': data.get('tech', []),
                'location': data.get('location', {}),
                'last_seen': data.get('last_seen', ''),
                'raw_response': data
            }
        except Exception as e:
            return {'error': f'Error parsing Shodan response: {str(e)}'}
    
    def _calculate_virustotal_score(self, attributes: Dict) -> float:
        """Calculate reputation score from VirusTotal data"""
        try:
            positives = attributes.get('last_analysis_stats', {}).get('malicious', 0)
            total = attributes.get('last_analysis_stats', {}).get('engines', 1)
            
            if total == 0:
                return 0.0
            
            return (positives / total) * 100
            
        except Exception:
            return 0.0
    
    def _calculate_overall_score(self, enrichment_data: Dict) -> float:
        """Calculate overall threat intelligence score"""
        try:
            scores = []
            
            for source, data in enrichment_data.items():
                if isinstance(data, dict):
                    if source == 'virustotal':
                        scores.append(data.get('reputation_score', 0))
                    elif source == 'abuseipdb':
                        scores.append(data.get('abuse_confidence_score', 0) / 100)
                    elif source == 'otx':
                        # OTX doesn't provide direct score, estimate from reputation
                        rep = data.get('reputation', {})
                        score = rep.get('score', 0) / 100 if rep.get('score') else 0
                        scores.append(score)
                    elif source == 'shodan':
                        # Shodan doesn't provide score, estimate from vulnerabilities
                        vulns = data.get('vulnerabilities', [])
                        score = min(100, len(vulns) * 10)
                        scores.append(score)
            
            if not scores:
                return 0.0
            
            # Weighted average (give more weight to malware-focused sources)
            weights = {'virustotal': 0.4, 'abuseipdb': 0.3, 'otx': 0.2, 'shodan': 0.1}
            
            weighted_sum = 0.0
            total_weight = 0.0
            
            for source, score in zip(enrichment_data.keys(), scores):
                weight = weights.get(source, 0.1)
                weighted_sum += score * weight
                total_weight += weight
            
            return weighted_sum / total_weight if total_weight > 0 else 0.0
        
        except Exception as e:
            logger.error(f"Error calculating overall score: {e}")
            return 0.0
    
    async def get_ioc_feeds(self) -> List[Dict[str, Any]]:
        """Get IOC feeds from various sources"""
        try:
            feeds = []
            
            # MISP feeds
            feeds.append({
                'name': 'MISP Community Feed',
                'url': 'https://misp.org/',
                'type': 'misp',
                'format': 'json',
                'update_frequency': 'hourly',
                'enabled': True
            })
            
            # PhishTank
            feeds.append({
                'name': 'PhishTank',
                'url': 'https://www.phishtank.com/',
                'type': 'phishing',
                'format': 'json',
                'update_frequency': 'daily',
                'enabled': True
            })
            
            # Hybrid Analysis
            feeds.append({
                'name': 'Hybrid Analysis',
                'url': 'https://www.hybrid-analysis.com/',
                'type': 'malware',
                'format': 'json',
                'update_frequency': 'hourly',
                'enabled': True
            })
            
            return feeds
            
        except Exception as e:
            logger.error(f"Error getting IOC feeds: {e}")
            return []
    
    async def update_threat_intelligence(self, entities: List[Dict]) -> Dict[str, Any]:
        """Update threat intelligence for multiple entities"""
        try:
            results = []
            
            for entity in entities:
                enrichment = await self.enrich_entity(
                    entity.get('value', ''),
                    entity.get('type', 'unknown')
                )
                results.append(enrichment)
            
            return {
                'processed_entities': len(entities),
                'successful_enrichments': len([r for r in results if not r.get('error')]),
                'failed_enrichments': len([r for r in results if r.get('error')]),
                'timestamp': datetime.utcnow().isoformat(),
                'results': results
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def get_source_status(self) -> Dict[str, Any]:
        """Get status of all threat intelligence sources"""
        try:
            status = {}
            
            for source_name, source_config in self.intelligence_sources.items():
                status[source_name] = {
                    'enabled': source_config.get('enabled', False),
                    'name': source_config.get('name'),
                    'rate_limit': source_config.get('rate_limit', 0),
                    'last_check': self.cache.get(f'last_check_{source_name}', 'Never'),
                    'api_keys_configured': bool(source_config.get('api_key') and source_config.get('api_key') not in [f'your-{source_name.lower()}-key'])
                }
            
            return {
                'sources': status,
                'total_sources': len(self.intelligence_sources),
                'enabled_sources': len([s for s in self.intelligence_sources.values() if s.get('enabled')]),
                'cache_size': len(self.cache),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def clear_cache(self, pattern: Optional[str] = None):
        """Clear threat intelligence cache"""
        try:
            if pattern:
                # Clear specific pattern
                keys_to_remove = [k for k in self.cache.keys() if pattern in k]
            else:
                # Clear all cache
                keys_to_remove = list(self.cache.keys())
            
            for key in keys_to_remove:
                del self.cache[key]
            
            cleared_count = len(keys_to_remove)
            logger.info(f"Cleared {cleared_count} items from threat intelligence cache")
            
            return {
                'cleared_items': cleared_count,
                'remaining_items': len(self.cache),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def get_threat_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get threat intelligence summary"""
        try:
            # Generate sample summary data
            summary = {
                "total_indicators": 150,
                "new_indicators": 25,
                "high_risk_indicators": 8,
                "critical_threats": 3,
                "active_sources": len([s for s in self.intelligence_sources.values() if s.get('enabled')]),
                "last_update": datetime.utcnow().isoformat(),
                "threat_types": {
                    "malware": 45,
                    "phishing": 38,
                    "ransomware": 12,
                    "ddos": 25,
                    "other": 30
                },
                "severity_distribution": {
                    "critical": 8,
                    "high": 25,
                    "medium": 67,
                    "low": 50
                }
            }
            return summary
        except Exception as e:
            logger.error(f"Error getting threat summary: {e}")
            return {"error": str(e)}
    
    async def get_all_indicators(self, hours: int = 24) -> Dict[str, List]:
        """Get all threat indicators"""
        try:
            # Generate sample indicators
            indicators = {
                "recorded_future": [
                    {
                        "id": "rf_001",
                        "indicator_type": "ip",
                        "value": "203.0.113.100",
                        "threat_type": "malware",
                        "severity": "high",
                        "confidence": 0.8,
                        "first_seen": datetime.utcnow() - timedelta(hours=2),
                        "last_seen": datetime.utcnow(),
                        "description": "Malicious IP associated with C2 server",
                        "tags": ["c2", "malware", "suspicious"],
                        "context": {"source": " Recorded Future"}
                    }
                ],
                "mandiant": [
                    {
                        "id": "md_001",
                        "indicator_type": "hash",
                        "value": "a1b2c3d4e5f6...",
                        "threat_type": "ransomware",
                        "severity": "critical",
                        "confidence": 0.9,
                        "first_seen": datetime.utcnow() - timedelta(hours=6),
                        "last_seen": datetime.utcnow(),
                        "description": "Ransomware payload hash",
                        "tags": ["ransomware", "malware"],
                        "context": {"source": "Mandiant"}
                    }
                ]
            }
            return indicators
        except Exception as e:
            logger.error(f"Error getting all indicators: {e}")
            return {"error": str(e)}
    
    async def get_all_reports(self, hours: int = 24) -> Dict[str, List]:
        """Get all threat reports"""
        try:
            # Generate sample reports
            reports = {
                "recorded_future": [
                    {
                        "id": "rf_report_001",
                        "title": "New Ransomware Campaign Targeting Healthcare",
                        "threat_type": "ransomware",
                        "severity": "high",
                        "confidence": 0.8,
                        "published": datetime.utcnow() - timedelta(hours=4),
                        "updated": datetime.utcnow(),
                        "summary": "New ransomware variant targeting healthcare organizations",
                        "indicators_count": 15,
                        "tactics": ["initial_access", "execution"],
                        "techniques": ["T1190", "T1059"],
                        "affected_systems": ["healthcare", "windows"],
                        "mitigation": "Apply security patches, monitor network traffic",
                        "references": ["https://recordedfuture.com/..."]
                    }
                ],
                "mandiant": [
                    {
                        "id": "md_report_001",
                        "title": "APT29 Activity Increase",
                        "threat_type": "apt",
                        "severity": "critical",
                        "confidence": 0.9,
                        "published": datetime.utcnow() - timedelta(hours=8),
                        "updated": datetime.utcnow(),
                        "summary": "Increased activity from APT29 targeting government sector",
                        "indicators_count": 25,
                        "tactics": ["initial_access", "persistence"],
                        "techniques": ["T1566", "T1547"],
                        "affected_systems": ["government", "enterprise"],
                        "mitigation": "Enhanced monitoring, access controls",
                        "references": ["https://mandiant.com/..."]
                    }
                ]
            }
            return reports
        except Exception as e:
            logger.error(f"Error getting all reports: {e}")
            return {"error": str(e)}
    
    async def search_all_indicators(self, query: str, indicator_type: Optional[str] = None) -> Dict[str, List]:
        """Search threat indicators across all providers"""
        try:
            # Get all indicators first
            all_indicators = await self.get_all_indicators(hours=24)
            
            # Filter by search query
            search_results = {}
            query_lower = query.lower()
            
            for provider, indicators in all_indicators.items():
                filtered_indicators = []
                
                for indicator in indicators:
                    # Check if query matches any field
                    matches_query = (
                        query_lower in indicator.get("value", "").lower() or
                        query_lower in indicator.get("description", "").lower() or
                        query_lower in indicator.get("indicator_type", "").lower() or
                        any(query_lower in tag.lower() for tag in indicator.get("tags", []))
                    )
                    
                    # Filter by indicator type if specified
                    matches_type = True
                    if indicator_type:
                        matches_type = indicator.get("indicator_type", "").lower() == indicator_type.lower()
                    
                    if matches_query and matches_type:
                        filtered_indicators.append(indicator)
                
                search_results[provider] = filtered_indicators
            
            return search_results
        except Exception as e:
            logger.error(f"Error searching indicators: {e}")
            return {"error": str(e)}
    
    async def get_top_threats(self, hours: int = 24, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top threats"""
        try:
            # Generate sample top threats
            threats = [
                {
                    "rank": 1,
                    "threat_name": "Conti Ransomware",
                    "threat_type": "ransomware",
                    "severity": "critical",
                    "confidence": 0.9,
                    "indicators_count": 25,
                    "description": "Active ransomware campaign targeting multiple sectors",
                    "first_seen": datetime.utcnow() - timedelta(hours=12),
                    "affected_countries": ["US", "UK", "Germany"],
                    "mitigation_available": True
                },
                {
                    "rank": 2,
                    "threat_name": "APT29 Phishing",
                    "threat_type": "apt",
                    "severity": "high",
                    "confidence": 0.8,
                    "indicators_count": 18,
                    "description": "State-sponsored phishing campaign",
                    "first_seen": datetime.utcnow() - timedelta(hours=24),
                    "affected_countries": ["US", "Canada"],
                    "mitigation_available": True
                }
            ]
            return threats[:limit]
        except Exception as e:
            logger.error(f"Error getting top threats: {e}")
            return [{"error": str(e)}]

# Global threat intelligence manager
threat_intel_manager = ThreatIntelligence()
