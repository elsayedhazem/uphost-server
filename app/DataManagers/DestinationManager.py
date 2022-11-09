from bson import ObjectId


class DestinationManager():
    def __init__(self, db, destination_id, timestamp):
        self.__collection = db["Destinations"]
        self.__doc = self.__collection.find_one(
            {"_id": ObjectId(destination_id)})
        listings_collection = db["Listings"]
        listing_ids = self.__doc["listingIds"]
        listing_docs = listings_collection.find({"_id": {"$in": listing_ids}})
        self.timestamp = timestamp
        self.new_destination_features = {}
        self.listings_features = {}
        for doc in listing_docs:
            features = doc.get("features", None)
            if features:
                most_recent_key = max(list(features.keys()))

                self.listings_features[doc["_id"]
                                       ] = features[most_recent_key]['0']

    @staticmethod
    def static_manage_destination(db, destination_id, timestamp):
        manager = DestinationManager(db, destination_id, timestamp)
        manager.manage_destination()

    def manage_destination(self):
        self.__extract_new_features()

        if self.new_destination_features:
            self.__collection.find_one_and_update(
                {"_id": self.__doc["_id"]},
                {'$set': {f"features.{self.timestamp}": self.new_destination_features}}
            )

    def __remove_nulls(self, dictionary):
        copy = {}
        for k in dictionary:
            if dictionary[k]:
                copy[k] = dictionary[k]

        return copy

    def __extract_pricing_features(self):
        prices = {listing_id: features.get("pricing", {}).get("totalPrice", {}).get(
            "amount", None) for listing_id, features in self.listings_features.items()}

        prices = self.__remove_nulls(prices)
        prices_per_guest = {}

        for listing_id in prices:
            n_guests = self.listings_features[listing_id].get(
                "numberOfGuests", None)
            if n_guests:
                price_per_guest = prices[listing_id] // n_guests
                prices_per_guest[listing_id] = price_per_guest

        max_price_per_guest = max(list(prices_per_guest.values()))
        max_price_per_guest = {list(prices_per_guest.keys())[list(
            prices_per_guest.values()).index(max_price_per_guest)]: max_price_per_guest}

        min_price_per_guest = min(list(prices_per_guest.values()))
        min_price_per_guest = {list(prices_per_guest.keys())[list(
            prices_per_guest.values()).index(min_price_per_guest)]: min_price_per_guest}

        avg_price_per_guest = sum(
            list(prices_per_guest.values())) // len(list(prices_per_guest.values()))
        return {
            "max": max_price_per_guest,
            "min": min_price_per_guest,
            "avg": avg_price_per_guest
        }

    def __rank_listings_by_occupancy(self, occupancyPercentages):
        sorted_occupancies_tuples = sorted(
            occupancyPercentages.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_occupancies_tuples)

    def __extract_booking_rates(self, occupancyPercentages):
        nonzero_occupancies = {k: v for k,
                               v in occupancyPercentages.items() if v}

        number_of_bookings_at_dates = {}

        for listing_id in nonzero_occupancies:
            calendar = self.listings_features[listing_id]["calendar"]
            if len(calendar) > 0:
                for date in calendar:
                    if date["available"]:
                        if not number_of_bookings_at_dates.get(date["date"], None):
                            number_of_bookings_at_dates[date["date"]] = 0
                        number_of_bookings_at_dates[date["date"]] += 1

        n_listings = len(list(self.listings_features.keys()))
        current_booking_percentages = {
            k: v / n_listings for k, v in number_of_bookings_at_dates.items()}

        return current_booking_percentages

    def __extract_new_features(self):
        occupancyPercentages = {listing_id: features.get(
            "occupancyPercentage", 0) for listing_id, features in self.listings_features.items()}
        self.new_destination_features["listingsByDescendingOccupancy"] = list(
            self.__rank_listings_by_occupancy(occupancyPercentages).keys())
        self.new_destination_features["bookingRates"] = self.__extract_booking_rates(
            occupancyPercentages)
        self.new_destination_features["avgOccupancy"] = sum(
            list(occupancyPercentages.values())) // len(list(occupancyPercentages.values()))

        pricing_features = self.__extract_pricing_features()
        self.new_destination_features["maxPrice"] = pricing_features["max"]
        self.new_destination_features["minPrice"] = pricing_features["min"]
        self.new_destination_features["avgPrice"] = pricing_features["avg"]
