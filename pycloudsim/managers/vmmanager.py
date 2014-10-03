from pycloudsim.model.tracegen import TraceGenerator
from itertools import islice
from pycloudsim.model.virtualmachine import VirtualMachine
from pycloudsim.common import log


class VMManager:
    #def __init__(self, trace_file, total_vm):
    def __init__(self):#, total_vm):
        self.add_virtual_machines_factory = None
        self.add_virtual_machines_args = None
        self.add_virtual_machines_callback = None
        self.total_vm = 0
        self.items = []

#        tg = TraceGenerator(trace_file)
#        trace = tg.gen_trace()
#        self.items = []
#        for t in islice(enumerate(trace), total_vm):
#            self.items += [VirtualMachine(t[0], t[1][0], t[1][1], t[1][2], t[1][3])]

#    def items(self, numeric_id):
#        return {
#            'weight': self.vm_list[numeric_id].value['weight'],
#            'cpu': self.vm_list[numeric_id].cpu(),
#            'mem': self.vm_list[numeric_id].mem(),
#            'disk': self.vm_list[numeric_id].disk(),
#            'net': self.vm_list[numeric_id].net(),
#        }

    #def set_vm_count(self, trace_file, total_vm):
    def set_vm_count(self, total_vm):
        self.total_vm = total_vm
#        self.vmm = VMManager(trace_file, total_vm)

    def get_item_index(self, id):
        result = -1
        i = 0
        found = False
        while i < len(self.items) and not found:
            item = self.items[i]
            j = item.id
            found = j == id.id
            if found:
                result = i
            i += 1
        return result

    def get_item_values(self, id):
        result = self.get_item_index(id)
        if result is not -1:
            result = self.items[result]
        else:
            result = None
        return result

    def items_remove(self, remove_list):
        for to_delete in remove_list:
            i = self.get_item_index(to_delete)
            if i is not -1:
                del self.items[i]

    def __str__(self):
        result = 'VMPool['
        for item in self.items:
            result += str(item) + ', '
        result += ']'
        return result

    def add_virtual_machine(self, vm):
        self.items += [vm]
        self.total_vm += 1
        #import ipdb; ipdb.set_trace() # BREAKPOINT
        log.info('add_virtual_machine {}'.format(vm))
        #print('add_virtual_machine: {}'.format(vm))

    def add_virtual_machines(self, vm=None):
        if self.add_virtual_machines_factory:
            result = self.add_virtual_machines_factory(
                **self.add_virtual_machines_args)
            for vm in result:
                self.add_virtual_machine(vm)
                if self.add_virtual_machines_callback:
                    self.add_virtual_machines_callback(vm)
        else:
            if vm.__class__ is VirtualMachine:
                self.add_virtual_machines(vm)
