# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SimilarwebscrapperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    Domain = scrapy.Field()
    Description = scrapy.Field()
    Similar_Sites = scrapy.Field()
    Ranks = scrapy.Field()
    Topics = scrapy.Field()
    Engagement = scrapy.Field()
    AlsoVisited_Websites = scrapy.Field()
    Traffic_Sources = scrapy.Field()
    Traffic_By_Countries = scrapy.Field()
    Similar_Web_URL = scrapy.Field()
    Audience_Interests = scrapy.Field()
    Related_Mobile_Apps = scrapy.Field()













