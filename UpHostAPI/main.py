from datetime import datetime
from fastapi import Request, BackgroundTasks
from config import app, APIFY_BASE_URL, APIFY_TOKEN
from Models import ScrapeParamsModel
from ScrapeManager import ScrapeManager
import requests
import os


APIFY_BASE_URL = "https://api.apify.com/v2"

APIFY_TOKEN = os.environ.get('APIFY_TOKEN')

scrape_check_in = None
scrape_check_out = None


@app.post("/scrape")
async def run_scrape(scrape_params: ScrapeParamsModel):
    scrape_params_dict = scrape_params.dict()
    scrape_params_dict["proxyConfiguration"] = {
        "useApifyProxy": True
    }
    params = {
        "token": APIFY_TOKEN
    }
    apify_actor_url = f"{APIFY_BASE_URL}/acts/dtrungtin~airbnb-scraper/runs"
    response = requests.post(
        apify_actor_url, json=scrape_params_dict, params=params).json()

    run_id = response['data']['id']
    scrape_check_in = scrape_params_dict['checkIn']
    scrape_check_out = scrape_params_dict['checkOut']

    return {
        "runId": run_id
    }


@app.get("/scrape/{run_id}")
async def check_scrape(request: Request, run_id, background_tasks: BackgroundTasks):
    apify_run_url = f"{APIFY_BASE_URL}/actor-runs/{run_id}"
    params = {
        'token': APIFY_TOKEN,
    }

    response = requests.get(
        url=apify_run_url, params=params).json()

    status = response["data"]["status"]
    finished_at = response["data"].get("finishedAt", None)

    if finished_at:
        finished_at = finished_at.split("T")[0]

    dataset_id = response['data']['defaultDatasetId']

    payload = {
        "status": status,
        "defaultDatasetId": dataset_id
    }

    if status == "FINISHED" or status == "SUCCEEDED":
        background_tasks.add_task(ScrapeManager.static_manage_scrape,
                                  request.app.db, run_id, dataset_id, finished_at)

    return payload
