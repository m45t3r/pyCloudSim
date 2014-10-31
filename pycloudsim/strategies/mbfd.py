import operator

class ModifiedBestFitDecreasingPlacement:
    def __init__(self):
        self.constraints = None
        self.items = None
        self.vmm = None
        self.pmm = None
        self.gen_costraints(['cpu', 'mem', 'disk', 'net'])

    def gen_costraints(self, constraint_list):
        self.constraints = lambda values: (
            add_constraints(values, constraint_list)
        )

    def check_constraints(self, item_list):
        total_cpu = sum(map(operator.itemgetter('cpu'), item_list))
        total_mem = sum(map(operator.itemgetter('mem'), item_list))
        total_disk = sum(map(operator.itemgetter('disk'), item_list))
        total_net = sum(map(operator.itemgetter('net'), item_list))
        return \
            total_cpu < self.available_cpu and \
            total_mem < self.available_mem and \
            total_disk < self.available_disk and \
            total_net < self.available_net

    def get_vm_objects(self, items_list):
        return items_list

    def set_vmm(self, vmm):
        self.vmm = vmm
        self.items = self.vmm.items

    def set_base_graph_name(self, base_graph_name):
        self.base_graph_name = base_graph_name

    def set_available_resources(self, available_resources):
        self.available_cpu = available_resources[0]
        self.available_mem = available_resources[1]
        self.available_disk = available_resources[2]
        self.available_net = available_resources[3]

    def solve_host(self, upper_bounds):
        # Set current available resources
        self.set_available_resources(upper_bounds)
        # Check if current allocation is valid
        # import pdb; pdb.set_trace()
        return self.check_constraints(self.vmm.items)
