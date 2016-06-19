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
        "https://www.similarweb.com/website/monster.com"
        # "file:///Users/BIKESHKAWAN/Development/phunka/GitHub/SimilarWebCrawler/similarwebscrapper/log.html"

    ]

    def __init__(self):
        self.driver = webdriver.Chrome()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        self.driver.close()

    def parse(self, response):
        self.driver.get(response.url)
        response = TextResponse(url=response.url, body=self.driver.page_source, encoding='utf-8')
        # print responsel', 'w') as f:
        # #     f.write(response.body)
        # # with open('log.htm


        item = SimilarwebscrapperItem()
        item['Domain'] = str(response.xpath("//span[@class='stickyHeader-nameText']/text()").extract_first())
        item['Description'] = str(response.xpath("//div[@class='analysis-descriptionText']/text()").extract_first())
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
        print("******************* Ranks ************************")


        ranking_items_elements = response.xpath("//div[@class='rankingItems']")
        global_rank_value = ranking_items_elements.xpath("div[1]/div/div[2]/span/text()").extract()
        country_rank_country_name = ranking_items_elements.xpath("div[2]/div/div[1]/a/text()").extract()
        country_rank_country_value = ranking_items_elements.xpath("div[2]/div/div[2]/span/text()").extract()
        category_rank_name = ranking_items_elements.xpath("div[3]/div/div[1]/a[1]/text()").extract()
        category_rank_value = ranking_items_elements.xpath("div[3]/div/div[2]/span/text()").extract()
        category_main_category = str(category_rank_name[0]).split(">")[0]
        category_sub_category = str(category_rank_name[0]).split(">")[1]

        rank_value_keys = ['Global_Rank', 'Country_Rank', 'Category_Rank']
        rank_value_values = [
            {'Rank': str(global_rank_value[0])},
            {'Country': str(country_rank_country_name[0]), 'Rank': str(country_rank_country_value[0])},
            {'Main_Category': category_main_category,
             'Sub_Category': category_sub_category,
             'Rank': str(category_rank_value[0])
             },
        ]
        rank_value = dict(zip(rank_value_keys, rank_value_values))
        item['Ranks'] = rank_value
        print(item['Ranks'])

        ########### Audience Interests and Topics #########

        print("******************* Audience Interests and Topics ************************")

        aud_interests_elements = response.xpath("//div[@data-waypoint='alsoVisited']")
        categories = response.xpath("//a[@class='audienceCategories-itemLink']/text()").extract()
        main_category = str(categories[0]).split(">")[0]
        sub_category = str(categories[0]).split(">")[1]
        also_visited_webistes_element = aud_interests_elements.xpath("div[2]/section[2]/div[1]/div")
        also_visited_webistes_list = []
        also_visited_websites_total = aud_interests_elements.xpath("div[2]/section[2]/div[2]/button/text()").extract()
        also_visited_websites_total = self.number_only(also_visited_websites_total[0])
        for website in also_visited_webistes_element:
            also_visited_webistes_list.append(str(website.xpath("div/a[1]/text()").extract()[0]))

        topic_list = []  # can be delete
        topic_list_dict = []
        for topic in response.xpath("//ul[@class='topics-list js-cloudContainer']/li/text()").extract():
            topic_list.append(topic)  # can be delete
            topic_dict = {}
            topic_dict['Topic_Name'] = str(topic)
            topic_list_dict.append(topic_dict)
        item['Topics'] = topic_list_dict
        print("*******************  Topics ************************")
        print(topic_list_dict)
        print("**********************Also Visited Sites ******************************")
        also_visited_webistes_values = {'Domains': [also_visited_webistes_list],
                                        'Total': also_visited_websites_total}
        item['AlsoVisited_Websites'] = also_visited_webistes_values
        print item['AlsoVisited_Websites']
        print(main_category, sub_category, also_visited_webistes_list, topic_list,
              also_visited_websites_total)  # can be delete

        print("***************** Audience Interests ******************************")
        item['Audience_Interests'] = [{'Main_Category': main_category,
                                       'Sub_Category': sub_category}]

        print (item['Audience_Interests'])

        print ("************************** Engagement *******************************")

        overview_elements = response.xpath("//div[@data-waypoint='overview']")
        engagement_keys = []
        engagement_values = []
        for engagement in overview_elements.xpath("div[2]/div[2]/div/div"):
            key = engagement.xpath("div/span[1]/text()").extract()
            value = engagement.xpath("div/span[2]/text()").extract()
            if key:
                engagement_keys.append(str(key[0]))
            if value:
                if "%" in str(value[0]):
                    value = self.percent_to_float(str(value[0]))
                    engagement_values.append(value)
                elif "M" in str(value[0]):
                    value = self.million_to_number(value[0])
                    engagement_values.append(value)
                else:
                    engagement_values.append(str(value[0]))

        print (engagement_keys, engagement_values)
        item['Engagement'] = dict(zip(engagement_keys, engagement_values))
        print(item['Engagement'])

        ######################## Traffic By Countires ##################################
        print("******************* Traffic By Countries ***************************************")
        traffic_countries_keys = []  # can be delete
        traffic_countries_values = []  # can be delete
        traffic_total_countries_dict = {}
        traffic_countries_list_dict = []
        "[[u'United States'], [u'India'], [u'Canada'], [u'United Kingdom'], [u'Philippines'], []], [[u'80.04%'], [u'4.46%'], [u'1.53%'], [u'1.19%'], [u'1.00%'], []])"
        for countries in response.xpath("//div[@id='geo-countries-accordion']/div"):
            key = countries.xpath("div/span/a/text()").extract()
            value = countries.xpath("div/span/span/text()").extract()
            countries_dict = {}
            if key:
                traffic_countries_keys.append(str(key[0]))  # can be delete
                countries_dict['Country'] = str(key[0])

            if value:
                traffic_countries_values.append(self.percent_to_float(value[0]))  # can be delete
                countries_dict['Percent'] = self.percent_to_float(value[0])

            traffic_countries_list_dict.append(countries_dict)
            traffic_countries_total = countries.xpath("button/text()").extract()
            if traffic_countries_total:
                traffic_total_countries_dict['Total_Countries'] = self.number_only(traffic_countries_total[0])
        item['Traffic_By_Countries'] = [traffic_total_countries_dict, traffic_countries_list_dict]

        print (item['Traffic_By_Countries'])

        ####################### Similar Web URL ####################################
        print("************** Similar Web URL ***************************")
        item['Similar_Web_URL'] = response.url

        print("********************** Traffic Sources ************************")
        traffic_source_chart_elements = response.xpath("//ul[@class='trafficSourcesChart-list']/li")
        # 1 - Direct
        tf1_direct_name = traffic_source_chart_elements[0].xpath("div[2]/div/span/text()").extract()
        tf1_direct_value = traffic_source_chart_elements[0].xpath("div[1]/div/div/text()").extract()

        # 2- Referrals
        tf2_referrals_name = traffic_source_chart_elements[1].xpath("div[2]/div/a/text()").extract()
        tf2_referrals_value = traffic_source_chart_elements[1].xpath("div[1]/div/div/text()").extract()

        # 3- Serach
        tf3_search_name = traffic_source_chart_elements[2].xpath("div[2]/div/a/text()").extract()
        tf3_search_value = traffic_source_chart_elements[2].xpath("div[1]/div/div/text()").extract()

        # 4- Social
        tf4_social_name = traffic_source_chart_elements[3].xpath("div[2]/div/a/text()").extract()
        tf4_social_value = traffic_source_chart_elements[3].xpath("div[1]/div/div/text()").extract()

        # 5-Mail
        tf5_mail_name = traffic_source_chart_elements[4].xpath("div[2]/div/span/text()").extract()
        tf5_mail_value = traffic_source_chart_elements[4].xpath("div[1]/div/div/text()").extract()

        # 6 - Display
        tf6_display_name = traffic_source_chart_elements[5].xpath("div[2]/div/a/text()").extract()
        tf6_display_value = traffic_source_chart_elements[5].xpath("div[1]/div/div/text()").extract()


        print(tf1_direct_name, tf1_direct_value)
        print(tf2_referrals_name, tf2_referrals_value)
        print(tf3_search_name, tf3_search_value)
        print(tf4_social_name, tf4_social_value)
        print(tf5_mail_name, tf5_mail_value)
        print(tf6_display_name, tf6_display_value)

        print("*********** Referrals ************************")

        refferals_elements = response.xpath("//div[@data-waypoint='referrals']")

        print("*********** Top Refering sites *************")

        top_refering_sites_dict_list = []
        top_reffering_sites = []
        top_refering_sites_total = refferals_elements.xpath("div[2]/section/div[1]/div[3]/button/text()").extract()
        top_reffering_sites_element = response.xpath("//div[@class='referralsSites referring']/ul/li")

        for site in top_reffering_sites_element:
            refering_site_dict = {}
            refering_site = site.xpath("div/a[1]/text()").extract()
            top_reffering_sites.append(site.xpath("div/a[1]/text()").extract())
            refering_site_dict['Domains'] = str(refering_site[0])
            top_refering_sites_dict_list.append(refering_site_dict)
        print(top_reffering_sites)
        print(top_refering_sites_total)

        print("**************** Top Destionation sites ******************")
        top_destination_sites = []
        top_destination_sites_dict_list = []
        top_destination_sites_total = refferals_elements.xpath("div[2]/section/div[3]/div[3]/button/text()").extract()
        top_destination_sites_element = response.xpath("//div[@class='referralsSites destination']/ul/li")
        for site in top_destination_sites_element:
            destination_site_dict = {}
            destination_site = site.xpath("div/a[1]/text()").extract()
            destination_site_dict['Domain'] = str(destination_site[0])
            top_destination_sites_dict_list.append(destination_site_dict)
            top_destination_sites.append(site.xpath("div/a[1]/text()").extract())

        print(top_destination_sites_dict_list)
        print(top_destination_sites_total)
        print("***************** Referrals *****************************")

        referrals_dict = {
            "Percent": self.percent_to_float(tf2_referrals_value[0]),
            "Top_Referring": {
                "Domains": top_refering_sites_dict_list,
                "Total": self.number_only(top_refering_sites_total[0])
            },
            "Top_Destination": {
                "Domains": top_destination_sites_dict_list,
                "Total": self.number_only(top_destination_sites_total[0])
            }}
        print(referrals_dict)



        ################ Display Advertising ##################
        print("**************** Display Advertising *******************************")

        display_advertising_elements = response.xpath("//div[@data-waypoint='display']")

        print("**************** Top Publisher  *******************************")
        top_publisher_elements = display_advertising_elements.xpath("div[2]/div[2]/div[1]")
        top_publisher_sites_list = []
        publisher_sites_total = display_advertising_elements.xpath("div[2]/div[2]/div[2]/button/text()").extract()
        top_publisher_sites_list.append(top_publisher_elements.xpath("div[1]/div/a[1]/text()").extract())
        top_publisher_sites_list.append(top_publisher_elements.xpath("div[2]/div/a[1]/text()").extract())
        top_publisher_sites_list.append(top_publisher_elements.xpath("div[3]/div/a[1]/text()").extract())
        top_publisher_sites_list.append(top_publisher_elements.xpath("div[4]/div/a[1]/text()").extract())
        top_publisher_sites_list.append(top_publisher_elements.xpath("div[5]/div/a[1]/text()").extract())

        print(top_publisher_sites_list)
        print(publisher_sites_total)

        print("**************** Top Ad Networks  *******************************")
        top_ad_networks_elements = response.xpath("//div[@class='highcharts-data-labels']").extract()
        top_ad_networks_names_dict_list = []
        for title in top_ad_networks_elements:
            networks_dict = {}
            name = title.xpath("span/text()").extract()
            networks_dict['Domain'] = name
            top_ad_networks_names_dict_list.append(networks_dict)
        print(top_ad_networks_names_dict_list)
        print("******************* Display Advertising Dict **********************************")
        display_advertising_dict ={"Percent":self.percent_to_float(tf6_display_value[0]),
                                    "Top_Publishers": {"Domains": top_publisher_sites_list,
                                                        "Total":self.number_only(publisher_sites_total[0])},
                                    "Top_Ad_Networks": top_ad_networks_names_dict_list}
        print(display_advertising_dict)

        ###################### Search ########################
        print("********************** Searches ***************************************")

        search_pie_elements = response.xpath("//div[@class='searchPie']")
        organic_searches_total_percent = search_pie_elements.xpath("div[1]/span[1]/text()").extract()
        paid_searches_total_percent = search_pie_elements.xpath("div[3]/span[1]/text()").extract()
        search_keywords_elements = response.xpath("//div[@class='searchKeywords']")

        organic_searches_elements = search_keywords_elements.xpath("div[1]/ul/li")
        organic_searches_total_keywords = search_keywords_elements.xpath("div[1]/div[2]/button/text()").extract()
        organic_searches_keywords_list = []
        for keyword in organic_searches_elements:
            organic_searches_keywords_list.append(str(keyword.xpath("span[2]/span/text()").extract_first()))

        paid_searches_elements = search_keywords_elements.xpath("div[2]/ul/li")
        paid_searches_total_keywords = search_keywords_elements.xpath("div[2]/div[2]/button/text()").extract()
        paid_searches_keywords_list = []
        for keyword in paid_searches_elements:
            paid_searches_keywords_list.append(str(keyword.xpath("span[2]/span/text()").extract_first()))

        search_dict = {"Percent": self.percent_to_float(tf3_search_value[0]),
                        "Organic": {
                            "Percent": self.percent_to_float(organic_searches_total_percent[0]),
                            "Keywords": organic_searches_keywords_list,
                            "Total": self.number_only(organic_searches_total_keywords[0])
                        },
                        "Paid": {
                            "Percent": self.percent_to_float(paid_searches_total_percent[0]),
                            "Keywords": paid_searches_keywords_list,
                            "Total": self.number_only(paid_searches_total_keywords[0])
                        }
                     }

        print (search_dict)


        ######### Social #############################

        print("****************** social **************************")

        tf2_social_elements = response.xpath("//ul[@class='socialList']/li")
        social_domain_dict_list = []
        for domain in tf2_social_elements:
            domain_dict = {}
            name = domain.xpath("div[1]/a/text()").extract()
            value = domain.xpath("div[2]/div[2]/text()").extract()
            domain_dict['Domain'] = str(name[0])
            domain_dict['Percent'] = self.percent_to_float(value[0])
            social_domain_dict_list.append(domain_dict)

        social_dict =  {
            "Percent": self.percent_to_float(tf4_social_value[0]),
            "Domains": [social_domain_dict_list]
        }
        print(social_dict)

        print("****************** Mail  **************************")
        mail_dict = {'Percent': self.percent_to_float(tf5_mail_value[0])}
        print(mail_dict)

        print("****************** Direct **************************")
        direct_dict = {'Percent': self.percent_to_float(tf1_direct_value[0])}
        print(direct_dict)

        print ("****************** Traffice Source Dict ***************************")
        item['Traffic_Sources'] = {"Direct": direct_dict,
                                   "Referrals": referrals_dict,
                                   "Search": search_dict,
                                   "Social": social_dict,
                                   "Mail": mail_dict,
                                   "Display_Advertising": display_advertising_dict}

        print(item['Traffic_Sources'])
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
        print(website_content_subdomains, website_content_subdomain_value, website_subdomain_names,
              website_subdomain_share_values)

        website_content_folders = "Folders"
        website_content_folders_value = website_content_elements.xpath("div[3]/div[4]/span[1]/text()").extract()

        website_folder_names = []
        website_folder_share_values = []
        for folder in website_content_elements.xpath("div[3]/div[5]/div"):
            website_folder_names.append(folder.xpath("span[1]/span[2]/span/text()").extract())
            website_folder_share_values.append(folder.xpath("span[2]/span[2]/text()").extract())

        print ("********************")
        print(website_content_folders, website_content_folders_value, website_folder_names, website_folder_share_values)

        #########  Mobile Apps #############################

        print("********************* Related Mobile Apps ***************************")
        ############### Apple Store ########################
        print("**********************    APPLE      ****************************************")
        apple_app_elements = response.xpath("//div[@class='apps-store-group apple']/div/ul/li")
        apple_app_dict_list = []
        for app in apple_app_elements:
            app_dict = {}
            app_dict['Name'] = str(app.xpath("a/span[2]/span/text()").extract_first())
            app_dict["URL"] = str(app.xpath("span/a/@href").extract_first())
            apple_app_dict_list.append(app_dict)

        print(apple_app_dict_list)

        print("**********************       Google      ****************************************")
        google_app_elements = response.xpath("//div[@class='apps-store-group google']/div/ul/li")
        google_app_dict_list = []
        for app in google_app_elements:
            app_dict = {}
            app_dict['Name'] = str(app.xpath("a/span[2]/span/text()").extract_first())
            app_dict["URL"] = str(app.xpath("span/a/@href").extract_first())
            google_app_dict_list.append(app_dict)
        print(google_app_dict_list)

        print("********************* Related Mobile Apps ***************************")
        item['Related_Mobile_Apps'] = {"Google_Play": google_app_dict_list,
                                       "App_Store": apple_app_dict_list
                                       }
        print(item['Related_Mobile_Apps'])

        #########  Mobile Apps #############################



        yield item

    def number_only(self, string):
        return int(re.sub("\D", "", string))

    def percent_to_float(self, string):
        return float(string.strip('%')) / 100

    def million_to_number(self, string):
        return float(string.strip("M")) * 1000000
