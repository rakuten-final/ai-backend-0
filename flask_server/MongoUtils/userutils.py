from pymongo import MongoClient
import os
import json
from dotenv import load_dotenv

load_dotenv()


connString = os.getenv("MONGO_STRING")
dbName = os.getenv("MONGO_DB_NAME")
colName=os.getenv("MONGO_USER_COL_NAME")

client = MongoClient(connString)
db = client[dbName]
col = db[colName]

def fetchById(id):
    user = col.find_one(id)
    return user

def insert(user):
    try:
        result = col.insert_one({
            "_id": user["user_id"],
            **user
        })
        
        print(f"Data inserted with ID: {result.inserted_id}")
    except Exception as e:
        print(f"An error occurred: {e}")