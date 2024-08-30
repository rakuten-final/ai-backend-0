from typing import Annotated
from typing_extensions import TypedDict
from typing import TypedDict, Literal, List, Union
import requests

import langgraph
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage,ToolMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.sqlite import SqliteSaver

import json
from IPython.display import Image, display
import flask
from flask_cors import CORS
from flask import request, jsonify
import os
from dotenv import load_dotenv

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from tqdm import tqdm

from collections import defaultdict
from datetime import datetime


load_dotenv("../.env")


def get_stored_result(path:str, type:Literal["json","csv"]):
    # Check if the path is valid
    if not os.path.exists(path):
        return None 
    if type == "json":
        with open(path, 'r') as f:
            data = json.load(f)
        return data
    elif type == "csv":
        with open(path, 'r') as f:
            data = json.load(f)
        return data
    else:
        return None 
    
def save_result(result, path:str, type:Literal["json","csv"]):
    if type == "json":
        with open(path, 'w') as f:
            json.dump(result, f, indent=4)
    elif type == "csv":
        #  check if the result is a dataframe
        if isinstance(result, pd.DataFrame):
            result.to_csv(path, index=False)
        else:
            print("The result is not a dataframe")
            raise ValueError("The result is not a dataframe")
    else:
        print("Invalid type")
        raise ValueError("Invalid type")

def get_category_wise_vector_store():
    client = QdrantClient(url=os.getenv("QDRANT_URL"),api_key=os.getenv("QDRANT_API_KEY"))
    collections_dict = client.get_collections().dict()
    all_collections = [collection['name'] for collection in collections_dict['collections']]
    category_wise_vector_store = {}
    for category in tqdm(all_collections):
        category_wise_vector_store[category] = QdrantVectorStore(
            client=client,
            collection_name=category,
            embedding=OpenAIEmbeddings(model="text-embedding-3-large"),
        )
    return category_wise_vector_store

CATEGORY_WISE_VECTOR_STORE = get_category_wise_vector_store()