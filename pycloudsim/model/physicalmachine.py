class PhysicalMachine:
    __count__ = 0
    def __init__(self, id):
        self.id = '%s' % id # self.__count__
        self.vms = []
        self.startup_machine()
        self.specs = None
        PhysicalMachine.__count__ += 1

    def startup_machine(self):
        self.cpu = 15
        self.mem = 15
        self.disk = self.net = 0
        self.suspended = False

    def consumed_power(self):
        pass

    def place_vm(self, vm):
        self.vms.append(vm)
        vm.value['placed'] = 1
        self.cpu = self.mem = 0
        self.disk = self.net = 0
        for vm in self.vms:
            self.cpu += vm.value['cpu']
            self.mem += vm.value['mem']
            self.disk += vm.value['disk']
            self.net += vm.value['net']

    def vms_to_str(self):
        result = ''
        for vm in self.vms:
            result += str(vm) + ', '
        return result

    def __str__(self):
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

    def suspend(self):
        self.suspended = True
        self.cpu = 0
        self.mem = 0
        self.disk = 0
        self.net = 0

    def wol(self):
        self.startup_machine()

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
                cpu = self.vms[0]['cpu']
                cpu_tens = int(str(cpu)[-1])
                cpu_without_tens = int(str(cpu)[:-1])
                bottom_cpu = cpu_without_tens * 10
                bottom_consumption = self.specs.specs_by_load[bottom_cpu]['consumption']
                top_cpu = cpu_without_tens * 10 + 10
                top_consumption = self.specs.specs_by_load[top_cpu]['consumption']
                result = bottom_consumption + \
                        (top_consumption - bottom_consumption) / 10 * cpu_tens
        return result
