class VirtualMachine(dict):
    __count__ = 0
    def __init__(self, id, flavor):# cpu_gen, mem_gen, disk_gen, net_gen):
        #id = uuid.uuid1()
        self.value = {}
        self.id = id #'%d' % id #VirtualMachine.__count__
        #self.id = str(id)[4:8] #'%d' % VirtualMachine.__count__
        self.value['weight'] = 1
        #self.value['cpu'] = cpu
        #self.value['mem'] = mem
        #self.value['disk'] = disk
        #self.value['net'] = net
        self.value['n'] = 1
        self.value['placed'] = 0
        self.value['flavor'] = flavor
        VirtualMachine.__count__ += 1

    def set_cpu_gen(self, cpu_gen):
        self.value['cpu_gen'] = cpu_gen

    def set_mem_gen(self, mem_gen):
        self.value['mem_gen'] = mem_gen

    def set_disk_gen(self, disk_gen):
        self.value['disk_gen'] = disk_gen

    def set_net_gen(self, net_gen):
        self.value['net_gen'] = net_gen

    def __str__(self):
        #result = 'VM{}({}, {}, {}, {})'.format(
        result = 'VM{}'.format(
            self.id,
#            self.value['cpu'],
#            self.value['mem'],
#            self.value['disk'],
#            self.value['net']
            )
        return result

    def __getitem__(self, attribute):
        # http://stackoverflow.com/questions/5818192/getting-field-names-reflectively-with-python
        # val = getattr(ob, attr)
        if type(attribute) is str:
            ob = self.value
            result = ob[attribute]
            return result
        else:
            print('getitem: attribute is not a string, is:{}, value:{}'.format(type(attribute), attribute))
