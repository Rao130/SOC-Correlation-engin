import yaml
import os

def validate_docker_compose():
    """Validate docker-compose.yml syntax and structure"""
    try:
        print("🔍 Validating docker-compose.yml...")
        
        # Read the docker-compose file
        with open('docker-compose.yml', 'r') as f:
            content = f.read()
        
        # Parse YAML
        config = yaml.safe_load(content)
        
        print("✅ YAML syntax is valid")
        
        # Check required sections
        if 'version' not in config:
            print("❌ Missing version")
            return False
        else:
            print(f"✅ Version: {config['version']}")
        
        if 'services' not in config:
            print("❌ Missing services section")
            return False
        else:
            services = config['services']
            print(f"✅ Found {len(services)} services")
        
        # Check each service
        required_services = ['soc-engine', 'mongodb', 'redis']
        for service in required_services:
            if service in services:
                print(f"✅ Service '{service}' found")
            else:
                print(f"❌ Service '{service}' missing")
                return False
        
        # Check for duplicate services
        service_names = list(services.keys())
        if len(service_names) != len(set(service_names)):
            print("❌ Duplicate service names found")
            duplicates = [name for name in service_names if service_names.count(name) > 1]
            print(f"   Duplicates: {set(duplicates)}")
            return False
        else:
            print("✅ No duplicate services")
        
        # Check port conflicts
        ports_used = {}
        for service_name, service_config in services.items():
            if 'ports' in service_config:
                for port_mapping in service_config['ports']:
                    if ':' in port_mapping:
                        host_port = port_mapping.split(':')[0]
                        if host_port in ports_used:
                            print(f"❌ Port conflict: {host_port} used by both {ports_used[host_port]} and {service_name}")
                            return False
                        else:
                            ports_used[host_port] = service_name
        
        print("✅ No port conflicts")
        print(f"✅ Ports used: {list(ports_used.keys())}")
        
        # Check networks
        if 'networks' not in config:
            print("❌ Missing networks section")
            return False
        else:
            networks = config['networks']
            print(f"✅ Found {len(networks)} networks")
            
            if 'soc-network' not in networks:
                print("❌ Missing soc-network")
                return False
            else:
                print("✅ soc-network found")
        
        # Check volumes
        if 'volumes' not in config:
            print("❌ Missing volumes section")
            return False
        else:
            volumes = config['volumes']
            print(f"✅ Found {len(volumes)} volumes")
        
        # Check service dependencies
        if 'soc-engine' in services:
            deps = services['soc-engine'].get('depends_on', {})
            if 'mongodb' not in deps:
                print("⚠️ soc-engine doesn't depend on mongodb")
            if 'redis' not in deps:
                print("⚠️ soc-engine doesn't depend on redis")
        
        print("\n🎉 docker-compose.yml is VALID!")
        print("\n📋 Service Summary:")
        for service_name, service_config in services.items():
            ports = service_config.get('ports', [])
            image = service_config.get('image', 'build')
            print(f"  • {service_name}: {image} (ports: {ports})")
        
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error: {e}")
        return False
    except FileNotFoundError:
        print("❌ docker-compose.yml not found")
        return False
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

if __name__ == "__main__":
    validate_docker_compose()
