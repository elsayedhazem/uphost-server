from datetime import datetime
from scrapy import Spider, Request
from UpHostScraper.utils import formatted_and_day_later
from datetime import datetime


class UpHostSpider(Spider):
    name = "UpHostSpider"

    def __init__(self, destination_string, checkin_date: datetime = None):
        super(UpHostSpider, self).__init__()
        self.destination_string = destination_string
        self.checkin_date = checkin_date if checkin_date else datetime.now()

    def start_requests(self):
        checkin, checkout = formatted_and_day_later(self.checkin_date)
        url = f"https://www.airbnb.com/s/{self.destination_string}/homes?tab_id=all_tab&refinement_paths%5B%5D=%2Fhomes&source=structured_search_input_header&checkin={checkin}&checkout={checkout}&search_type=search_query"

        yield Request(url=url, callback=self.parse)

    def parse(self, response):
        pass

    def _extract_title(self, response):
        pass
