from dotenv import load_dotenv
import os
from fastapi import FastAPI
from pymongo import MongoClient

load_dotenv()

APIFY_BASE_URL = os.getenv("APIFY_BASE_URL")
APIFY_TOKEN = os.getenv('APIFY_TOKEN')

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

app = FastAPI()


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(MONGO_URI)
    app.db = app.mongodb_client[DB_NAME]


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()
