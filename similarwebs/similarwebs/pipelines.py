# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html




import json
import csv
import codecs
from similarwebs.items import SimilarwebsErrorItem
from similarwebs.items import SimilarwebsItem


json_path = "/Users/bikeshkawan/Development/phunka/GitHub/SimilarWebCrawler/similarwebs/json/"
csv_path = "/Users/bikeshkawan/Development/phunka/GitHub/SimilarWebCrawler/similarwebs/csv/"
class SimilarWebDataToSingleJson(object):

    def __init__(self):
        self.file = codecs.open('{}alldomainsdata.json'.format(json_path), 'wb',encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item),ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

class SimilarWebDataToJson(object,):

    i = 2

    def process_item(self, item, spider):
        self.file = codecs.open('{}{}-{}.json'.format(json_path,self.i,item['Overview']['Domain']), 'wb', encoding = 'utf-8')
        line = json.dumps(dict(item),ensure_ascii=False) + "\n"
        self.file.write(line)
        self.i +=1
        return item

class SimilarWebDataToCsv(object):

    def __init__(self):
        self.csvwriter = csv.writer(open('{}alldomainsdata.csv'.format(csv_path), 'wb'))
        self.csvwriter.writerow(
            ['Domain', 'Global_Rank', 'Country_Name','Country_Rank','Category_Rank', 'Main_Category', 'Sub_Category'])

    def process_item(self, item, spider):

        self.csvwriter.writerow([item['Overview']['Domain'],
                                 item['Overview']['Ranks']['Global_Rank']['Rank'],
                                 item['Overview']['Ranks']['Country_Rank']['Rank'],
                                 item['Overview']['Ranks']['Country_Rank']['Country'],
                                 item['Overview']['Ranks']['Country_Rank']['Rank'],
                                 item['Overview']['Ranks']['Category_Rank']['Main_Category'],
                                 item['Overview']['Ranks']['Category_Rank']['Sub_Category']])
        return item

class SimilarWebError(object):
    pass

    #
    # def __init__(self):
    #     self.csvwriter = csv.writer(open('{}error.csv'.format(csv_path), 'wb'))
    #     self.csvwriter.writerow(
    #         ['Domain'])
    #
    # def process_item(self, item, spider):
    #     if isinstance(item,SimilarwebsErrorItem):
    #         self.csvwriter.writerow([item])
    #         return item
