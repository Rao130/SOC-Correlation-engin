#!/bin/bash
# SOC Correlation Engine - Hybrid Deployment Script
# Generated: 2026-05-02T13:19:33.875536

set -e

echo "Starting SOC Correlation Engine Hybrid Deployment..."

# Environment setup
export ENVIRONMENT=local
export DEPLOYMENT_TYPE=hybrid

# Check prerequisites
echo "Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed." >&2; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "kubectl is required but not installed." >&2; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "Terraform is required but not installed." >&2; exit 1; }

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
