

class DestinationManager():
	def __init__(self, db, destination_id, timestamp):
		self.__collection = db["Destinations"]
		self.__doc = self.__collection.find_one({"_id":destination_id})
		listings_collection = db["Listings"]
		listing_docs = listings_collection.find({"_id": { "$in": self.__doc["listingIds"]}})
		self.timestamp = timestamp
		self.new_destination_features = None
		self.listings_features = {}
		for doc in listing_docs:
			features = doc["features"]
			most_recent_key = max(list(features.keys()))

			self.listings_features[doc["_id"]] = features[most_recent_key][0]

	@staticmethod
	def static_manage_destination(self, db, destination_id):
		manager = DestinationManager(db, destination_id)
		manager.manage_destination()

	def manage_destination(self):
		self.__extract_new_features(self)
		
		if self.new_destination_features:
			self.__collection.find_one_and_update(
				{"_id": self.__doc["id"]},
            	{'$set': {f"features.{self.timestamp}": self.new_destination_features}}
			)

	def __remove_nulls(self, dictionary):
		for k in dictionary:
			if dictionary[k] is None:
				del dictionary[k]
		
		return dictionary

	def __extract_pricing_features(self):
		prices = { listing_id: features["pricing"].get("totalAmount", None) for listing_id, features in self.listings_features.items() }

		prices = self.__remove_nulls(prices)
		prices_per_guest = {}

		for listing_id in prices:
			n_guests = self.listings_features[listing_id].get("numberOfGuests", None)
			if n_guests:
				price_per_guest = prices[listing_id] // n_guests
				prices_per_guest[listing_id] = price_per_guest

		max_price_per_guest = max(list(prices.values()))
		max_price_per_guest = { prices_per_guest.keys()[prices_per_guest.values().index(max_price_per_guest)] : max_price_per_guest }
		
		min_price_per_guest = min(list(prices.values()))
		min_price_per_guest = { prices_per_guest.keys()[prices_per_guest.values().index(min_price_per_guest)] : min_price_per_guest }

		avg_price_per_guest = sum(list(price_per_guest.values())) // len(list(prices_per_guest.values()))
		return {
			"max": min_price_per_guest,
			"min": max_price_per_guest,
			"avg": avg_price_per_guest
		}

	def __rank_listings_by_occupancy(self, occupancyPercentages):
		sorted_occupancies_tuples = sorted(occupancyPercentages.items(), key=lambda x:x[1], reverse=True)
		return dict(sorted_occupancies_tuples)

	def __extract_new_features(self):

		self.new_destination_features["avgOccupancy"] = sum(list(occupancyPercentages)) // len(list(occupancyPercentages))
		
		pricing_features = self.__extract_pricing_features()
		self.new_destination_features["maxPrice"] = pricing_features["max"]
		self.new_destination_features["minPrice"] = pricing_features["min"]
		self.new_destination_features["avgPrice"] = pricing_features["avg"]

		occupancyPercentages = { listing_id: features["occupancyPercentage"] for listing_id, features in self.listings_features.items() }
		self.new_destination_features["listingsByDescendingOccupancy"] = list(self.__rank_listings_by_occupancy(occupancyPercentages).keys())
