from pymongo import MongoClient
import os
import json
from dotenv import load_dotenv

load_dotenv()


connString = os.getenv("MONGO_STRING")
dbName = os.getenv("MONGO_DB_NAME")
colName=os.getenv("MONGO_COL_NAME")

client = MongoClient(connString)
db = client[dbName]
col = db[colName]

def insertData(jsonFilePtr):
    jsonData = json.load(jsonFilePtr)
    
    documents = [{'_id': id_, **data} for id_, data in jsonData.items()]
    
    
    try:
        result = col.insert_many(documents, ordered=False)  # ordered=False allows unordered bulk inserts
        print(f"Data inserted with IDs: {result.inserted_ids}")
    except Exception as e:
        print(f"An error occurred: {e}")
        
        
def fetchById(id):
    product = col.find_one(id)
    return product

def fetchAll():
    #return as a dict
    products = {}
    for product in col.find():
        products[product["_id"]] = product
    return products


def fetchPaginated(page, page_size):
    # Calculate the number of documents to skip
    skip = (page - 1) * page_size
    # Fetch paginated results
    cursor = col.find().skip(skip).limit(page_size)
    
    # Convert cursor to list of products
    products = list(cursor)
    
    return products
