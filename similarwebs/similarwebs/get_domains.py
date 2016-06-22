

import csv

class GetDomains:
    data = None
    csv_path = "/Users/BIKESHKAWAN/Development/phunka/similarwebs/csv/"


    def connect(self):
        readfile = open('{}similarweb_domains.csv'.format(self.csv_path))
        self.data = csv.reader(readfile)

    def next_url(self):
        for row in self.data:
            yield row[0]

