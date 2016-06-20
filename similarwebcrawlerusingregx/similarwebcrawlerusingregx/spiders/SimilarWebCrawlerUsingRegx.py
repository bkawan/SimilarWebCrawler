# -*- coding: utf-8 -*-
import scrapy
import json
import re
from scrapy import signals
from scrapy.http import TextResponse
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from similarwebcrawlerusingregx.items import SimilarwebcrawlerusingregxItem


class SimilarwebcrawlerusingregxSpider(scrapy.Spider):
    name = "SimilarWebCrawlerUsingRegx"
    allowed_domains = ["similarweb.com"]
    start_urls = [
        "https://www.similarweb.com/website/monster.com",
        # "file:///Users/bikeshkawan/Development/phunka/GitHub/SimilarWebCrawler/similarwebcrawlerusingregx/log.html"


    ]

    def __init__(self):
        self.driver = webdriver.Chrome()
        dispatcher.connect(self.spider_closed,signals.spider_closed)

    def spider_closed(self,spider):
        self.driver.close()


    def parse(self, response):
        self.driver.get(response.url)
        response = TextResponse(url =response.url,body=self.driver.page_source,encoding = 'utf-8')

        # print(response.xpath("//html").extract())
        # converting TextResponse to String as re needs string
        stringdata = response.xpath("//html").extract()
        print("**************")
        # print(type(str(stringdata[0])))
        print("**************")

        # regular expression for finding Sw.preloadedData  variable inside script
        data_regex = re.compile(r'Sw\.preloadedData\s=\s(.*)')

        matched_data = data_regex.findall((stringdata[0].encode('ascii', 'ignore')))

        sw_preloaded_data = matched_data[0].strip(";")

        item = SimilarwebcrawlerusingregxItem()
        item['Overview'] = json.loads(sw_preloaded_data).values()[0]

        return item










