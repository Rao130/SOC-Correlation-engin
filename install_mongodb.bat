@echo off
echo ========================================
echo MONGODB INSTALLATION SCRIPT
echo ========================================
echo.

echo Downloading MongoDB...
powershell -Command "Invoke-WebRequest -Uri 'https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-7.0.5-signed.msi' -OutFile 'mongodb_installer.msi'"

echo Installing MongoDB...
msiexec /i mongodb_installer.msi /quiet /norestart

echo Creating data directory...
mkdir C:\data\db 2>nul

echo Starting MongoDB service...
net start MongoDB

echo Cleaning up...
del mongodb_installer.msi

echo.
echo MongoDB installation completed!
echo You can now run your SOC Correlation Engine.
pause
