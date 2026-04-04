import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio
from collections import defaultdict

class FileDatabase:
    """Simple file-based database for demo purposes"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize data files
        self.alerts_file = self.data_dir / "alerts.json"
        self.reputation_file = self.data_dir / "reputation.json"
        self.correlations_file = self.data_dir / "correlations.json"
        self.logs_file = self.data_dir / "logs.json"
        
        # Load existing data
        self._load_data()
    
    def _load_data(self):
        """Load data from files"""
        try:
            if self.alerts_file.exists():
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    self.alerts = json.load(f)
            else:
                self.alerts = []
        except:
            self.alerts = []
        
        try:
            if self.reputation_file.exists():
                with open(self.reputation_file, 'r', encoding='utf-8') as f:
                    self.reputation = json.load(f)
            else:
                self.reputation = []
        except:
            self.reputation = []
        
        try:
            if self.correlations_file.exists():
                with open(self.correlations_file, 'r', encoding='utf-8') as f:
                    self.correlations = json.load(f)
            else:
                self.correlations = []
        except:
            self.correlations = []
        
        try:
            if self.logs_file.exists():
                with open(self.logs_file, 'r', encoding='utf-8') as f:
                    self.logs = json.load(f)
            else:
                self.logs = []
        except:
            self.logs = []
    
    def _save_data(self):
        """Save data to files"""
        try:
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump(self.alerts, f, indent=2, default=str)
            
            with open(self.reputation_file, 'w', encoding='utf-8') as f:
                json.dump(self.reputation, f, indent=2, default=str)
            
            with open(self.correlations_file, 'w', encoding='utf-8') as f:
                json.dump(self.correlations, f, indent=2, default=str)
            
            with open(self.logs_file, 'w', encoding='utf-8') as f:
                json.dump(self.logs, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def __getattr__(self, name):
        """Get collection by name"""
        if name == 'alerts':
            return MockCollection(self.alerts, self._save_data)
        elif name == 'reputation':
            return MockCollection(self.reputation, self._save_data)
        elif name == 'correlation_groups':
            return MockCollection(self.correlations, self._save_data)
        elif name == 'logs':
            return MockCollection(self.logs, self._save_data)
        else:
            return MockCollection([], self._save_data)

class MockCollection:
    """Mock collection that works with file storage"""
    
    def __init__(self, data: List[Dict], save_callback):
        self.data = data
        self.save_callback = save_callback
    
    async def find(self, query: Optional[Dict] = None):
        """Find documents with optional filtering"""
        if not query:
            return MockCursor(self.data)
        
        # Simple filtering implementation
        filtered = self.data
        if query:
            filtered = []
            for doc in self.data:
                match = True
                for key, value in query.items():
                    if key == '$or':
                        # Handle $or queries
                        or_match = False
                        for or_condition in value:
                            for or_key, or_value in or_condition.items():
                                if isinstance(or_value, str) and or_value.lower() in str(doc.get(or_key, '')).lower():
                                    or_match = True
                                    break
                        if or_match:
                            match = True
                            break
                    elif key in doc and (isinstance(value, str) and value.lower() in str(doc[key]).lower()):
                        match = True
                    elif key in doc and doc[key] == value:
                        match = True
                    else:
                        match = False
                    if not match:
                        break
                if match:
                    filtered.append(doc)
            filtered = filtered
        return MockCursor(filtered)
    
    async def find_one(self, query: Optional[Dict] = None):
        """Find one document"""
        result = await self.find(query)
        return result.data[0] if result.data else None
    
    async def insert_one(self, document: Dict):
        """Insert one document"""
        document['_id'] = f"file_{len(self.data)}"
        document['created_at'] = datetime.utcnow().isoformat()
        self.data.append(document)
        self.save_callback()
        return MockInsertResult(document['_id'])
    
    async def update_one(self, query: Dict, update: Dict):
        """Update one document"""
        for doc in self.data:
            match = True
            for key, value in query.items():
                if key in doc and doc[key] == value:
                    match = True
                else:
                    match = False
                    break
            
            if match:
                if '$set' in update:
                    doc.update(update['$set'])
                doc['updated_at'] = datetime.utcnow().isoformat()
                self.save_callback()
                return MockUpdateResult()
        
        return MockUpdateResult()
    
    async def delete_one(self, query: Dict):
        """Delete one document"""
        for i, doc in enumerate(self.data):
            match = True
            for key, value in query.items():
                if key in doc and doc[key] == value:
                    match = True
                else:
                    match = False
                    break
            
            if match:
                del self.data[i]
                self.save_callback()
                return MockDeleteResult()
        
        return MockDeleteResult()
    
    async def count_documents(self, query: Optional[Dict] = None):
        """Count documents"""
        result = await self.find(query)
        return len(result.data)
    
    async def aggregate(self, pipeline: List[Dict]):
        """Simple aggregation"""
        # Basic aggregation implementation
        result = []
        
        # Handle $group operations
        for stage in pipeline:
            if '$group' in stage:
                group_spec = stage['$group']
                if '_id' in group_spec and '$sum' in group_spec:
                    # Simple sum grouping
                    groups = defaultdict(int)
                    for doc in self.data:
                        group_key = doc.get(group_spec['_id'], 'unknown')
                        groups[group_key] += doc.get(group_spec['$sum'], 0)
                    
                    for key, value in groups.items():
                        result.append({'_id': key, 'count': value})
        
        return MockCursor(result)
    
    def create_index(self, *args, **kwargs):
        """Mock index creation"""
        pass

class MockCursor:
    """Mock cursor for file database"""
    
    def __init__(self, data: List[Dict]):
        self.data = data
    
    def sort(self, *args):
        """Sort data"""
        if args:
            for sort_spec in args:
                if isinstance(sort_spec, tuple):
                    field, direction = sort_spec
                    reverse = direction == -1
                    self.data.sort(key=lambda x: x.get(field, ''), reverse=reverse)
        return self
    
    def skip(self, count: int):
        """Skip documents"""
        return MockCursor(self.data[count:])
    
    def limit(self, count: int):
        """Limit documents"""
        return MockCursor(self.data[:count])
    
    async def to_list(self, length: Optional[int] = None):
        """Convert to list"""
        return self.data[:length] if length else self.data

class MockInsertResult:
    """Mock insert result"""
    def __init__(self, inserted_id: str):
        self.inserted_id = inserted_id

class MockUpdateResult:
    """Mock update result"""
    def __init__(self):
        self.modified_count = 1

class MockDeleteResult:
    """Mock delete result"""
    def __init__(self):
        self.deleted_count = 1
