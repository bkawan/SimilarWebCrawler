# -*- coding: utf-8 -*-
import json
import scrapy
from scrapy import signals
from scrapy.http import TextResponse

from similarwebscrapper.items import SimilarwebscrapperItem
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher

import re

class SimilarwebSpider(scrapy.Spider):
    name = "similarweb"
    allowed_domains = ["similarweb.com"]
    start_urls = [
        # "https://www.similarweb.com/website/monster.com"
        "file:///Users/BIKESHKAWAN/Development/phunka/GitHub/SimilarWebCrawler/similarwebscrapper/log.html"

    ]

    def __init__(self):
        self.driver = webdriver.Chrome()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        self.driver.close()


    def parse(self, response):
        # self.driver.get(response.url)
        # response = TextResponse(url=response.url, body=self.driver.page_source, encoding='utf-8')
        print response
        # with open('log.html', 'w') as f:
        #     f.write(response.body)

        item = SimilarwebscrapperItem()
        item['Domain'] = response.xpath("//span[@class='stickyHeader-nameText']/text()").extract()
        item['Description'] =response.xpath("//div[@class='analysis-descriptionText']/text()").extract()
        similar_sites_elements = response.xpath("//section[@class='similarSitesSection']/ul/li")
        similar_sites_list = []
        for site in similar_sites_elements:
            site = site.xpath("div/div/span/a[1]/text()").extract()
            similar_sites_list.append(str(site[0].strip()))
            print(str(site[0].strip()))
        print("********* Similar Sites ************")
        item['Similar_Sites'] = similar_sites_list
        print(similar_sites_list)

        ########### Rank    #################


        ranking_items_elements = response.xpath("//div[@class='rankingItems']")

        global_rank_value = ranking_items_elements.xpath("div[1]/div/div[2]/span/text()").extract()

        country_rank_country_name = ranking_items_elements.xpath("div[2]/div/div[1]/a/text()").extract()

        country_rank_country_value = ranking_items_elements.xpath("div[2]/div/div[2]/span/text()").extract()

        category_rank_name = ranking_items_elements.xpath("div[3]/div/div[1]/a[1]/text()").extract()
        category_rank_value = ranking_items_elements.xpath("div[3]/div/div[2]/span/text()").extract()

        category_main_category = str(category_rank_name[0]).split(">")[0]
        category_sub_category = str(category_rank_name[0]).split(">")[1]

        print("**** Ranks *******")
        print (global_rank_value, country_rank_country_name, country_rank_country_value,
               category_main_category, category_sub_category, category_rank_value)

        # ** ** Ranks ** ** ** *
        # ([u'1,359'], [u'United States'], [u'300'], 'Career and Education ', ' Jobs and Employment', [u'8'])

        rank_key = "Ranks"
        # rank_value1 = dict(zip)




        traffic_source_chart_elements = response.xpath("//ul[@class='trafficSourcesChart-list']/li")
        # 1 - Direct
        tf1_direct_name = traffic_source_chart_elements[0].xpath("div[2]/div/span/text()").extract()
        tf1_direct_key = "Percent"
        tf1_direct_value  = traffic_source_chart_elements[0].xpath("div[1]/div/div/text()").extract()

        # 2- Referrals
        tf2_referrals_name = traffic_source_chart_elements[1].xpath("div[2]/div/a/text()").extract()
        tf2_referrals_key = "Percent"
        tf2_referrals_value = traffic_source_chart_elements[1].xpath("div[1]/div/div/text()").extract()

        # 3- Serach
        tf3_search_name = traffic_source_chart_elements[2].xpath("div[2]/div/a/text()").extract()
        tf3_search_key = "Percent"
        tf3_search_value = traffic_source_chart_elements[2].xpath("div[1]/div/div/text()").extract()


        # 4- Social
        tf4_social_name = traffic_source_chart_elements[3].xpath("div[2]/div/a/text()").extract()
        tf4_social_key = "Percent"
        tf4_social_value = traffic_source_chart_elements[3].xpath("div[1]/div/div/text()").extract()

        # 5-Mail
        tf5_mail_name = traffic_source_chart_elements[4].xpath("div[2]/div/span/text()").extract()
        tf5_mail_keys = "Percent"
        tf5_mail_value = traffic_source_chart_elements[4].xpath("div[1]/div/div/text()").extract()


        # 3-
        tf6_display_name = traffic_source_chart_elements[5].xpath("div[2]/div/a/text()").extract()
        tf6_display_key = "Percent"
        tf6_display_value = traffic_source_chart_elements[5].xpath("div[1]/div/div/text()").extract()

        print("************************")

        print(tf1_direct_name,tf1_direct_value)
        print(tf2_referrals_name, tf2_referrals_value)
        print(tf3_search_name, tf3_search_value)
        print(tf4_social_name, tf4_social_value)
        print(tf5_mail_name, tf5_mail_value)
        print(tf6_display_name, tf6_display_value)

        print("*********** Top Refering sites *************")

        refferals_elements = response.xpath("//div[@data-waypoint='referrals']")

        ########### Top Referring Sites: ################
        website_block_title_element = response.xpath("//h4[@class='websitePage-blocktitle']/text()").extract()


        top_referral_block_title = website_block_title_element[0]
        top_reffering_sites = []
        top_refering_sites_total = refferals_elements.xpath("div[2]/section/div[1]/div[3]/button/text()").extract()
        top_refering_sites_total = self.number_only(top_refering_sites_total[0])
        top_reffering_sites_element = response.xpath("//div[@class='referralsSites referring']/ul/li")

        for site in top_reffering_sites_element:
            top_reffering_sites.append(site.xpath("div/a[1]/text()").extract())

        print("******************")
        print (top_referral_block_title) ## Referring Sites
        print(top_reffering_sites)
        print(top_refering_sites_total)
        print("******* Top Destionation sites***********")
        ########### Top Referring Sites: ################

        ############## Top Destination Sites ###############
        top_destination_block_title = website_block_title_element[1]
        top_destination_sites = []
        top_destination_sites_total = refferals_elements.xpath("div[2]/section/div[3]/div[3]/button/text()").extract()
        top_destination_sites_total = self.number_only(top_destination_sites_total[0])
        top_destination_sites_element = response.xpath("//div[@class='referralsSites destination']/ul/li")

        for site in top_destination_sites_element:
            top_destination_sites.append(site.xpath("div/a[1]/text()").extract())

        print("****************")
        print(top_destination_block_title)
        print(top_destination_sites)
        print(top_destination_sites_total)
        print("****************")


        ################ Top Destination Sites ###############

        ################ Display Advertising ##################
        "/html/body/div[3]/div/div/div[8]"
        "/html/body/div[3]/div/div/div[8]/div[2]/div[2]/div[2]/button"

        display_advert_block_element = response.xpath("//div[@data-waypoint='display']")

        display_main_title = display_advert_block_element.xpath("div[1]/h2[1]/text()").extract()

        display_publisher_title = display_advert_block_element.xpath("div[2]/div[2]/h3/text()").extract()

        display_publisher_sites_element = display_advert_block_element.xpath("div[2]/div[2]/div[1]")

        display_publisher_sites_list =[]
        display_publisher_total = display_advert_block_element.xpath("div[2]/div[2]/div[2]/button/text()").extract()
        display_publisher_total = self.number_only(display_publisher_total[0])

        display_publisher_sites_list.append(display_publisher_sites_element.xpath("div[1]/div/a[1]/text()").extract())
        display_publisher_sites_list.append(display_publisher_sites_element.xpath("div[2]/div/a[1]/text()").extract())
        display_publisher_sites_list.append(display_publisher_sites_element.xpath("div[3]/div/a[1]/text()").extract())
        display_publisher_sites_list.append(display_publisher_sites_element.xpath("div[4]/div/a[1]/text()").extract())
        display_publisher_sites_list.append(display_publisher_sites_element.xpath("div[5]/div/a[1]/text()").extract())

        print(display_main_title)
        print("*****************")


        print(display_publisher_title)
        print(display_publisher_sites_list)
        print(display_publisher_total)
        print("*****************")


        ##################    TOP Ad Network   ############################
        display_network_title = display_advert_block_element.xpath("div[2]/div[3]/div[1]/h3/text()").extract()
        ##
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

        search_pie= response.xpath("//div[@class='searchPie']")

        tf3_search_type1_key = search_pie.xpath("div[1]/span[2]/text()").extract()
        tf3_search_type1_value = search_pie.xpath("div[1]/span[1]/text()").extract()

        tf3_search_type2_key = search_pie.xpath("div[3]/span[2]/text()").extract()
        tf3_search_type2_value = search_pie.xpath("div[3]/span[1]/text()").extract()

        print(tf3_search_type1_key,tf3_search_type1_value)
        print(tf3_search_type2_key,tf3_search_type2_value)


        search_keywords = response.xpath("//div[@class='searchKeywords']")


        search_keywords_type1_key = search_keywords.xpath("div[1]/div[1]/h4/text()").extract()

        search_keywords_type1_elements = search_keywords.xpath("div[1]/ul/li")

        search_keywords_type1_value = []
        search_keywords_type1_total = search_keywords.xpath("div[1]/div[2]/button/text()").extract()
        search_keywords_type1_total = self.number_only(search_keywords_type1_total[0])

        for keyword in search_keywords_type1_elements:
            search_keywords_type1_value.append(keyword.xpath("span[2]/span/text()").extract())

        search_keywords_type2_key = search_keywords.xpath("div[2]/div[1]/h4/text()").extract()

        search_keywords_type2_elements = search_keywords.xpath("div[2]/ul/li")

        search_keywords_type2_value = []
        search_keywords_type2_total = search_keywords.xpath("div[2]/div[2]/button/text()").extract()
        search_keywords_type2_total = self.number_only(search_keywords_type2_total[0])

        for keyword in search_keywords_type2_elements:
            search_keywords_type2_value.append(keyword.xpath("span[2]/span/text()").extract())

        print(search_keywords_type1_key,search_keywords_type1_value)
        print(search_keywords_type2_key,search_keywords_type2_value)
        print(search_keywords_type1_total,search_keywords_type2_total)

        ###################### Search ########################
        ######### Social #############################

        social_keys = []
        social_values =[]

        tf2_social_elements = response.xpath("//ul[@class='socialList']/li")

        for social in tf2_social_elements:
            name = social.xpath("div[1]/a/text()").extract()
            value = social.xpath("div[2]/div[2]/text()").extract()
            social_keys.append(name)
            social_values.append(value)

        print(social_keys,social_values)

        ######### Social #############################

        date= "/html/body/div[3]/div/div/div[4]/div[2]/div[1]/div[1]/div/div[2]/div[1]/div/svg/g[8]/text/tspan[1]/text()"
        visits = "/html/body/div[3]/div/div/div[4]/div[2]/div[1]/div[1]/div/div[2]/div[1]/div/svg/g[8]/text/tspan[3]/text()"
        overview_elements = response.xpath("//div[@data-waypoint='overview']")

        date = response.xpath(date).extract()
        visits = response.xpath(visits).extract()
        print(">>>>>>>>>>>>>>>>>>>")

        print(date,visits)
        print(">>>>>>>>>>>>>>>>>>>")



        overview1_engagement_title = overview_elements.xpath("div[2]/div[2]/h3/text()").extract()

        overview1_engagement_keys = []
        overview1_engagement_values = []

        for engagement in overview_elements.xpath("div[2]/div[2]/div/div"):
            overview1_engagement_keys.append(engagement.xpath("div/span[1]/text()").extract())
            overview1_engagement_values.append(engagement.xpath("div/span[2]/text()").extract())

        print (overview1_engagement_keys,overview1_engagement_values)
        print("*******************")

        "/html/body/div[3]/div/div/div[4]/div[3]/div[2]/div[2]/article/div/div"
        "/html/body/div[3]/div/div/div[4]/div[3]/div[2]/div[2]/article/div/div/div[6]/button"
        traffic_countries_keys= []
        traffic_countries_values =[]
        traffic_countries_total =""
        country = dict()

        for countries in response.xpath("//div[@id='geo-countries-accordion']/div"):
            traffic_countries_keys.append(countries.xpath("div/span/a/text()").extract())
            traffic_countries_values.append(countries.xpath("div/span/span/text()").extract())
            traffic_countries_total = countries.xpath("button/text()").extract()
        traffic_countries_total = self.number_only(traffic_countries_total[0])
        print("Total",traffic_countries_total)


        for countries in response.xpath("//div[@id='geo-countries-accordion']/div"):
            country[countries.xpath("div/span/a/text()").extract_first()] =countries.xpath("div/span/span/text()").extract_first()

        dict1 = dict()
        print("________")
        dict1['country'] = country
        print (dict1)
        print("________")


        ############## Website content #############

        website_content_elements = response.xpath("//section[@data-waypoint='websiteContent']/div[4]")

        website_content_subdomains = "Subdomains"
        website_content_subdomain_value = website_content_elements.xpath("div[2]/div[4]/span[1]/text()").extract()

        website_subdomain_names = []
        website_subdomain_share_values = []
        for subdomain in website_content_elements.xpath("div[2]/div[5]/div"):
            website_subdomain_names.append(subdomain.xpath("span[1]/span/span/text()").extract())
            website_subdomain_share_values.append(subdomain.xpath("span[2]/span[2]/text()").extract())

        print("&&&&&&&&&&&&&&&&")
        print(website_content_subdomains,website_content_subdomain_value,website_subdomain_names,website_subdomain_share_values)

        website_content_folders = "Folders"
        website_content_folders_value = website_content_elements.xpath("div[3]/div[4]/span[1]/text()").extract()

        website_folder_names = []
        website_folder_share_values = []
        for folder in website_content_elements.xpath("div[3]/div[5]/div"):
            website_folder_names.append(folder.xpath("span[1]/span[2]/span/text()").extract())
            website_folder_share_values.append(folder.xpath("span[2]/span[2]/text()").extract())

        print ("********************")
        print(website_content_folders,website_content_folders_value,website_folder_names, website_folder_share_values)



        ########### Audience Interests #########

        aud_interests_elements = response.xpath("//div[@data-waypoint='alsoVisited']")
        categories = response.xpath("//a[@class='audienceCategories-itemLink']/text()").extract()

        main_category = str(categories[0]).split(">")[0]
        sub_category = str(categories[0]).split(">")[1]

        also_visited_webistes_element = aud_interests_elements.xpath("div[2]/section[2]/div[1]/div")
        also_visited_webistes_list = []
        also_visited_websites_total = aud_interests_elements.xpath("div[2]/section[2]/div[2]/button/text()").extract()
        also_visited_websites_total = self.number_only(also_visited_websites_total[0])
        for website in also_visited_webistes_element:
            also_visited_webistes_list.append(website.xpath("div/a[1]/text()").extract())

        topic_list = []
        for topic in response.xpath("//ul[@class='topics-list js-cloudContainer']/li/text()").extract():
            topic_list.append(topic)
        print("*********")
        print(main_category,sub_category,also_visited_webistes_list,topic_list,also_visited_websites_total)
        print("**********")



        print("***********")




        #########  Mobile Apps #############################

        print("****** Mobile Apps *************")
        mobile_apps = response.xpath("//ul[@class='mobileApps-appList']/li")
        mobile_apps_list = []
        mobile_apps_href = []
        for apps in mobile_apps:
            a = apps.xpath("a/span[2]/span/text()").extract()
            href = apps.xpath("a/@href").extract()
            mobile_apps_list.append(a)
            mobile_apps_href.append(response.urljoin(href[0]))

        item['Related_Mobile_Apps'] = mobile_apps_list
        print (mobile_apps_list,mobile_apps_href)

        #########  Mobile Apps #############################



        yield item


    def number_only(self,string):
        return re.sub("\D", "", string)




