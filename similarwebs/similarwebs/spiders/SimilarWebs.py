# -*- coding: utf-8 -*-
import scrapy
from similarwebs.get_domains import GetDomains
from scrapy import signals
from scrapy.http import TextResponse
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
import json
import re
import codecs
import locale
import sys
from decimal import  Decimal, ROUND_HALF_UP
from similarwebs.items import SimilarwebsItem




class SimilarwebsSpider(scrapy.Spider):
    name = "similarwebs"
    allowed_domains = ["similarweb.com"]
    args = False
    start_urls = [
        # "https://www.similarweb.com/website/jobsnepal.com",
        # "https://www.similarweb.com/website/google.com",
        # "https://www.similarweb.com/website/ebay.com",

        # "file:///Users/BIKESHKAWAN/Development/phunka/similarwebs/csv/hamrobazar.html"

    ]
    url = GetDomains()
    base_url ="https://www.similarweb.com/website/"

    def __init__(self,*args,**kwargs):
        self.driver = webdriver.Chrome()
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
        reload(sys)
        sys.setdefaultencoding('utf-8')
        if kwargs.get('url'):
            self.start_urls = [kwargs.get('url')]
            self.args = True

    def spider_closed(self, spider):
        self.driver.close()

    def start_requests(self):
        if not self.args:
            self.url.connect()
            urls = self.url.next_url().next()
            start_url = self.base_url + urls
            print (start_url)
        else:
            start_url = self.base_url + self.start_urls[0]

        yield scrapy.Request(start_url)

    def parse(self, response):
        if not self.args:
            next_url = self.base_url + self.url.next_url().next()

            yield scrapy.Request(next_url,self.parse_website,dont_filter=True)
            yield scrapy.Request(next_url)
        else:
            print("****************")
            print(response.url)
            print("****************")

            yield scrapy.Request(response.url,self.parse_website)


    def parse_website(self, response):
        html_path = "/Users/bikeshkawan/Development/phunka/GitHub/SimilarWebCrawler/similarwebs/html/"
        self.driver.get(response.url)

        response = TextResponse(url=response.url, body=self.driver.page_source, encoding='utf-8')




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
        website_overview_data = json.loads(sw_preloaded_data)



        print("***************")
        print(sw_preloaded_data)
        print(type(website_overview_data))
        print(website_overview_data.keys())
        print(website_overview_data['overview'])
        print("****************")

        domain_name = website_overview_data['overview']['RedirectUrl']

        with open('{}{}.html'.format(html_path, domain_name), 'wb') as data:
            data.write(response.body)



        similar_web_url= response.url

        global_rank = website_overview_data['overview']['GlobalRank'][0]

        category_rank = website_overview_data['overview']['CategoryRank'][0]

        country_rank = website_overview_data['overview']['CountryRanks'].values()[0][0]



        top_destination_dict_list = website_overview_data['overview']['Referrals']['destination']
        top_destination_new_dict_list = []
        for destination in top_destination_dict_list:
            top_destionation_dict = {}
            top_destionation_dict['Domain'] = destination.values()[0]
            top_destionation_dict['Percent'] = self.float_limit_4(destination.values()[1])
            top_destination_new_dict_list.append(top_destionation_dict)

        top_referrals_dict_list = website_overview_data['overview']['Referrals']['referrals']
        top_referrals_new_dict_list = []
        for referrals in top_referrals_dict_list:
            top_destionation_dict = {}
            top_destionation_dict['Domain'] = referrals.values()[0]
            top_destionation_dict['Percent'] = self.float_limit_4(referrals.values()[1])
            top_referrals_new_dict_list.append(top_destionation_dict)
        mail_percent = website_overview_data['overview']['TrafficSources']['Mail']
        direct_percent = website_overview_data['overview']['TrafficSources']['Direct']
        search_percent = website_overview_data['overview']['TrafficSources']['Search']
        social_percent = website_overview_data['overview']['TrafficSources']['Social']
        referrals_percent= website_overview_data['overview']['TrafficSources']['Referrals']

        bounce_rate = website_overview_data['overview']['Engagements']['BounceRate']
        bounce_rate = self.percent_to_float(bounce_rate)
        total_engagement_visits = website_overview_data['overview']['Engagements']['TotalLastMonthVisits']
        total_engagement_visits = self.visit_units_to_number(total_engagement_visits)

        avg_time_on_page = website_overview_data['overview']['Engagements']['TimeOnSite']
        avg_page_views = website_overview_data['overview']['Engagements']['PageViews']
        avg_page_views = self.float(avg_page_views)
        weekly_traffic_number = website_overview_data['overview']['Engagements']['WeeklyTrafficNumbers']
        weekly_engagement_visits_dict_list = []
        for k, v in weekly_traffic_number.items():
            visit_dict = {}
            visit_dict['Date'] = k
            visit_dict['Visits'] = v
            weekly_engagement_visits_dict_list.append(visit_dict)
        top_ad_networks_list = website_overview_data['overview']['AdNetworks']['Data']
        top_ad_networks_dict_list = []
        for network in top_ad_networks_list:
            network_dict = {}
            network_dict['Domain'] = self.getIndex(network,0)
            network_dict['Percent'] = self.float_limit_4(self.getIndex(network, 2))
            top_ad_networks_dict_list.append(network_dict)
        category = website_overview_data['overview']['Category']
        main_category = category.split("/")[0]
        sub_category = category.split("/")[1]








        description = str(response.xpath("//div[@class='analysis-descriptionText']/text()").extract_first())

        ranking_items_elements = response.xpath("//div[@class='rankingItems']")
        country_rank_name = ranking_items_elements.xpath("div[2]/div/div[1]/a/text()").extract()

        ######################## Traffic By Countires ##################################
        print("******************* Traffic By Countries ***************************************")
        traffic_by_countries_dict_list = []
        for countries in response.xpath("//div[@id='geo-countries-accordion']/div"):
            key = countries.xpath("div/span/a/text()").extract()
            value = countries.xpath("div/span/span/text()").extract()
            countries_dict = {}
            if key:
                countries_dict['Country'] = self.getIndex(key,0)
            if value:
                countries_dict['Percent'] = self.percent_to_float(self.getIndex(value,0))
            traffic_by_countries_dict_list.append(countries_dict)

        print("********************** Traffic Sources ************************")
        traffic_source_chart_elements = response.xpath("//ul[@class='trafficSourcesChart-list']/li")

        print("*********** Referrals ************************")

        refferals_elements = response.xpath("//div[@data-waypoint='referrals']")
        top_referring_total = refferals_elements.xpath("div[2]/section/div[1]/div[3]/button/text()").extract_first()
        top_destination_total = refferals_elements.xpath("div[2]/section/div[3]/div[3]/button/text()").extract_first()
        top_referring_total = self.number_only(top_referring_total)
        top_destination_total  = self.number_only(top_destination_total)



        print("********************** Searches ***************************************")

        search_pie_elements = response.xpath("//div[@class='searchPie']")
        organic_percent = search_pie_elements.xpath("div[1]/span[1]/text()").extract_first()
        paid_percent = search_pie_elements.xpath("div[3]/span[1]/text()").extract_first()

        search_keywords_elements = response.xpath("//div[@class='searchKeywords']")

        organic_searches_elements = search_keywords_elements.xpath("div[1]/ul/li")
        organic_total = search_keywords_elements.xpath("div[1]/div[2]/button/text()").extract()
        organic_keywords_list = []
        for keyword in organic_searches_elements:
            organic_keywords_list.append(str(keyword.xpath("span[2]/span/text()").extract_first()))

        paid_searches_elements = search_keywords_elements.xpath("div[2]/ul/li")
        paid_total = search_keywords_elements.xpath("div[2]/div[2]/button/text()").extract()
        paid_keywords_list = []
        for keyword in paid_searches_elements:
            paid_keywords_list.append(str(keyword.xpath("span[2]/span/text()").extract_first()))

        organic_percent = self.percent_to_float(organic_percent),
        organic_total = self.number_only(self.getIndex(organic_total,0))
        paid_percent = self.percent_to_float(paid_percent),
        paid_total = self.number_only(self.getIndex(paid_total,0))

        print("****************** social **************************")

        social_elements = response.xpath("//ul[@class='socialList']/li")
        social_domain_dict_list = []
        for domain in social_elements:
            domain_dict = {}
            name = domain.xpath("div[1]/a/text()").extract()
            value = domain.xpath("div[2]/div[2]/text()").extract()
            domain_dict['Domain'] = self.getIndex(name,0)
            domain_dict['Percent'] = self.percent_to_float(self.getIndex(value,0))
            social_domain_dict_list.append(domain_dict)

        print("**************** Display Advertising *******************************")

        display_advertising_elements = response.xpath("//div[@data-waypoint='display']")

        print("**************** Top Publisher  *******************************")
        top_publishers_elements = display_advertising_elements.xpath("div[2]/div[2]/div[1]")
        top_publishers_list = []
        top_publishers_total = display_advertising_elements.xpath("div[2]/div[2]/div[2]/button/text()").extract_first()
        top_publishers_total = self.number_only(top_publishers_total)
        top_publishers_list.append(top_publishers_elements.xpath("div[1]/div/a[1]/text()").extract_first())
        top_publishers_list.append(top_publishers_elements.xpath("div[2]/div/a[1]/text()").extract_first())
        top_publishers_list.append(top_publishers_elements.xpath("div[3]/div/a[1]/text()").extract_first())
        top_publishers_list.append(top_publishers_elements.xpath("div[4]/div/a[1]/text()").extract_first())
        top_publishers_list.append(top_publishers_elements.xpath("div[5]/div/a[1]/text()").extract_first())

        try:
            display_advertising_percent = traffic_source_chart_elements[5].xpath("div[1]/div/div/text()").extract_first()
            display_advertising_percent = self.percent_to_float(self.getIndex(display_advertising_percent, 0))

        except:
            display_advertising_percent = "Null"




        print("******************* Audience Interests and Topics ************************")

        audience_interests_elements = response.xpath("//div[@data-waypoint='alsoVisited']")


        audience_interests_category = response.xpath("//a[@class='audienceCategories-itemLink']/text()").extract()
        try:
            if audience_interests_category:
                audience_interests_main_category = self.getIndex(audience_interests_category,0).split(">")[0]
                audience_interests_sub_category = self.getIndex(audience_interests_category,0).split(">")[1]
        except:
            audience_interests_main_category = "Null"
            audience_interests_sub_category = "Null"

        also_visited_webistes_elements = audience_interests_elements.xpath("div[2]/section[2]/div[1]/div")
        also_visited_websites_list = []
        also_visited_websites_total = audience_interests_elements.xpath("div[2]/section[2]/div[2]/button/text()").extract()
        also_visited_websites_total = self.number_only(self.getIndex(also_visited_websites_total,0))

        for website in also_visited_webistes_elements:
            also_visited_websites_list.append(str(website.xpath("div/a[1]/text()").extract()[0]))

        topics_dict_list = []
        for topic in response.xpath("//ul[@class='topics-list js-cloudContainer']/li"):


            topic_dict = {}
            topic_dict['Topic_Name'] = str(topic.xpath('text()').extract_first())
            topic_dict['Data_Weight']  = self.float_limit_4(float(topic.xpath('@data-weight').extract_first()))

            topics_dict_list.append(topic_dict)

        print("**********************Also Visited Sites ******************************")

        similar_sites_elements = response.xpath("//section[@class='similarSitesSection']/ul/li")
        similar_sites_list = []
        for site in similar_sites_elements:
            site = site.xpath("div/div/span/a[1]/text()").extract()
            similar_sites_list.append(self.getIndex(site,0))


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


        audience_interests_percent = 'Null'

        try:
            engagement_date = website_overview_data['Overview']['Date'].split("-")
            if engagement_date:

                engagement_date = "{}/{}".format(engagement_date[1],engagement_date[0])
            else:
                engagement_date = website_overview_data['Overview']['Date']
        except:
            engagement_date = 'Null'
        item = SimilarwebsItem()

        item['Overview']= {
            "SimilarWebURL": similar_web_url,
            "Domain": domain_name,
            "Description": description,
            "Ranks": {
                "Global_Rank": {
                    "Rank": global_rank
                },
                "Country_Rank": {
                    "Country": country_rank_name,
                    "Rank": country_rank
                },
                "Category_Rank": {
                    "Main_Category": main_category,
                    "Sub_Category": sub_category,
                    "Rank": category_rank
                }
            },
            "Engagement": {
                "Date": engagement_date,
                "Total_Visits": total_engagement_visits,
                "Visits":weekly_engagement_visits_dict_list ,
                "Avg_Time_On_Page": avg_time_on_page,
                "Avg_Page_Views": avg_page_views,
                "Bounce_Rate": bounce_rate
            },
            "Traffic_By_Countries": traffic_by_countries_dict_list

            ,
            "Traffic_Sources": {
                "Direct": {
                    "Percent": self.float_limit_4(direct_percent)
                },
                "Referrals": {
                    "Percent": self.float_limit_4(referrals_percent),
                    "Top_Referring": {
                        "Domains":top_referrals_new_dict_list,
                        "Total": top_referring_total
                    },
                    "Top_Destination": {
                        "Domains":top_destination_new_dict_list,
                        "Total": top_destination_total
                    }
                },
                "Search": {
                    "Percent": self.float_limit_4(search_percent),
                    "Organic": {
                        "Percent": self.float_limit_4(organic_percent),
                        "Keywords": organic_keywords_list,
                        "Total": organic_total
                    },
                    "Paid": {
                        "Percent": self.float_limit_4(paid_percent),
                        "Keywords": paid_keywords_list,
                        "Total": paid_total
                    }
                },
                "Social": {
                    "Percent": self.float_limit_4(social_percent),
                    "Domains": social_domain_dict_list
                },
                "Mail": {
                    "Percent": self.float_limit_4(mail_percent)
                },
                "Display_Advertising": {
                    "Percent": self.float_limit_4(display_advertising_percent),
                    "Top_Publishers": {
                        "Domains": top_publishers_list,
                        "Total": top_publishers_total
                    },
                    "Top_Ad_Networks": top_ad_networks_dict_list
                }
            },
            "Audience_Interests": [
                {
                    "Main_Category": audience_interests_main_category,
                    "Sub_Category": audience_interests_sub_category,
                    "Percent": self.float_limit_4(audience_interests_percent)
                }
            ],
            "Also_Visited_Websites": {
                "Domains": also_visited_websites_list,
                "Total": also_visited_websites_total
            },
            "Topics":topics_dict_list,
            "Similar_Sites": similar_sites_list,
            "Related_Mobile_Apps": {
                "Google_Play": google_app_dict_list,
                "App_Store": apple_app_dict_list

            }
        }

        yield item

    def float(self,string):
        try:
            value = float(string)
        except:
            value = 'Null'
        return value

    def float_limit_4(self, string):
        try:
            value = "%.4f" %string
            value = float(value)
        except:
            value = string
        return value

    def number_only(self, string):
        try:
            value =  int(re.sub("\D", "", string))
        except:
            value = "Null"
        return value

    def percent_to_float(self, string):
        try:
            value = float(string.strip('%')) / 100
            value = float("%.4f" %value)
        except:
            value = 'Null'

        return value


    def visit_units_to_number(self,string):


        if "M" in string:
            value = float(string.strip("M")) * 1000000
        elif "K" in string:
            value = float(string.strip("K")) * 1000
        elif "B" in string:
            value = float(string.strip("B")) * 1000000000
        else:
            value = float(string)



        return value


    def getIndex(self,item_list,index):
        try:
            value = item_list[index]
            if type(value) == "str":
                value = value.strip()
            else:
                value = value
        except:
            value = 'Null'

        return value
