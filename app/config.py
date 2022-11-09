import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pymongo import MongoClient

APIFY_BASE_URL = os.environ.get("APIFY_BASE_URL")
APIFY_TOKEN = os.environ.get('APIFY_TOKEN')

MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = os.environ.get("DB_NAME")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(MONGO_URI)
    app.db = app.mongodb_client[str(DB_NAME)]


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()
