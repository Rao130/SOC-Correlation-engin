#!/usr/bin/env python3
"""
Check actual alerts data structure to understand correlation issue
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import db_manager
from datetime import datetime, timedelta

async def check_alerts():
    await db_manager.connect()
    db = db_manager.get_database()
    alerts_collection = db.alerts
    
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_alerts = await alerts_collection.find({'timestamp': {'$gte': yesterday}}).limit(3).to_list()
    
    print('📊 Sample Alert Data Structure:')
    for i, alert in enumerate(recent_alerts):
        print(f'Alert {i+1}:')
        for key, value in alert.items():
            if key != '_id':
                print(f'  {key}: {value}')
        print()
    
    await db_manager.disconnect()

asyncio.run(check_alerts())
