from lxml import etree
import lxml.html
from collections import defaultdict, OrderedDict
import traceback

class SpecParser():
    def __init__(self):
        self.directory = None
        self.specs_by_load = []
        self.specs_by_consumption = []
        self.specs_by_ratio = []
        self.consumptions = []
        self.ratios = []
        self.num = -1
        self.cpu_freq = None
        self.cores = None
        self.threads = None
        self.current = None

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def set_directory(self, directory):
        self.directory = directory

    def parse(self, filename):
        doc = lxml.html.parse(self.directory + '/' + filename)
        #doc = lxml.html.parse('power_ssj2008-20121031-00575.html')

        # CPU Frequency
        spec_hw_cpu_freq_path = '//*[@id="set_sut"]/div[3]/table/tbody/tr[6]/td[2]'
        xp_spec_hw_cpu_freq = doc.xpath(spec_hw_cpu_freq_path)
        self.cpu_freq = int(xp_spec_hw_cpu_freq[0].text)
        # Cores
        spec_hw_cores_path = '//*[@id="set_sut"]/div[3]/table/tbody/tr[7]/td[2]'
        xp_spec_hw_cores = doc.xpath(spec_hw_cores_path)
        self.cores = int(xp_spec_hw_cores[0].text.split()[0])
        # Threads
        spec_hw_threads_path = '//*[@id="set_sut"]/div[3]/table/tbody/tr[8]/td[2]'
        xp_spec_hw_threads = doc.xpath(spec_hw_threads_path)
        self.threads = int(xp_spec_hw_threads[0].text.split()[0])

        spec_loads_path = '//*[@id="resultsSummary"]/div[2]/table/tbody/tr/td[1]'
        spec_power_consumption_path = '//*[@id="resultsSummary"]/div[2]/table/tbody/tr/td[4]'
        spec_idle_consumption_path = '//*[@id="resultsSummary"]/div[2]/table/tbody/tr[11]/td[3]'
        spec_perfpower_ratio_path = '//*[@id="resultsSummary"]/div[2]/table/tbody/tr/td[5]'
        xp_spec_loads = doc.xpath(spec_loads_path)
        xp_spec_power_consumptions = doc.xpath(spec_power_consumption_path)
        xp_spec_idle_consumptions = doc.xpath(spec_idle_consumption_path)
        xp_spec_perfpower_ratios = doc.xpath(spec_perfpower_ratio_path)

        #spec_loads = [if col is not None: col.text[:-1] for col in xp_spec_loads]
        spec_loads = []
        for col in xp_spec_loads:
            if col is not None and col.text is not None:
                spec_loads += [int(col.text[:-1])]
        spec_loads += [0]

        idle_consumption = float(xp_spec_idle_consumptions[0].text.replace(',',''))
        spec_power_consumption = [float(col.text.replace(',','')) for col in xp_spec_power_consumptions][:-1] + [idle_consumption]

        spec_perfpower_ratios = [float(col.text.replace(',','')) for col in xp_spec_perfpower_ratios] + [0.0]
        specs_list = zip(spec_loads, spec_power_consumption, spec_perfpower_ratios)

        self.specs_by_load = defaultdict(defaultdict)
        self.specs_by_consumption = defaultdict(defaultdict)
        self.specs_by_ratio = defaultdict(defaultdict)

        for spec in specs_list:
            load = spec[0]
            consumption = spec[1]
            ratio = spec[2]
            self.consumptions += [consumption]
            self.ratios += [ratio]
            self.specs_by_load[load]['consumption'] = consumption
            self.specs_by_load[load]['ratio'] = ratio
            self.specs_by_consumption[consumption]['load'] = load
            self.specs_by_consumption[consumption]['ratio'] = ratio
            self.specs_by_ratio[ratio]['load'] = load
            self.specs_by_ratio[ratio]['consumption'] = consumption

        self.consumptions.sort()
        self.ratios.sort()
        self.ratios.reverse()

    def next(self):
        if self.num < 9:
            result, self.num = self.num, self.num + 1
            current_ratio = self.ratios[self.num]
            result = self.specs_by_ratio[current_ratio]#['consumption']
            self.current = result
            return result
        else:
            raise StopIteration()

    def next_consumption(self):
        return self.next()['consumption']

    def next_ratio(self):
        self.next()
        return self.ratios[self.num]

    def next_load(self):
        return self.next()['load']

    def curr_consumption(self):
        result = None
        if self.current is not None:
            result = self.current['consumption']
        return result

    def curr_ratio(self):
        result = None
        if self.current is not None:
            result = self.ratios[self.num]
        return result

    def curr_load(self):
        result = None
        if self.current is not None:
            result = self.current['load']
        return result

    def optimal_load(self):
        return self


#sorted_results = sorted(results.iterkeys())
#
#keylist = results.keys()
#key_results = keylist.sort()
#
## specs[80]['ratio']
## specs[80]['power']
##print xp[0]
#
#s = """<table>
#  <tr><th>Event</th><th>Start Date</th><th>End Date</th></tr>
#  <tr><td>a</td><td>b</td><td>c</td></tr>
#  <tr><td>d</td><td>e</td><td>f</td></tr>
#  <tr><td>g</td><td>h</td><td>i</td></tr>
#</table>
#"""
##table = etree.XML(s)
##rows = iter(doc)
##headers = [col.text for col in next(rows)]
##headers = [col.text for col in xp]
#for row in rows:
#    values = [col.text for col in row]
#    print dict(zip(headers, values))


if __name__ == "__main__":
    pass
    #spec_parser = SpecParser()
    #spec_parser.set_directory('./')
    #spec_parser.parse('power_ssj2008-20121031-00575.html')
    #print(spec_parser.optimal_load().next())
    #print(spec_parser.optimal_load().next())
    #print(spec_parser.optimal_load().next())
    #print(spec_parser.optimal_load().next())
    #print(spec_parser.optimal_load().next())
    #print(spec_parser.optimal_load().next())
    #print(spec_parser.optimal_load().next())
    #print(spec_parser.optimal_load().next())
    #print(spec_parser.optimal_load().next())
    #print(spec_parser.optimal_load().next())
