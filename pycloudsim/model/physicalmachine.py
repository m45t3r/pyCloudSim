class PhysicalMachine:
    __count__ = 0
    def __init__(self, id):
        self.id = '%s' % id # self.__count__
        self.vms = []
        self.specs = None
        self.startup_machine()
        PhysicalMachine.__count__ += 1

    def startup_machine(self):
        self.cpu = 0
        self.mem = 0
        self.disk = 0
        self.net = 0
        self.suspended = False

    def consumed_power(self):
        pass

    def place_vm(self, vm):
        self.vms.append(vm)
        vm.value['placed'] = 1
#        self.cpu = self.mem = 0
#        self.disk = self.net = 0
#        for vm in self.vms:
        self.cpu += vm.value['cpu']
        self.mem += vm.value['mem']
        self.disk += vm.value['disk']
        self.net += vm.value['net']

    def remove_vm(self, vm):
        self.vms.remove(vm)
        vm.value['placed'] = 0
#        self.cpu = self.mem = 0
#        self.disk = self.net = 0
#        for vm in self.vms:
        self.cpu -= vm.value['cpu']
        self.mem -= vm.value['mem']
        self.disk -= vm.value['disk']
        self.net -= vm.value['net']


    def available_resources(self):
        return [
            100 - self.cpu,
            100 - self.mem,
            100 - self.disk,
            100 - self.net,
        ]

    def vms_to_str(self):
        result = ''
        for vm in self.vms:
            result += str(vm) + ', '
        return result

    def to_full_string(self):
        if self.suspended:
            state = 'sus'
        else:
            state = 'run'
        result = 'PM[{}-{}/{}]({}, {}, {}, {}) | [{}/{}]'.format(
            self.id,
            state,
            self.estimate_consumed_power(),
            self.cpu,
            self.mem,
            self.disk,
            self.net,
            len(self.vms),
            self.vms_to_str())
        return result

    def __str__(self):
        result = 'PM{}'.format(
            self.id,
            )
        return result

    def suspend(self):
        self.suspended = True
        self.cpu = 0
        self.mem = 0
        self.disk = 0
        self.net = 0

    def wol(self):
        self.startup_machine()

    def estimate_used_cpu(self):
        # Less than 10% => Idle
        result = 5
        if len(self.vms) is not 0:
            result = 0
            for vm in self.vms:
                result += vm['cpu']
        return result

    def estimate_consumed_power(self):
        result = 0
        if self.suspended:
            result = 5
        else:
            if self.specs is None:
                # P(cpu) = P_idle + (P_busy - P_idle) x cpu
                p_idle = 114.0
                p_busy = 250.0
                result = p_idle + (p_busy - p_idle) * self.cpu/100
                #if self.vms != []:
                #    p_idle = 114.0
                #    p_busy = 250.0
                #    result = p_idle + (p_busy - p_idle) * self.cpu/100
                #else:
                #    pass
            else:
                cpu = self.estimate_used_cpu()
                if cpu < 10:
                    # Idle consumption, when no VMs
                    result = self.specs.specs_by_load[0]['consumption']
                else:
                    cpu_tens = int(str(cpu)[-1])
                    cpu_without_tens = int(str(cpu)[:-1])
                    bottom_cpu = cpu_without_tens * 10
                    bottom_consumption = self.specs.specs_by_load[bottom_cpu]['consumption']
                    top_cpu = cpu_without_tens * 10 + 10
                    if top_cpu < 110:
                        top_consumption = self.specs.specs_by_load[top_cpu]['consumption']
                        result = bottom_consumption + \
                                (top_consumption - bottom_consumption) / 10 * cpu_tens
                    else:
                        result = bottom_consumption
        return result
