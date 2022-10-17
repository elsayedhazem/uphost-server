# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ListingScrape(scrapy.Item):
    """Results of scraping a listing at a timestamp"""
    # Numeric Types
    timestamp = scrapy.Field()
    price = scrapy.Field()
    rating = scrapy.Field()
    guests = scrapy.Field()
    bedrooms = scrapy.Field()
    beds = scrapy.Field()
    baths = scrapy.Field()
    minimum_stay = scrapy.Field()  # defaults to 1
    current_price_per_night = scrapy.Field()

    # Lists
    months_ahead_unavailable_dates = scrapy.Field()  # 6 months ahead
    months_ahead_price_per_night = scrapy.Field()  # 6 months ahead

    # Strings
    destination = scrapy.Field()
    title = scrapy.Field()
    features = scrapy.Field()
    link = scrapy.Field()
    cancellation_policy = scrapy.Field()

    # Bools
    superhost = scrapy.Field()
