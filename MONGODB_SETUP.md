# MongoDB Setup Instructions for SOC Correlation Engine

## Prerequisites
1. MongoDB installed and running on localhost:27017
2. Python 3.8+ with required packages

## MongoDB Installation

### Windows:
1. Download MongoDB Community Server from https://www.mongodb.com/try/download/community
2. Run the installer with default settings
3. Start MongoDB service:
   ```powershell
   net start MongoDB
   ```

### Linux (Ubuntu/Debian):
```bash
# Import MongoDB public key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update package list and install MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod
```

### macOS:
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb/brew/mongodb-community
```

## Configuration

The application is configured to use MongoDB by default with these settings:
- **URL**: mongodb://localhost:27017
- **Database**: soc_correlation_engine
- **Collections**: alerts, correlation_groups, reputation, logs

## Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_TYPE=mongodb
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=soc_correlation_engine
REDIS_URL=redis://localhost:6379
```

## Database Initialization

When you first start the application, it will:
1. Connect to MongoDB
2. Create the database and collections if they don't exist
3. Create indexes for optimal performance
4. Initialize empty collections

## MongoDB Compass (Optional GUI)

Download MongoDB Compass from https://www.mongodb.com/try/download/compass
- Connect to: `mongodb://localhost:27017`
- Database: `soc_correlation_engine`

## Troubleshooting

### Connection Issues:
1. Ensure MongoDB is running: `net start MongoDB` (Windows) or `sudo systemctl status mongod` (Linux)
2. Check if port 27017 is accessible
3. Verify firewall settings

### Performance:
- MongoDB automatically creates indexes on startup
- For large datasets, consider increasing RAM allocation
- Monitor performance with MongoDB Compass

## Backup and Restore

### Backup:
```bash
mongodump --db soc_correlation_engine --out backup/
```

### Restore:
```bash
mongorestore --db soc_correlation_engine backup/soc_correlation_engine/
```

## Production Considerations

1. **Security**: Enable authentication in MongoDB
2. **Performance**: Use replica sets for high availability
3. **Monitoring**: Set up MongoDB monitoring
4. **Backups**: Configure regular automated backups

## Connection String Examples

### Local MongoDB:
```
mongodb://localhost:27017
```

### MongoDB with Authentication:
```
mongodb://username:password@localhost:27017/soc_correlation_engine?authSource=admin
```

### MongoDB Atlas (Cloud):
```
mongodb+srv://username:password@cluster.mongodb.net/soc_correlation_engine
```
