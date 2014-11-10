from pmmanager import PMManager
from vmmanager import VMManager
from pycloudsim.strategies.energyunaware import EnergyUnawareStrategyPlacement
from pycloudsim.strategies.mbfd import ModifiedBestFitDecreasingPlacement
from pycloudsim.strategies.mbfd2 import ModifiedBestFitDecreasing2Placement
from pycloudsim.strategies.ffd import FirstFitDecreasingPlacement
from pycloudsim.strategies.iteratedec import EvolutionaryComputationStrategyPlacement
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

        # MBFD is completely different to other methods
        if (isinstance(self.strategy, ModifiedBestFitDecreasingPlacement) or 
            isinstance(self.strategy, ModifiedBestFitDecreasing2Placement) or
            isinstance(self.strategy, FirstFitDecreasingPlacement)):
            
            for host in self.pmm.items:
                host.suspend()

            # Need to create a separate copy or the results are wrong, don't know why
            host_list = copy.deepcopy(self.pmm.items)
            # Sort in decreasing order of CPU utilization
            vms_list = sorted(self.vmm.items, key=operator.itemgetter('cpu'), reverse=True)
            log.info('*** MBFD simulation with {} VMs'.format(len(vms_list)))
            for vm in vms_list:
                log.info('--- Placing VM {}'.format(vm))
                log.info('VM requested resources: {}'.format(vm.resources_to_list()))
                min_power = float('inf')
                allocated_host = None

                for host in host_list:
                    available_resources = host.available_resources()
                    compute_resources = available_resources
                    if self.strategy.solve_host(compute_resources, vm):
                        log.info('Host {} available resources: {}'.format(host, available_resources))
                        if isinstance(self.strategy, FirstFitDecreasingPlacement):
                            allocated_host = host
                            break
                        else:
                            is_suspended = host.suspended
                            if is_suspended:
                                host.wol()
                            host.place_vm(vm)
                            # The original MBFD evaluate the power consumption in each host
                            if isinstance(self.strategy, ModifiedBestFitDecreasingPlacement):
                                power = host.estimate_consumed_power()
                            # While the modified MBFD evaluate the global power consumption
                            else:
                                power = self.calculate_power_consumed(host_list)
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
                    # Get allocated_host index so we can add it in the self.pmm.items
                    i = host_list.index(allocated_host)
                    # Checking if allocated_host is suspended, so we can wake up it
                    if allocated_host.suspended:
                        log.info('Wake-on-Lan host {}'.format(self.pmm.items[i]))
                        # Need to wake-up both the host in host_list and self.pmm.items
                        allocated_host.wol()
                        self.pmm.items[i].wol()
                    # Same thing to allocation
                    allocated_host.place_vm(vm)
                    self.place_vms([vm], self.pmm.items[i])
                    # We can get this information from either place, doesn't matter
                    available_resources = allocated_host.available_resources()
                    log.info('Host available resources after placement: {}'.format(available_resources))
                    log.info('Placed VMs: {}'.format(self.placed_vms()))

            # Suspend idle PMs
            for host in self.pmm.items:
                if host.vms == []:
                    log.info('Suspending host {}'.format(host))
                    host.suspend()
        
        # End of MBFD family of algorithms
        else:
            linear_method = common.config['non_linear'].lower() == 'false'
            for host in self.pmm.items:
                #if number_pms == 100 and number_vms == 64 and host.id == '64':
    #            if number_pms == 100 and number_vms == 64:
    #            if isinstance(self.strategy, EvolutionaryComputationStrategyPlacement):
    #                import ipdb; ipdb.set_trace() # BREAKPOINT
                log.info('--- Placing VMS on host {}'.format(host))
                if self.vmm.items != []:
                    available_resources = host.available_resources()
                    compute_resources = available_resources
                    log.info('Host available resources: {}'.format(available_resources))
                    skip = False
                    if linear_method:
                        log.info('LINEAR MODEL OPTIMIZATION (maximizing VMs per host):')
                    else:
                        non_linear_optimum = int(common.config['non_linear_optimum'])
                        log.info('NON LINEAR MODEL OPTIMIZATION:')
                        for index in range(0, non_linear_optimum):
                            optimal_cpu = host.specs.optimal_load().next()['load']
                            if index is not non_linear_optimum - 1:
                                log.info('Skiping optimum {}'.format(optimal_cpu))
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
                        if vms != []:
                            self.place_vms(vms, host)
                            available_resources = host.available_resources()
                            log.info('Host available resources after placement: {}'.format(available_resources))
                        else:
                            if not isinstance(self.strategy, EnergyUnawareStrategyPlacement):
                                # Special case when there are still VMs but the CPU
                                # usage is higher than the otimal_cpu value to be used,
                                # we allocate the rest
                                # This is not elegant, me no like this =(. This method
                                # needs refactoring!!!
                                log.info('Special case, there are still: {} VMs'.format(len(self.vmm.items)))
                                log.info('  CPU of VM[0]: {}'.format(self.vmm.items[0].value['cpu']))
                                compute_resources[0] = 100
                                log.info('  Incrementing computing resources to: {}'.format(compute_resources))
                                solution = self.strategy.solve_host(compute_resources)
                                vms = self.strategy.get_vm_objects(solution)
                                self.place_vms(vms, host)
                                available_resources = host.available_resources()
                                log.info('Host available resources after placement: {}'.format(available_resources))
                else:
                    if not isinstance(self.strategy, EnergyUnawareStrategyPlacement):
                        host.suspend()
                        log.info('Suspending host: {}'.format(host))

    def calculate_power_consumed(self, host_list = None):
        if not host_list:
            host_list = self.pmm.items
        result = 0
        for host in host_list:
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
