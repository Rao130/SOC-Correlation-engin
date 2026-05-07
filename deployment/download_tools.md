# Deployment Tools Download Commands

## DOCKER INSTALLATION
### Windows:
1. **Download Docker Desktop:**
   ```
   https://www.docker.com/products/docker-desktop/
   ```
2. **Run installer and restart system**

## KUBECTL INSTALLATION  
### Windows:
1. **Download kubectl.exe:**
   ```
   https://kubernetes.io/docs/tasks/tools/windows-kubectl/
   ```
2. **Move to C:\Windows\System32 or add to PATH**

## TERRAFORM INSTALLATION
### Windows:
1. **Download Terraform:**
   ```
   https://www.terraform.io/downloads.html
   ```
2. **Extract and add to PATH**

## QUICK INSTALL COMMANDS

### Using Chocolatey (Recommended):
```powershell
# Install Chocolatey first
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install all tools
choco install docker-desktop kubernetes-cli terraform
```

### Using PowerShell:
```powershell
# Using winget (Windows 10+)
winget install Docker.DockerDesktop
winget install Kubernetes.kubectl
winget install Hashicorp.Terraform
```

### Using Chocolatey (Alternative):
```powershell
choco install docker-desktop
choco install kubernetes-cli  
choco install terraform
```

## VERIFICATION COMMANDS
```powershell
# Verify installations
docker --version
kubectl version --client
terraform --version
```

## NEXT STEPS
After installing tools:
1. Restart your computer
2. Run deployment test:
   ```
   python deployment/deploy_hybrid.py --dry-run
   ```
3. Run actual deployment:
   ```
   python deployment/deploy_hybrid.py --template production_hybrid
   ```
