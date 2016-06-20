# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import csv
class SimilarWebDataToJson(object):

    def __init__(self):
        self.file = open('similarweboutputdata.json', 'wb')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

class SimilarWebDataToCsv(object):

    def __init__(self):
        self.csvwriter = csv.writer(open('similarweboutputdata.csv', 'wb'))
        self.csvwriter.writerow(
            ['Domain', 'Global_Rank', 'Country_Rank''Category_Rank', 'Main_Category', 'Sub_Category'])

    def process_item(self, item, spider):
        self.csvwriter.writerow([item['Overview']['RedirectUrl'],
                                 item['Overview']['GlobalRank'][0],
                                 item['Overview']['CountryRanks'].values()[0][0],
                                 item['Overview']['CategoryRank'][0],
                                 item['Overview']['Category'].split("/")[0],
                                 item['Overview']['Category'].split("/")[1]])
        return item
