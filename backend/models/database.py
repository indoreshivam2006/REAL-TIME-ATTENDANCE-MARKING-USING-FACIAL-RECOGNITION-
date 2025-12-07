import json
import os
from datetime import datetime
from pymongo import MongoClient
from config import Config

class Database:
    """Database abstraction layer with MongoDB and JSON fallback"""
    
    def __init__(self):
        self.use_mongodb = False
        self.db = None
        self.json_storage = Config.JSON_STORAGE_PATH
        
        # Always use JSON fallback for now (MongoDB is optional)
        print("ℹ️  Using JSON file storage")
        self._init_json_storage()
    
    def _init_json_storage(self):
        """Initialize JSON storage files"""
        collections = ['teachers', 'students', 'sessions', 'attendance']
        for collection in collections:
            filepath = os.path.join(self.json_storage, f'{collection}.json')
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    json.dump([], f)
    
    def _read_json(self, collection):
        """Read data from JSON file"""
        filepath = os.path.join(self.json_storage, f'{collection}.json')
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _write_json(self, collection, data):
        """Write data to JSON file"""
        filepath = os.path.join(self.json_storage, f'{collection}.json')
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def insert_one(self, collection, document):
        """Insert a single document"""
        if self.use_mongodb:
            result = self.db[collection].insert_one(document)
            document['_id'] = str(result.inserted_id)
            return document
        else:
            data = self._read_json(collection)
            # Generate simple ID
            document['_id'] = str(len(data) + 1)
            document['createdAt'] = datetime.now().isoformat()
            data.append(document)
            self._write_json(collection, data)
            return document
    
    def find_one(self, collection, query):
        """Find a single document"""
        if self.use_mongodb:
            result = self.db[collection].find_one(query)
            if result and '_id' in result:
                result['_id'] = str(result['_id'])
            return result
        else:
            data = self._read_json(collection)
            for doc in data:
                match = all(doc.get(k) == v for k, v in query.items())
                if match:
                    return doc
            return None
    
    def find(self, collection, query=None):
        """Find multiple documents"""
        if query is None:
            query = {}
            
        if self.use_mongodb:
            results = list(self.db[collection].find(query))
            for result in results:
                if '_id' in result:
                    result['_id'] = str(result['_id'])
            return results
        else:
            data = self._read_json(collection)
            if not query:
                return data
            
            results = []
            for doc in data:
                match = all(doc.get(k) == v for k, v in query.items())
                if match:
                    results.append(doc)
            return results
    
    def update_one(self, collection, query, update):
        """Update a single document"""
        if self.use_mongodb:
            self.db[collection].update_one(query, {'$set': update})
            return True
        else:
            data = self._read_json(collection)
            for doc in data:
                match = all(doc.get(k) == v for k, v in query.items())
                if match:
                    doc.update(update)
                    doc['updatedAt'] = datetime.now().isoformat()
                    self._write_json(collection, data)
                    return True
            return False
    
    def delete_one(self, collection, query):
        """Delete a single document"""
        if self.use_mongodb:
            result = self.db[collection].delete_one(query)
            return result.deleted_count > 0
        else:
            data = self._read_json(collection)
            original_length = len(data)
            data = [doc for doc in data if not all(doc.get(k) == v for k, v in query.items())]
            if len(data) < original_length:
                self._write_json(collection, data)
                return True
            return False
    
    def delete_many(self, collection, query):
        """Delete multiple documents"""
        if self.use_mongodb:
            result = self.db[collection].delete_many(query)
            return result.deleted_count
        else:
            data = self._read_json(collection)
            original_length = len(data)
            data = [doc for doc in data if not all(doc.get(k) == v for k, v in query.items())]
            deleted_count = original_length - len(data)
            if deleted_count > 0:
                self._write_json(collection, data)
            return deleted_count
    
    def count_documents(self, collection, query=None):
        """Count documents matching query"""
        if query is None:
            query = {}
            
        if self.use_mongodb:
            return self.db[collection].count_documents(query)
        else:
            data = self._read_json(collection)
            if not query:
                return len(data)
            
            count = 0
            for doc in data:
                match = all(doc.get(k) == v for k, v in query.items())
                if match:
                    count += 1
            return count

# Global database instance
db = Database()
