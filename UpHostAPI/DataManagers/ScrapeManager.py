import requests
from datetime import datetime
from .DestinationManager import DestinationManager
from config import APIFY_BASE_URL, APIFY_TOKEN


class ScrapeManager():
    def __init__(self, db, run_id, dataset_id, finished_at):
        self.__db = db
        self.run_id = run_id
        self.dataset_id = dataset_id
        self.finished_at = datetime.strptime(
            finished_at, "%Y-%m-%d").timestamp()
        self.data = None
        self.destination_id = None

    @staticmethod
    def static_manage_scrape(db, run_id, dataset_id, finished_at):
        manager = ScrapeManager(db, run_id, dataset_id, finished_at)
        manager.manage_scrape()

    def manage_scrape(self):
        self.__fetch_scrape()
        self.__store_scrape()
        for listing in self.data:
            self.__process_listing(listing)

        DestinationManager.static_manage_destination(self.__db, self.destination_id, self.finished_at)

    def __fetch_scrape(self):
        apify_dataset_url = f"{APIFY_BASE_URL}/datasets/{self.dataset_id}/items"
        params = {
            "token": APIFY_TOKEN,
            'format': "json",
            'clean': 1,
        }

        self.data = requests.get(apify_dataset_url, params=params).json()

    def __store_scrape(self):
        scrapes_collection = self.__db["Scrapes"]
        if scrapes_collection.find_one({"_id": self.run_id}):
            return
        scrape = {
            "_id": self.run_id,
            "timestamp": self.finished_at,
            "data": self.data
        }

        scrapes_collection.insert_one(scrape)

    def __store_new_destination(self, destination_str):
        destination_doc = {
            "destinationStr": destination_str,
            "listingIds": [],
            "features": {},
            "lastScraped": self.finished_at,
        }

        destinations_collection = self.__db["Destinations"]
        return destinations_collection.insert_one(destination_doc).inserted_id

    def __store_new_listing(self, listing):
        listing_id = listing["idStr"]
        listing_doc = {
            "_id": listing_id,
            "hostId": str(listing["primaryHost"]["id"]),
        }

        destinations_collection = self.__db["Destinations"]
        destination_str = listing['countryCode']
        destination = destinations_collection.find_one(
            {"destinationStr": destination_str})

        dest_id = destination["_id"] if destination else self.__store_new_destination(
            destination_str)
        listing_doc["destinationId"] = dest_id

        self.__db["Destinations"].find_one_and_update(
            {'_id': dest_id}, {'$push': {'listingIds': listing_id}})

        listing_doc["features"] = {}
        return self.__db["Listings"].insert_one(listing_doc).inserted_id

    def __extract_listing_features(self, listing):
        listing_features = {}

        calendar = listing.get("calendar", None)
        if calendar:
            listing_features["pricing"] = {
                "checkIn": calendar[0]["date"],
                "checkOut": calendar[1]["date"],
                "totalPrice": listing["pricing"]["totalPrice"]
            }
        else:
            listing_features["pricing"] = None
        
        amenities = listing.get("listingAmenities", None)
        if amenities:
            amenities = [a["name"] for a in amenities]

        listing_features["amenities"] = amenities

        same_as_scraped_features = ["numberOfGuests", "name", "roomType", "calendar", "location", "isNew", "stars", "occupancyPercentage",
                                    "guestControls", "isHostedBySuperHost", "bathroomLabel", "bedLabel", "bedroomLabel", "minNights", "maxNights"]

        for feature in same_as_scraped_features:
            value = listing.get(feature, None)
            if not value:
                listing_features[feature] = None

            listing_features[feature] = value

        listing_features["hostTotalListingsCount"]: listing["primaryHost"].get(
            "totalListingsCount", 1)

        return listing_features

    def __process_listing(self, listing):

        if not self.__db["Listings"].find_one({"_id": listing["idStr"]}):
            self.__store_new_listing(listing)
        
        if not self.destination_id:
            self.destination_id = self.__db["Listings"].find_one({"_id": listing["idStr"]})["destinationId"]

        listing_features = self.__extract_listing_features(listing)
        timestamp = self.finished_at
        
        if listing_features["pricing"]:
            self.__db["Listings"].find_one_and_update(
                {"_id": listing["idStr"]},
                {'$set': {f"features.{timestamp}": listing_features}}
            )
