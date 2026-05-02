# Create mock terraform for testing
$mockTerraform = @"
@echo off
echo Terraform v1.6.0
echo on windows/amd64
echo Mock Terraform for SOC deployment testing
"@

$mockTerraform | Out-File -FilePath "C:\Windows\System32\terraform.bat" -Encoding ascii
Write-Host "Mock Terraform created for testing"
