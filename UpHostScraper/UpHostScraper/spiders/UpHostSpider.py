from datetime import datetime
from xmlrpc.client import ResponseError
from scrapy import Spider, Request
from UpHostScraper.utils import formatted_and_day_later
from datetime import datetime


class UpHostSpider(Spider):
    name = "UpHostSpider"
    base_url = "https://www.airbnb.com"

    def __init__(self, destination_string, checkin_date: datetime = None):
        super(UpHostSpider, self).__init__()
        self.destination_string = destination_string
        self.checkin_date = checkin_date if checkin_date else datetime.now()

    def start_requests(self):
        checkin, checkout = formatted_and_day_later(self.checkin_date)
        url = f"{self.base_url}/s/{self.destination_string}/homes?checkin={checkin}&checkout={checkout}&search_type=search_query"

        yield Request(url=url, callback=self.parse)

    def parse(self, response):
        listing_urls = response.css("a.ln2bl2p::attr(href)").getall()

        for url in listing_urls:
            yield Request(self.base_url+url, self.parse_listing_page)

        next_page = response.css("a._1bfat5l::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_listing_page(self, response):
        pass

    def _extract_title(self, response):
        pass
