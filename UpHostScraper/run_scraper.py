from datetime import datetime
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from UpHostScraper.spiders.UpHostSpider import UpHostSpider


def run():
    settings = get_project_settings()
    process = CrawlerProcess(settings=settings)

    process.crawl(UpHostSpider, destination_string="doha",
                  checkin_date=datetime(2022, 11, 24))
    process.start()


if __name__ == '__main__':
    run()
