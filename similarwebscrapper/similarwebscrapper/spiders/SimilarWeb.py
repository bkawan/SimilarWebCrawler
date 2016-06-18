# -*- coding: utf-8 -*-
import json
import scrapy
from scrapy import signals
from scrapy.http import TextResponse

from similarwebscrapper.items import SimilarwebscrapperItem
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher


class SimilarwebSpider(scrapy.Spider):
    name = "similarweb"
    allowed_domains = ["similarweb.com"]
    start_urls = [
        "https://www.similarweb.com/website/monster.com"
    ]

    def __init__(self):
        self.driver = webdriver.Chrome()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        self.driver.close()


    # Ranks = scrapy.Field()
    # Topics = scrapy.Field()
    # Engagement = scrapy.Field()
    # AlsoVisited_Websites = scrapy.Field()
    # Traffic_Sources = scrapy.Field()
    # Traffic_By_Countries = scrapy.Field()
    # Similar_Web_URL = scrapy.Field()
    # Audience_Interests = scrapy.Field()

    def parse(self, response):
        self.driver.get(response.url)
        response = TextResponse(url=response.url, body=self.driver.page_source, encoding='utf-8')
        # with open('log.txt', 'w') as f:
        #     f.write(response.body)

        item = SimilarwebscrapperItem()
        item['Domain'] = response.xpath("//span[@class='stickyHeader-nameText']/text()").extract()
        item['Description'] =response.xpath("//div[@class='analysis-descriptionText']/text()").extract()
        similar_sites = response.xpath("//ul[@class='similarSitesList similarity js-similarSitesList']/li")
        print("********")
        print(similar_sites)
        print("********")
        similar_sites_list = []
        print("******************")

        for site in similar_sites:
            site = site.xpath("div/div/span/a[1]/text()").extract()
            similar_sites_list.append(str(site[0].strip()))
            print(str(site[0].strip()))
        print("*********************")
        item['Similar_Sites'] = similar_sites_list


        traffic_source_chart = response.xpath("//ul[@class='trafficSourcesChart-list']/li")
        # 1 - Direct
        tf1_direct_name = traffic_source_chart[0].xpath("div[2]/div/span/text()").extract()
        tf1_direct_key = "Percent"
        tf1_direct_value  = traffic_source_chart[0].xpath("div[1]/div/div/text()").extract()

        # 2- Referrals
        tf2_referrals_name = traffic_source_chart[1].xpath("div[2]/div/a/text()").extract()
        tf2_referrals_key = "Percent"
        tf2_referrals_value = traffic_source_chart[1].xpath("div[1]/div/div/text()").extract()

        # 3- Serach
        tf3_search_name = traffic_source_chart[2].xpath("div[2]/div/a/text()").extract()
        tf3_search_key = "Percent"
        tf3_search_value = traffic_source_chart[2].xpath("div[1]/div/div/text()").extract()


        # 4- Social
        tf4_social_name = traffic_source_chart[3].xpath("div[2]/div/a/text()").extract()
        tf4_social_key = "Percent"
        tf4_social_value = traffic_source_chart[3].xpath("div[1]/div/div/text()").extract()

        # 5-Mail
        tf5_mail_name = traffic_source_chart[4].xpath("div[2]/div/span/text()").extract()
        tf5_mail_keys = "Percent"
        tf5_mail_value = traffic_source_chart[4].xpath("div[1]/div/div/text()").extract()


        # 3-
        tf6_display_name = traffic_source_chart[5].xpath("div[2]/div/a/text()").extract()
        tf6_display_key = "Percent"
        tf6_display_value = traffic_source_chart[5].xpath("div[1]/div/div/text()").extract()

        print("************************")

        print(tf1_direct_name,tf1_direct_value)
        print(tf2_referrals_name, tf2_referrals_value)
        print(tf3_search_name, tf3_search_value)
        print(tf4_social_name, tf4_social_value)
        print(tf5_mail_name, tf5_mail_value)
        print(tf6_display_name, tf6_display_value)

        print("************************")

        ########### Top Referring Sites: ################
        website_block_title_element = response.xpath("//h4[@class='websitePage-blocktitle']/text()").extract()


        top_referral_block_title = website_block_title_element[0]
        top_reffering_sites = []
        top_reffering_sites_element = response.xpath("//div[@class='referralsSites referring']/ul/li")

        for site in top_reffering_sites_element:
            top_reffering_sites.append(site.xpath("div/a[1]/text()").extract())

        print("******************")
        print (top_referral_block_title) ## Referring Sites
        print(top_reffering_sites)
        print("******************")
        ########### Top Referring Sites: ################

        ############## Top Destination Sites ###############
        top_destination_block_title = website_block_title_element[1]
        top_destination_sites = []
        top_destination_sites_element = response.xpath("//div[@class='referralsSites destination']/ul/li")

        for site in top_destination_sites_element:
            top_destination_sites.append(site.xpath("div/a[1]/text()").extract())

        print("****************")
        print(top_destination_block_title)
        print(top_destination_sites)
        print("****************")


        ################ Top Destination Sites ###############

        ################ Display Advertising ##################

        display_advert_block_element = response.xpath("//div[@data-waypoint='display']")

        display_main_title = display_advert_block_element.xpath("div[1]/h2[1]/text()").extract()

        display_publisher_title = display_advert_block_element.xpath("div[2]/div[2]/h3/text()").extract()

        display_publisher_sites_element = display_advert_block_element.xpath("div[2]/div[2]/div[1]")

        display_publisher_sites_list =[]

        display_publisher_sites_list.append(display_publisher_sites_element.xpath("div[1]/div/a[1]/text()").extract())
        display_publisher_sites_list.append(display_publisher_sites_element.xpath("div[2]/div/a[1]/text()").extract())
        display_publisher_sites_list.append(display_publisher_sites_element.xpath("div[3]/div/a[1]/text()").extract())
        display_publisher_sites_list.append(display_publisher_sites_element.xpath("div[4]/div/a[1]/text()").extract())
        display_publisher_sites_list.append(display_publisher_sites_element.xpath("div[5]/div/a[1]/text()").extract())

        print(display_main_title)
        print("*****************")


        print(display_publisher_title)
        print(display_publisher_sites_list)
        print("*****************")


        ##################    TOP Ad Network   ############################
        display_network_title = display_advert_block_element.xpath("div[2]/div[3]/div[1]/h3/text()").extract()



        display_network_title_elements = response.xpath("//div[@class='highcharts-data-labels']").extract()
        print("***********")
        print(display_network_title_elements)
        print("***********")


        display_network_title_list = []
        for title in display_network_title_elements:
            display_network_title.append(title.xpath("span/text()").extract())


        print(display_network_title)
        print(display_network_title_list)
        print("******************")


        ##################    TOP Ad Network   ############################



        ################ Display Advertising ##################

        ###################### Search ########################


        ###################### Search ########################


        ##################### Website Contents #######################

        social_keys = []
        social_values =[]

        tf2_social_elements = response.xpath("//ul[@class='socialList']/li")

        for social in tf2_social_elements:
            name = social.xpath("div[1]/a/text()").extract()
            value = social.xpath("div[2]/div[2]/text()").extract()
            print(name,value)

        mobile_apps = response.xpath("//ul[@class='mobileApps-appList']/li")
        mobile_apps_list = []
        for apps in mobile_apps:
            a = apps.xpath("a/span[2]/span/text()").extract()
            mobile_apps_list.append(a)

        item['Related_Mobile_Apps'] = mobile_apps_list

        yield item




