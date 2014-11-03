from pmmanager import PMManager
from vmmanager import VMManager
from pycloudsim.strategies.energyunaware import EnergyUnawareStrategyPlacement
from pycloudsim.strategies.mbfd import ModifiedBestFitDecreasingPlacement
from pycloudsim.common import log
import pycloudsim.common as common
import copy
import operator
import logging
log = logging.getLogger(__name__)

class Manager:
    def __init__(self):
        self.placement = []
        self.pmm = PMManager()
        self.strategy = None
        self.vmm = VMManager()
        self.pmm_copy = None
        self.vmm_copy = None

    def set_vm_distributor(self, algorithm, manager):
        algorithm(manager)

    def set_strategy(self, strategy):
        self.strategy = strategy
        #if self.base_graph_name:
        #    self.strategy.set_base_graph_name(self.base_graph_name)
        self.strategy.set_vmm(self.vmm)
        self.strategy.pmm = self.pmm

    def place_vms(self, vms, host):
        i = 0
        while i < len(vms):
            vm = vms[i]
            host.place_vm(vm)
            print('{}'.format(host))
            resources = vm.resources_to_list()
            power = host.estimate_consumed_power()
            log.info('  + VM {} resources: {} (power: {})'.format(vm, resources, power))
            i += 1
        self.vmm.items_remove(vms)

    def placed_vms(self):
        result = 0
        for host in self.pmm.items:
            result += len(host.vms)
        return result

    def unplaced_vms(self):
        return self.vmm.total_vm - self.placed_vms()

    def solve_hosts(self):
        number_pms = self.pmm.total_pm
        number_vms = self.vmm.total_vm
        pms_list = self.pmm.items
        vms_list = self.vmm.items
        del pms_list[number_pms:]
        del vms_list[number_vms:]

        # MBFD is completely different to other methods, since it iterates
        # first in VMs
        if isinstance(self.strategy, ModifiedBestFitDecreasingPlacement):
            for host in self.pmm.items:
                host.suspend()

            # Sort in decreasing order of CPU utilization
            vms_list = sorted(self.vmm.items, key=operator.itemgetter('cpu'), reverse=True)
            # import pdb; pdb.set_trace() # BREAKPOINT
            for vm in vms_list:
                self.vmm.items = [vm]
                log.info('--- Placing VM {}'.format(vm))
                min_power = float('inf')
                allocated_host = None
                vms = None

                for host in self.pmm.items:
                    available_resources = host.available_resources()
                    compute_resources = available_resources
                    log.info('Host {} available resources: {}'.format(host, available_resources))
                    if self.strategy.solve_host(compute_resources):
                        is_suspended = host.suspended
                        if is_suspended:
                            host.wol()
                        host.place_vm(vm)
                        #power = host.estimate_consumed_power()
                        power = self.calculate_power_consumed()
                        log.info('Calculated power on host {}: {}'.format(host, power))
                        host.remove_vm(vm)
                        if is_suspended:
                            host.suspend()
                        if power < min_power:
                            log.info('New minimal allocation found on host {}'.format(host))
                            allocated_host = host
                            min_power = power
                            
                if allocated_host is not None:
                    log.info('Allocating {} on host {}'.format(vm, allocated_host))
                    if allocated_host.suspended:
                        log.info('Wake-on-Lan host {}'.format(allocated_host))
                        allocated_host.wol()
                    allocated_host.place_vm(vm)
                    available_resources = allocated_host.available_resources()
                    log.info('Host available resources after placement: {}'.format(available_resources))

            # Suspend idle PMs
            for host in self.pmm.items:
                if host.vms == []:
                    log.info('Suspending host {}'.format(host))
                    host.suspend()


        else:
            for host in self.pmm.items:
                log.info('--- Placing VMS on host {}'.format(host))
                if self.vmm.items != []:
                    available_resources = host.available_resources()
                    compute_resources = available_resources
                    log.info('Host available resources: {}'.format(available_resources))
                    linear_method = common.config['non_linear'].lower() == 'false'
                    skip = False
                    if linear_method:
                        log.info('LINEAR MODEL OPTIMIZATION (maximizing VMs per host):')
                    else:
                        non_linear_optimum = int(common.config['non_linear_optimum'])
                        log.info('NON LINEAR MODEL OPTIMIZATION:')
                        for index in range(0, non_linear_optimum):
    #                        import ipdb; ipdb.set_trace() # BREAKPOINT
                            optimal_cpu = host.specs.optimal_load().next()['load']
                            if index is not non_linear_optimum - 1:
                                log.info('Skiping optimum {}'.format(optimal_cpu))
    #                    optimal_cpu = host.specs.optimal_load().next()['load']
    #                    optimal_cpu = host.specs.optimal_load().next()['load']
    #                    optimal_cpu = host.specs.optimal_load().next()['load']
    #                    optimal_cpu = host.specs.optimal_load().next()['load']
                        skip = host.cpu >= optimal_cpu
                        if not skip:
                            compute_resources[0] = optimal_cpu
                            log.info('Optimal CPU value is: {}'.format(optimal_cpu))
                            log.info('Current CPU value is: {}'.format(host.cpu))
                            log.info('Setting up computing resources to: {}'.format(compute_resources))
                        else:
                            log.info('CPU threshold bigger than optimal, skipping this host')

                    if not skip:
                        solution = self.strategy.solve_host(compute_resources)
                        vms = self.strategy.get_vm_objects(solution)
                        if vms is not None:
                            self.place_vms(vms, host)
                            available_resources = host.available_resources()
                            log.info('Host available resources after placement: {}'.format(available_resources))
                else:
                    if not isinstance(self.strategy, EnergyUnawareStrategyPlacement):
                        host.suspend()
                        log.info('Suspending host: {}'.format(host))
                    #print(host)


    def calculate_power_consumed(self):
        result = 0
        for host in self.pmm.items:
            result += host.estimate_consumed_power()
        return result

    def calculate_physical_hosts_used(self):
        result = 0
        for host in self.pmm.items:
            if host.vms != []:
                result += 1
        return result

    def calculate_physical_hosts_suspended(self):
        result = 0
        for host in self.pmm.items:
            if host.suspended:
                result += 1
        return result

    def calculate_physical_hosts_idle(self):
        result = 0
        for host in self.pmm.items:
            if host.vms == [] and not host.suspended:
                result += 1
        return result

    def copy(self):
        self.pmm_copy = copy.deepcopy(self.pmm)
        self.vmm_copy = copy.deepcopy(self.vmm)

    def reset(self):
        self.pmm = copy.deepcopy(self.pmm_copy)
        self.vmm = copy.deepcopy(self.vmm_copy)

#    def add_physical_host(self, host):
#        log.info('add_physical_host {}'.format(host))
#        self.total_pm += 1
#        #print('add_physical_host: {}'.format(host))
#
#    def add_physical_hosts(self, host=None):
#        if self.add_physical_hosts_factory:
#            result = self.add_physical_hosts_factory(
#                **self.add_physical_hosts_args)
#            for host in result:
#                self.add_physical_host(host)
#                if self.add_physical_hosts_callback:
#                    self.add_physical_hosts_callback(host)
#        else:
#            self.add_physical_host(host)

#    def add_virtual_machine(self, vm):
#        self.vmm.add_virtual_machine(vm)
#        self.vm_list += [vm]
#        self.total_vm += 1
#        #import ipdb; ipdb.set_trace() # BREAKPOINT
#        log.info('add_virtual_machine {}'.format(vm))
#        #print('add_virtual_machine: {}'.format(vm))

#    def add_virtual_machines(self, vm=None):
#        self.vmm.add_virtual_machines(vm)
#        if self.add_virtual_machines_factory:
#            result = self.add_virtual_machines_factory(
#                **self.add_virtual_machines_args)
#            for vm in result:
#                self.add_virtual_machine(vm)
#                if self.add_virtual_machines_callback:
#                    self.add_virtual_machines_callback(vm)
#        else:
#            import ipdb; ipdb.set_trace() # BREAKPOINT
#            self.add_virtual_machines(vm)
