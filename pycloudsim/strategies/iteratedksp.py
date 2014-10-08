from openopt import KSP

#def gen_costraint(self, values, constraint):
#    return values.value[constraint] < 99
#
#def add_constraints(self, values, constraint_list):
#    return [self.add_constraint(values, constraint) for constraint in constraint_list]

def add_constraint(values, constraint):
    # http://stackoverflow.com/questions/5818192/getting-field-names-reflectively-with-python
    # val = getattr(ob, attr)
    return values[constraint] < 99

def add_constraints(values, constraint_list):
    return [add_constraint(values, constraint) for constraint in constraint_list]

class OpenOptStrategyPlacement:
    def __init__(self):
        self.constraints = None
        self.items = None
        self.vmm = None
        self.pmm = None
        #self.items_count = items_count
        #self.hosts_count = hosts_count
#        self.gen_costraints(['cpu', 'mem', 'disk', 'net'])
        self.gen_costraints()

#    def gen_costraints(self, constraint_list):
#        self.constraints = lambda values: (
#            add_constraints(values, constraint_list)
#        )

    def gen_costraints(self): #, constraint_list):
        self.constraints = lambda values: (
            values['cpu'] < self.available_cpu,
            values['mem'] < self.available_mem,
            values['disk'] < self.available_disk,
            values['net'] < self.available_net,
            #add_constraints(values, constraint_list)
        )

    def get_vm_objects(self, items_list):
        result = []
        for item in items_list.xf:
            result += [self.vmm.items[item]]#get_item_values(item)]
        return result

    def set_vmm(self, vmm):
        self.vmm = vmm
        self.items = self.vmm.items

    def set_base_graph_name(self, base_graph_name):
        self.base_graph_name = base_graph_name

    def solve_host(self, upper_bounds):
        self.available_cpu = upper_bounds[0]
        self.available_mem = upper_bounds[1]
        self.available_disk = upper_bounds[2]
        self.available_net = upper_bounds[3]
        p = KSP('weight', self.items, constraints = self.constraints)
        result = p.solve('glpk', iprint = -1)
        return result
