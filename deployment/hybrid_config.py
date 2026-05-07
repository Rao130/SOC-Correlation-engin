"""
Hybrid Deployment Configuration for SOC Correlation Engine
"""
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import yaml
import json
from datetime import datetime

class Environment(Enum):
    LOCAL = "local"
    CLOUD = "cloud"
    EDGE = "edge"
    HYBRID = "hybrid"

class DeploymentType(Enum):
    ON_PREMISES = "on_premises"
    CLOUD_MANAGED = "cloud_managed"
    CONTAINER_ORCHESTRATION = "container_orchestration"
    HYBRID_MULTI_CLOUD = "hybrid_multi_cloud"

@dataclass
class ServerConfig:
    """Server configuration"""
    environment: Environment
    host: str
    port: int
    ssl_enabled: bool
    workers: int
    max_connections: int
    database_url: str
    redis_url: str
    log_level: str

@dataclass
class CloudConfig:
    """Cloud provider configuration"""
    provider: str  # aws, azure, gcp
    region: str
    instance_type: str
    storage_type: str
    auto_scaling: bool
    backup_retention: int
    monitoring_enabled: bool

@dataclass
class SecurityConfig:
    """Security configuration"""
    ssl_cert_path: Optional[str]
    ssl_key_path: Optional[str]
    jwt_secret: str
    encryption_key: str
    firewall_rules: List[Dict]
    access_control: Dict
    audit_logging: bool

@dataclass
class HybridConfig:
    """Hybrid deployment configuration"""
    primary_environment: Environment
    secondary_environments: List[Environment]
    sync_strategy: str
    failover_enabled: bool
    load_balancing: bool
    data_replication: bool

class HybridDeploymentManager:
    """Manage hybrid deployment configurations"""
    
    def __init__(self):
        self.configs = {}
        self.active_config = None
        self.deployment_templates = {}
        
    def initialize_deployment_templates(self):
        """Initialize deployment templates"""
        self.deployment_templates = {
            "production_hybrid": {
                "name": "Production Hybrid Deployment",
                "description": "Production-ready hybrid deployment with local and cloud components",
                "environments": {
                    "local": {
                        "type": "on_premises",
                        "purpose": "sensitive_data_processing",
                        "components": ["database", "correlation_engine", "api_gateway"],
                        "resources": {
                            "cpu": "8 cores",
                            "memory": "32GB",
                            "storage": "1TB SSD",
                            "network": "10Gbps"
                        }
                    },
                    "cloud": {
                        "type": "aws_ec2",
                        "purpose": "scalability_and_backup",
                        "components": ["web_interface", "analytics", "reporting", "backup"],
                        "resources": {
                            "instance_type": "t3.xlarge",
                            "storage": "500GB EBS",
                            "auto_scaling": {
                                "min_instances": 2,
                                "max_instances": 10,
                                "target_cpu": 70
                            }
                        }
                    },
                    "edge": {
                        "type": "edge_nodes",
                        "purpose": "remote_site_processing",
                        "components": ["data_collection", "preprocessing"],
                        "locations": ["site_a", "site_b", "site_c"],
                        "resources": {
                            "cpu": "4 cores",
                            "memory": "8GB",
                            "storage": "256GB SSD"
                        }
                    }
                },
                "networking": {
                    "vpn_tunnels": ["local_to_cloud", "edge_to_local"],
                    "load_balancer": "application_load_balancer",
                    "dns_failover": True,
                    "cdn_integration": True
                },
                "security": {
                    "encryption": "end_to_end",
                    "authentication": "multi_factor",
                    "authorization": "rbac",
                    "monitoring": "siem_integration"
                },
                "data_flow": {
                    "local_to_cloud": "encrypted_sync",
                    "cloud_to_local": "read_only_replica",
                    "edge_to_local": "secure_tunnel",
                    "backup_strategy": "3_2_1_rule"
                }
            },
            "development_hybrid": {
                "name": "Development Hybrid Deployment",
                "description": "Development environment with hybrid capabilities",
                "environments": {
                    "local": {
                        "type": "docker_compose",
                        "purpose": "development_testing",
                        "components": ["all_services"],
                        "resources": {
                            "cpu": "4 cores",
                            "memory": "16GB",
                            "storage": "500GB"
                        }
                    },
                    "cloud": {
                        "type": "aws_ec2",
                        "purpose": "staging_environment",
                        "components": ["staging_api", "test_database"],
                        "resources": {
                            "instance_type": "t3.medium",
                            "storage": "100GB EBS"
                        }
                    }
                }
            },
            "disaster_recovery": {
                "name": "Disaster Recovery Setup",
                "description": "Multi-region disaster recovery configuration",
                "environments": {
                    "primary": {
                        "type": "on_premises",
                        "purpose": "primary_production",
                        "components": ["all_services"],
                        "location": "datacenter_a"
                    },
                    "secondary": {
                        "type": "cloud_multi_region",
                        "purpose": "disaster_recovery",
                        "components": ["backup_services", "standby_database"],
                        "regions": ["us-east-1", "us-west-2", "eu-west-1"],
                        "rto": "4_hours",
                        "rpo": "1_hour"
                    }
                }
            }
        }
    
    def create_hybrid_config(self, template_name: str, customizations: Dict = None) -> HybridConfig:
        """Create hybrid configuration from template"""
        if template_name not in self.deployment_templates:
            raise ValueError(f"Template {template_name} not found")
        
        template = self.deployment_templates[template_name]
        
        # Apply customizations
        if customizations:
            template.update(customizations)
        
        # Create configuration objects
        primary_env = Environment.LOCAL  # Default primary
        secondary_envs = [Environment.CLOUD, Environment.EDGE]
        
        config = HybridConfig(
            primary_environment=primary_env,
            secondary_environments=secondary_envs,
            sync_strategy="bidirectional_encrypted",
            failover_enabled=True,
            load_balancing=True,
            data_replication=True
        )
        
        return config
    
    def generate_docker_compose(self, environment: str = "local") -> str:
        """Generate Docker Compose configuration"""
        compose_config = {
            "version": "3.8",
            "services": {
                "mongodb": {
                    "image": "mongo:6.0",
                    "container_name": "soc_mongodb",
                    "restart": "unless-stopped",
                    "environment": {
                        "MONGO_INITDB_ROOT_USERNAME": "admin",
                        "MONGO_INITDB_ROOT_PASSWORD": "${MONGO_PASSWORD}",
                        "MONGO_INITDB_DATABASE": "soc_correlation_engine"
                    },
                    "volumes": [
                        "mongodb_data:/data/db",
                        "./init-mongo.js:/docker-entrypoint-initdb.d/init-mongo.js:ro"
                    ],
                    "ports": ["27017:27017"],
                    "networks": ["soc_network"]
                },
                "redis": {
                    "image": "redis:7-alpine",
                    "container_name": "soc_redis",
                    "restart": "unless-stopped",
                    "command": "redis-server --requirepass ${REDIS_PASSWORD}",
                    "volumes": ["redis_data:/data"],
                    "ports": ["6379:6379"],
                    "networks": ["soc_network"]
                },
                "soc_api": {
                    "build": {
                        "context": ".",
                        "dockerfile": "Dockerfile"
                    },
                    "container_name": "soc_api",
                    "restart": "unless-stopped",
                    "environment": {
                        "DATABASE_URL": "mongodb://admin:${MONGO_PASSWORD}@mongodb:27017/soc_correlation_engine?authSource=admin",
                        "REDIS_URL": "redis://:${REDIS_PASSWORD}@redis:6379/0",
                        "JWT_SECRET": "${JWT_SECRET}",
                        "ENCRYPTION_KEY": "${ENCRYPTION_KEY}",
                        "LOG_LEVEL": "INFO",
                        "ENVIRONMENT": environment
                    },
                    "ports": ["8000:8000"],
                    "depends_on": ["mongodb", "redis"],
                    "volumes": ["./logs:/app/logs"],
                    "networks": ["soc_network"]
                },
                "nginx": {
                    "image": "nginx:alpine",
                    "container_name": "soc_nginx",
                    "restart": "unless-stopped",
                    "ports": ["80:80", "443:443"],
                    "volumes": [
                        "./nginx.conf:/etc/nginx/nginx.conf:ro",
                        "./ssl:/etc/nginx/ssl:ro"
                    ],
                    "depends_on": ["soc_api"],
                    "networks": ["soc_network"]
                }
            },
            "volumes": {
                "mongodb_data": {"driver": "local"},
                "redis_data": {"driver": "local"}
            },
            "networks": {
                "soc_network": {"driver": "bridge"}
            }
        }
        
        return yaml.dump(compose_config, default_flow_style=False)
    
    def generate_kubernetes_manifests(self, environment: str = "cloud") -> Dict:
        """Generate Kubernetes manifests"""
        manifests = {}
        
        # Namespace
        manifests["namespace"] = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": "soc-correlation-engine",
                "labels": {
                    "name": "soc-correlation-engine",
                    "environment": environment
                }
            }
        }
        
        # ConfigMap
        manifests["configmap"] = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "soc-config",
                "namespace": "soc-correlation-engine"
            },
            "data": {
                "ENVIRONMENT": environment,
                "LOG_LEVEL": "INFO",
                "REDIS_HOST": "redis-service",
                "MONGODB_HOST": "mongodb-service"
            }
        }
        
        # Secret
        manifests["secret"] = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "soc-secrets",
                "namespace": "soc-correlation-engine"
            },
            "type": "Opaque",
            "data": {
                "MONGODB_PASSWORD": "YWRtaW4=",  # base64 encoded
                "REDIS_PASSWORD": "cGFzc3dvcmQ=",
                "JWT_SECRET": "c3VwZXJfc2VjcmV0X2tleQ==",
                "ENCRYPTION_KEY": "ZW5jcnlwdGlvbl9rZXk="
            }
        }
        
        # MongoDB StatefulSet
        manifests["mongodb"] = {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": "mongodb",
                "namespace": "soc-correlation-engine"
            },
            "spec": {
                "serviceName": "mongodb-service",
                "replicas": 1,
                "selector": {
                    "matchLabels": {"app": "mongodb"}
                },
                "template": {
                    "metadata": {
                        "labels": {"app": "mongodb"}
                    },
                    "spec": {
                        "containers": [{
                            "name": "mongodb",
                            "image": "mongo:6.0",
                            "ports": [{"containerPort": 27017}],
                            "env": [
                                {"name": "MONGO_INITDB_ROOT_USERNAME", "value": "admin"},
                                {"name": "MONGO_INITDB_ROOT_PASSWORD", "valueFrom": {"secretKeyRef": {"name": "soc-secrets", "key": "MONGODB_PASSWORD"}}}
                            ],
                            "volumeMounts": [{"name": "mongodb-storage", "mountPath": "/data/db"}]
                        }]
                    }
                },
                "volumeClaimTemplates": [{
                    "metadata": {"name": "mongodb-storage"},
                    "spec": {
                        "accessModes": ["ReadWriteOnce"],
                        "resources": {"requests": {"storage": "100Gi"}}
                    }
                }]
            }
        }
        
        # API Deployment
        manifests["api"] = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "soc-api",
                "namespace": "soc-correlation-engine"
            },
            "spec": {
                "replicas": 3,
                "selector": {
                    "matchLabels": {"app": "soc-api"}
                },
                "template": {
                    "metadata": {
                        "labels": {"app": "soc-api"}
                    },
                    "spec": {
                        "containers": [{
                            "name": "soc-api",
                            "image": "soc-correlation-engine:latest",
                            "ports": [{"containerPort": 8000}],
                            "envFrom": [
                                {"configMapRef": {"name": "soc-config"}},
                                {"secretRef": {"name": "soc-secrets"}}
                            ],
                            "resources": {
                                "requests": {
                                    "memory": "512Mi",
                                    "cpu": "250m"
                                },
                                "limits": {
                                    "memory": "2Gi",
                                    "cpu": "1000m"
                                }
                            },
                            "livenessProbe": {
                                "httpGet": {"path": "/health", "port": 8000},
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {"path": "/ready", "port": 8000},
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
        
        # Services
        manifests["services"] = {
            "mongodb-service": {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "mongodb-service",
                    "namespace": "soc-correlation-engine"
                },
                "spec": {
                    "selector": {"app": "mongodb"},
                    "ports": [{"port": 27017, "targetPort": 27017}],
                    "type": "ClusterIP"
                }
            },
            "api-service": {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "api-service",
                    "namespace": "soc-correlation-engine"
                },
                "spec": {
                    "selector": {"app": "soc-api"},
                    "ports": [{"port": 80, "targetPort": 8000}],
                    "type": "LoadBalancer"
                }
            }
        }
        
        return manifests
    
    def generate_terraform_config(self, cloud_provider: str = "aws") -> str:
        """Generate Terraform configuration for cloud deployment"""
        if cloud_provider == "aws":
            return self._generate_aws_terraform()
        elif cloud_provider == "azure":
            return self._generate_azure_terraform()
        elif cloud_provider == "gcp":
            return self._generate_gcp_terraform()
        else:
            raise ValueError(f"Cloud provider {cloud_provider} not supported")
    
    def _generate_aws_terraform(self) -> str:
        """Generate AWS Terraform configuration"""
        terraform_config = '''
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC Configuration
resource "aws_vpc" "soc_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name        = "soc-vpc"
    Environment = var.environment
  }
}

# Subnets
resource "aws_subnet" "public_subnet" {
  count             = 2
  vpc_id            = aws_vpc.soc_vpc.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  map_public_ip_on_launch = true
  
  tags = {
    Name        = "soc-public-subnet-${count.index + 1}"
    Environment = var.environment
  }
}

resource "aws_subnet" "private_subnet" {
  count             = 2
  vpc_id            = aws_vpc.soc_vpc.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name        = "soc-private-subnet-${count.index + 1}"
    Environment = var.environment
  }
}

# Security Groups
resource "aws_security_group" "soc_sg" {
  name_prefix = "soc-sg-"
  vpc_id      = aws_vpc.soc_vpc.id
  
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "API"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name        = "soc-security-group"
    Environment = var.environment
  }
}

# EC2 Instances
resource "aws_instance" "soc_api" {
  count                  = var.instance_count
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public_subnet[count.index % 2].id
  vpc_security_group_ids = [aws_security_group.soc_sg.id]
  
  user_data = templatefile("user_data.sh", {
    environment = var.environment
    db_host     = aws_db_instance.soc_database.address
  })
  
  tags = {
    Name        = "soc-api-${count.index + 1}"
    Environment = var.environment
  }
}

# RDS Database
resource "aws_db_instance" "soc_database" {
  identifier = "soc-database-${var.environment}"
  
  engine         = "mongodb"
  engine_version = "6.0"
  instance_class = var.db_instance_class
  
  allocated_storage     = var.db_storage
  max_allocated_storage = var.db_max_storage
  storage_type         = "gp2"
  storage_encrypted    = true
  
  db_name  = "soc_correlation_engine"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.soc_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.soc_db_subnet.name
  
  backup_retention_period = var.backup_retention
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = false
  
  tags = {
    Name        = "soc-database"
    Environment = var.environment
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "soc_asg" {
  name                = "soc-asg-${var.environment}"
  vpc_zone_identifier = aws_subnet.public_subnet[*].id
  target_group_arns   = [aws_lb_target_group.soc_tg.arn]
  health_check_type    = "EC2"
  health_check_grace_period = 300
  
  min_size         = var.min_instances
  max_size         = var.max_instances
  desired_capacity  = var.desired_instances
  
  launch_template {
    id      = aws_launch_template.soc_lt.id
    version = "$Latest"
  }
  
  tag {
    key                 = "Name"
    value               = "soc-api"
    propagate_at_launch = true
  }
  
  tag {
    key                 = "Environment"
    value               = var.environment
    propagate_at_launch = true
  }
}

# Application Load Balancer
resource "aws_lb" "soc_alb" {
  name               = "soc-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.soc_sg.id]
  subnets            = aws_subnet.public_subnet[*].id
  
  enable_deletion_protection = false
  
  tags = {
    Name        = "soc-alb"
    Environment = var.environment
  }
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "instance_count" {
  description = "Number of instances"
  type        = number
  default     = 2
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.xlarge"
}

variable "min_instances" {
  description = "Minimum number of instances"
  type        = number
  default     = 2
}

variable "max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 10
}

variable "desired_instances" {
  description = "Desired number of instances"
  type        = number
  default     = 3
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r5.large"
}

variable "db_storage" {
  description = "RDS storage size in GB"
  type        = number
  default     = 500
}

variable "db_max_storage" {
  description = "Maximum RDS storage in GB"
  type        = number
  default     = 1000
}

variable "backup_retention" {
  description = "Backup retention period in days"
  type        = number
  default     = 30
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "admin"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}
'''
        return terraform_config
    
    def _generate_azure_terraform(self) -> str:
        """Generate Azure Terraform configuration"""
        # Azure-specific Terraform config
        return '''
# Azure Terraform configuration for SOC Correlation Engine
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Resource Group
resource "azurerm_resource_group" "soc_rg" {
  name     = "soc-correlation-engine-${var.environment}"
  location = var.azure_region
}

# Virtual Network
resource "azurerm_virtual_network" "soc_vnet" {
  name                = "soc-vnet-${var.environment}"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.soc_rg.location
  resource_group_name = azurerm_resource_group.soc_rg.name
}

# Subnet
resource "azurerm_subnet" "soc_subnet" {
  name                 = "soc-subnet-${var.environment}"
  resource_group_name  = azurerm_resource_group.soc_rg.name
  virtual_network_name = azurerm_virtual_network.soc_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Network Security Group
resource "azurerm_network_security_group" "soc_nsg" {
  name                = "soc-nsg-${var.environment}"
  location            = azurerm_resource_group.soc_rg.location
  resource_group_name = azurerm_resource_group.soc_rg.name
}

# Public IP
resource "azurerm_public_ip" "soc_public_ip" {
  name                = "soc-pip-${var.environment}"
  location            = azurerm_resource_group.soc_rg.location
  resource_group_name = azurerm_resource_group.soc_rg.name
  allocation_method   = "Static"
  sku                = "Standard"
}

# Virtual Machine
resource "azurerm_linux_virtual_machine" "soc_vm" {
  name                  = "soc-vm-${var.environment}"
  location              = azurerm_resource_group.soc_rg.location
  resource_group_name   = azurerm_resource_group.soc_rg.name
  network_interface_ids = [azurerm_network_interface.soc_nic.id]
  size                  = var.vm_size
  
  admin_username = var.admin_username
  admin_ssh_key {
    username   = var.admin_username
    public_key = file(var.public_key_path)
  }
  
  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
    disk_size_gb         = var.disk_size_gb
  }
  
  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts-gen2"
    version   = "latest"
  }
}

# Variables
variable "azure_region" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "vm_size" {
  description = "Virtual machine size"
  type        = string
  default     = "Standard_D4s_v3"
}

variable "disk_size_gb" {
  description = "Disk size in GB"
  type        = number
  default     = 128
}

variable "admin_username" {
  description = "Admin username"
  type        = string
  default     = "azureuser"
}

variable "public_key_path" {
  description = "Path to public SSH key"
  type        = string
}
'''
    
    def _generate_gcp_terraform(self) -> str:
        """Generate GCP Terraform configuration"""
        # GCP-specific Terraform config
        return '''
# GCP Terraform configuration for SOC Correlation Engine
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.gcp_project
  region  = var.gcp_region
}

# VPC Network
resource "google_compute_network" "soc_vpc" {
  name                    = "soc-vpc-${var.environment}"
  auto_create_subnetworks = false
}

# Subnet
resource "google_compute_subnetwork" "soc_subnet" {
  name          = "soc-subnet-${var.environment}"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.gcp_region
  network       = google_compute_network.soc_vpc.id
}

# Firewall Rules
resource "google_compute_firewall" "soc_firewall" {
  name    = "soc-firewall-${var.environment}"
  network = google_compute_network.soc_vpc.name
  
  allow {
    protocol = "tcp"
    ports    = ["22", "80", "443", "8000"]
  }
  
  source_ranges = ["0.0.0.0/0"]
}

# Compute Instance
resource "google_compute_instance" "soc_vm" {
  name         = "soc-vm-${var.environment}"
  machine_type = var.machine_type
  zone         = var.gcp_zone
  
  boot_disk {
    initialize_params {
      image = data.google_compute_image.ubuntu.self_link
      size  = var.disk_size_gb
      type  = "pd-ssd"
    }
  }
  
  network_interface {
    subnetwork = google_compute_subnetwork.soc_subnet.self_link
    access_config {
      # Ephemeral IP
    }
  }
  
  metadata = {
    ssh-keys = "${var.ssh_user}:${file(var.public_key_path)}"
  }
}

# Data
data "google_compute_image" "ubuntu" {
  family  = "ubuntu-2004-lts"
  project = "ubuntu-os-cloud"
}

# Variables
variable "gcp_project" {
  description = "GCP project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "gcp_zone" {
  description = "GCP zone"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "machine_type" {
  description = "Machine type"
  type        = string
  default     = "e2-standard-4"
}

variable "disk_size_gb" {
  description = "Disk size in GB"
  type        = number
  default     = 100
}

variable "ssh_user" {
  description = "SSH username"
  type        = string
  default     = "ubuntu"
}

variable "public_key_path" {
  description = "Path to public SSH key"
  type        = string
}
'''
    
    def generate_deployment_script(self, config: HybridConfig) -> str:
        """Generate deployment script"""
        script = f'''#!/bin/bash
# SOC Correlation Engine - Hybrid Deployment Script
# Generated: {datetime.now().isoformat()}

set -e

echo "Starting SOC Correlation Engine Hybrid Deployment..."

# Environment setup
export ENVIRONMENT={config.primary_environment.value}
export DEPLOYMENT_TYPE=hybrid

# Check prerequisites
echo "Checking prerequisites..."
command -v docker >/dev/null 2>&1 || {{ echo "Docker is required but not installed." >&2; exit 1; }}
command -v kubectl >/dev/null 2>&1 || {{ echo "kubectl is required but not installed." >&2; exit 1; }}
command -v terraform >/dev/null 2>&1 || {{ echo "Terraform is required but not installed." >&2; exit 1; }}

# Deploy local environment
echo "Deploying local environment..."
docker-compose -f docker-compose.local.yml up -d

# Deploy cloud environment
echo "Deploying cloud environment..."
cd infrastructure/
terraform init
terraform plan -var-file="production.tfvars"
terraform apply -auto-approve -var-file="production.tfvars"

# Deploy edge nodes
echo "Deploying edge nodes..."
for site in site_a site_b site_c; do
    echo "Deploying edge node: $site"
    scp -r edge-deployment/ $site-user@$site-site:~/
    ssh $site-user@$site-site "cd edge-deployment && docker-compose up -d"
done

# Configure networking
echo "Configuring hybrid networking..."
./scripts/setup-vpn-tunnels.sh
./scripts/configure-load-balancer.sh

# Setup monitoring
echo "Setting up monitoring..."
./scripts/deploy-monitoring.sh

# Run health checks
echo "Running health checks..."
./scripts/health-check.sh

echo "Hybrid deployment completed successfully!"
echo "Dashboard available at: https://your-domain.com"
echo "Monitoring available at: https://monitoring.your-domain.com"
'''
        return script
