import collections
import numpy as np
import scipy.stats as stats
import csv


def filter_equals(data, column, value):
    column = data[column]
    index, value = min(enumerate(column), key=lambda x: abs(x[1]-value))
#    print('index={}, value={}'.format(index, value))
    newdata = {}
    for key, list_value in data.iteritems():
        newdata[key] = list_value[index]
    return newdata

def indexes_between(list_data, minv, maxv):
    result = []
    for index, value in enumerate(list_data):
        if minv <= value <= maxv:
            result += [index]
    return result

def filter_range(data, column, minv, maxv):
    column = data[column]
    indexes = indexes_between(column, minv, maxv)
    newdata = {}
    for key, list_value in data.iteritems():
        newdata[key] = [list_value[i] for i in indexes]
    return newdata


class TraceFilter():
    def __init__(self, fname):
        self.fname = fname
        self.file_in = open(fname)
        self.reader = csv.DictReader(self.file_in, delimiter='\t')
        fields = self.reader.fieldnames
        data = {}
        for line in self.reader:
            for field in fields:
                d = data.get(field)
                if not d:
                    try:
                        data[field] = [float(line[field])]
                    except:
                        data[field] = [str(line[field])]
                else:
                    try:
                        data[field].append(float(line[field]))
                    except:
                        data[field].append(str(line[field]))
        self.data = data
        self.filtered_data = {}

    def csv_write(self):
        f = self.filtered_data.keys()
        print f
        self.fname = 'eggs.csv'
        self.file_out = open(self.fname, mode='w')
        self.writer = csv.DictWriter(self.file_out, fieldnames=f, delimiter='\t')

        for column in self.filtered_data.keys():
            inverted_item = {}
            for value in self.filtered_data[column]:
                inverted_item[column] = value
                print inverted_item
                self.writer.writerow(inverted_item)
#        with open('eggs.csv', 'wb') as csvfile:
#            spamwriter = csv.DictWriter(csvfile, fieldnames=f, delimiter='\t')
#            spamwriter.writerow(self.filtered_data)

    def filter_rows_by_range(self, column, minv, maxv):
        self.filtered_data = filter_range(self.data, column, minv, maxv)




#        min = np.amin(column)
#        max = np.amax(column)
#        mean = np.mean(column)
#        print('min={}, max={}, mean={}'.format(min, max, mean))
