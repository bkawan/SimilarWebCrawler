# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import json
import csv

class SimilarWebDataToJSONPipeline(object):

    def __init__(self):
        self.file = open('similarweboutputdata.json', 'wb')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

class SimilarWebDataToCSVPipeline(object):

    def __init__(self):
        self.csvwriter = csv.writer(open('similarweboutputdata.csv', 'wb'))
        self.csvwriter.writerow(['Domain','Global_Rank','Country_Rank''Category_Rank','Main_Category','Sub_Category'])
    def process_item(self,item,spider):
        self.csvwriter.writerow([item['Domain'],
                                 item['Ranks']['Global_Rank']['Rank'],
                                 item['Ranks']['Country_Rank']['Rank'],
                                 item['Ranks']['Category_Rank']['Rank'],
                                 item['Ranks']['Category_Rank']['Main_Category'],
                                 item['Ranks']['Category_Rank']['Sub_Category']])
        return item
