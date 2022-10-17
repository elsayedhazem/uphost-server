import scrapy


class UpHostSpider(scrapy.spider):
    def __init__(self):
        super(UpHostSpider, self).__init__()

    def parse(self, response):
        pass
