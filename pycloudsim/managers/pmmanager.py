from pycloudsim.model.physicalmachine import PhysicalMachine
from pycloudsim.common import log


class PMManager:
    def __init__(self): #, total_pm):
        self.items = []
        self.add_physical_hosts_factory = None
        self.add_physical_hosts_args = None
        self.add_physical_hosts_callback = None
        self.total_pm = 0
#        self.items = [PhysicalMachine(i)
#                          for i in range(total_pm)]

#    def items(self, numeric_id):
#        return item_list[numeric_id]

    def set_pm_count(self, total_pm):
        self.total_pm = total_pm
#        self.pmm = PMManager(total_pm)

    def __str__(self):
        result = 'PMPool['
        for item in self.items:
            result += str(item) + ', '
        result += ']'
        return result

    def add_physical_host(self, host):
        self.items += [host]
        self.total_pm += 1
        log.info('add_physical_host {}'.format(host.id))
        #print('add_physical_host: {}'.format(host))

    def add_physical_hosts(self, host=None):
        if self.add_physical_hosts_factory:
            result = self.add_physical_hosts_factory(
                **self.add_physical_hosts_args)
            for host in result:
                self.add_physical_host(host)
                if self.add_physical_hosts_callback:
                    self.add_physical_hosts_callback(host)
        else:
            self.add_physical_host(host)
