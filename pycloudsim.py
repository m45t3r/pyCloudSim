#!/usr/bin/python
# vim:ts=4:sts=4:sw=4:et:wrap:ai:fileencoding=utf-8:
#
# Copyright 2013-2014 Albert De La Fuente
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
pyCloudSim :: A Cloud VMs placement simulator
"""
__version__ = "0.2"
__author__  = "Albert De La Fuente Vigliotti"


from pycloudsim.managers.simmanager import Simulator
from pycloudsim.managers.manager import Manager
from pycloudsim.model.physicalmachine import PhysicalMachine
from pycloudsim.specs.power_ssj2008 import SpecParser
from pycloudsim.model.tracegen import FileTraceGenerator
from pycloudsim.model.virtualmachine import VirtualMachine
import pycloudsim.common as common
import argparse
import logging
import copy
import json
import os

# Trap exceptions into an ipython shell
#import sys
#from IPython.core import ultratb
#sys.excepthook = ultratb.FormattedTB(mode='Verbose',
#                                     color_scheme='Linux', call_pdb=1)

log = logging.getLogger(__name__)

#PROF_DATA = {}
#
#def profile(fn):
#    @wraps(fn)
#    def with_profiling(*args, **kwargs):
#        start_time = time.time()
#
#        ret = fn(*args, **kwargs)
#
#        elapsed_time = time.time() - start_time
#
#        if fn.__name__ not in PROF_DATA:
#            PROF_DATA[fn.__name__] = [0, []]
#        PROF_DATA[fn.__name__][0] += 1
#        PROF_DATA[fn.__name__][1].append(elapsed_time)
#
#        return ret
#
#    return with_profiling
#
#def print_prof_data():
#    for fname, data in PROF_DATA.items():
#        max_time = max(data[1])
#        avg_time = sum(data[1]) / len(data[1])
#        print "Function %s called %d times. " % (fname, data[0]),
#        print 'Execution time max: %.3f, average: %.3f' % (max_time, avg_time)
#
#def clear_prof_data():
#    global PROF_DATA
#    PROF_DATA = {}

def host_factory(**kwargs):
    pms_list = kwargs['pms']
    result = []
    for pm in pms_list:
        pm_id = pm['id']
        pm_spec = pm['specpower']
#        result += ['host {}'.format(host)]
#        print('Creating host {}'.format(host))
        h = PhysicalMachine(pm_id)
        # FIXME: Specs could be singletons
        h.specs = SpecParser()
        # TODO: Fix hardcoded paths
        specs_directory = common.config['specs_directory']
        h.specs.set_directory(specs_directory)
        #h.specs.parse('power_ssj2008-20121031-00575.html')
        h.specs.parse(pm_spec)
        # TODO: Parse: and Net
        h.cpu_freq = h.specs.cpu_freq
        h.cores = h.specs.cores
        h.threads = h.specs.threads
        h.memory = 24*1024
        h.network = 1000
        result += [h]
        log.info('host_factory: Creating PM {}, with specs {}'.format(pm_id, pm_spec))
        #m.add_physical_host(h)
    return result

def host_callback(arg):
    pass
    #print(arg)

def vm_factory(**kwargs):
    vms_list = kwargs['vms']
    #flavor = kwargs['flavor']
    #m = kwargs['manager']
    trace_table = [[
        'planetlab-workload-traces/20110409/146-179_surfsnel_dsl_internl_net_root',
        'planetlab-workload-traces/20110420/plgmu4_ite_gmu_edu_rnp_dcc_ufjf',
        'planetlab-workload-traces/20110409/host4-plb_loria_fr_uw_oneswarm',
        'planetlab-workload-traces/20110309/planetlab1_fct_ualg_pt_root'],
                [
        'planetlab-workload-traces/20110420/plgmu4_ite_gmu_edu_rnp_dcc_ufjf',
        'planetlab-workload-traces/20110409/146-179_surfsnel_dsl_internl_net_root',
        'planetlab-workload-traces/20110409/host4-plb_loria_fr_uw_oneswarm',
        'planetlab-workload-traces/20110409/146-179_surfsnel_dsl_internl_net_root'],
                [
        'planetlab-workload-traces/20110322/planetlab1_williams_edu_uw_oneswarm',
        'planetlab-workload-traces/20110409/146-179_surfsnel_dsl_internl_net_root',
        'planetlab-workload-traces/20110409/host4-plb_loria_fr_uw_oneswarm',
        'planetlab-workload-traces/20110409/146-179_surfsnel_dsl_internl_net_root'],
                [
        'planetlab-workload-traces/20110322/planetlab1_williams_edu_uw_oneswarm',
        'planetlab-workload-traces/20110420/plgmu4_ite_gmu_edu_rnp_dcc_ufjf',
        'planetlab-workload-traces/20110322/planetlab1_williams_edu_uw_oneswarm',
        'planetlab-workload-traces/20110409/146-179_surfsnel_dsl_internl_net_root',
                ]
                ]
    result = []
    index = 0
    for vm in vms_list:
        vm_id = vm['id']
        vm_flavor = vm['flavor']
        vm_trace = vm['trace']
        vm_trace_cpu = vm_trace['cpu']
        vm_trace_mem = vm_trace['mem']
        vm_trace_disk = vm_trace['disk']
        vm_trace_net = vm_trace['net']
        working_dir = '../'
        #cpu_gen = FileTraceGenerator(working_dir + trace_table[index][0])
        #mem_gen = FileTraceGenerator(working_dir + trace_table[index][1])
        #disk_gen = FileTraceGenerator(working_dir + trace_table[index][2])
        #net_gen = FileTraceGenerator(working_dir + trace_table[index][3])
        cpu_gen = FileTraceGenerator(working_dir + vm_trace_cpu)
        mem_gen = FileTraceGenerator(working_dir + vm_trace_mem)
        disk_gen = FileTraceGenerator(working_dir + vm_trace_disk)
        net_gen = FileTraceGenerator(working_dir + vm_trace_net)
        index += 1
        vmi = VirtualMachine(vm_id, vm_flavor)#, cpu_gen, mem_gen, disk_gen, net_gen)
        #import ipdb; ipdb.set_trace() # BREAKPOINT
        vmi.set_cpu_gen(cpu_gen)
        vmi.set_mem_gen(mem_gen)
        vmi.set_disk_gen(disk_gen)
        vmi.set_net_gen(net_gen)
        result += [vmi]
        log.info('vm_factory: Creating VM {}, with flavor {}'.format(vm_id, vm_flavor))
        #m.add_virtual_machine(vmi)
#        vmi.start()
    return result

def vm_distributor_strategy_user(*kwarg, **kwargs):
    #vms_list = kwargs['vm_distributor_strategy']
    pass
#    m = kwargs['manager']

def vm_callback(arg):
    print(arg)


class pycloudsim():
    def __init__(self):
        pass

    def get_default_arg(self, default_value, arg):
        if arg is None:
            return default_value
        else:
            return arg

    def load_json(self, filename):
        json_data = open(filename)
        data = json.load(json_data)
        json_data.close()
        return data

    def parse_args(self):
        parser = argparse.ArgumentParser(description='A VM distribution/placement simulator.')
        parser.add_argument('-pm', '--pmcount', help='Number of physical machines', required=False)
        parser.add_argument('-vma', '--vmstart', help='Start number of VMs (def: 16)', required=False)
        parser.add_argument('-vmo', '--vmstop', help='Stop number of VMs (def: 304)', required=False)
        parser.add_argument('-vme', '--vmstep', help='Increment step number of VMs (def: 16)', required=False)
    #    parser.add_argument('-t', '--vmtrace', help='Full path to trace file', required=True)
        parser.add_argument('-o', '--output', help='Output path', required=True)
        parser.add_argument('-seu', '--simeu', help='Simulate Energy Unaware', required=False)
        parser.add_argument('-sksp', '--simksp', help='Simulate Iterated-KSP', required=False)
        parser.add_argument('-skspmem', '--simkspmem', help='Simulate Iterated-KSP-CPU', required=False)
        parser.add_argument('-skspnetgraph', '--simkspnetgraph', help='Simulate Iterated-KSP-Net-Graph', required=False)
        parser.add_argument('-sec', '--simec', help='Simulate Iterated-EC', required=False)
        parser.add_argument('-secnet', '--simecnet', help='Simulate Iterated-EC-Net', required=False)
        parser.add_argument('-secnetgraph', '--simecnetgraph', help='Simulate Iterated-EC-Net-Graph', required=False)
        args = parser.parse_args()

        self.pmcount = int(self.get_default_arg(72, args.pmcount))
        self.vmstart = int(self.get_default_arg(16, args.vmstart))
        self.vmstop = int(self.get_default_arg(304, args.vmstop))
        self.vmstep = int(self.get_default_arg(16, args.vmstep))
    #   self. trace_file = get_default_arg('planetlab-workload-traces/merkur_planetlab_haw-hamburg_de_yale_p4p', args.vmtrace)
        self.output_path = self.get_default_arg('results/path', args.output)
        self.simulate_eu = bool(self.get_default_arg(0, args.simeu))
        self.simulate_ksp = bool(self.get_default_arg(0, args.simksp))
        self.simulate_ksp_mem = bool(self.get_default_arg(0, args.simkspmem))
        self.simulate_ksp_net_graph = bool(self.get_default_arg(0, args.simkspnetgraph))
        self.simulate_ec = bool(self.get_default_arg(0, args.simec))
        self.simulate_ec_net = bool(self.get_default_arg(0, args.simecnet))
        self.simulate_ec_net_graph = bool(self.get_default_arg(0, args.simecnetgraph))

    def run(self):
        # TODO: Try to pull this out from the pycloudsim leve to the simulation
        # level
        import ipdb; ipdb.set_trace() # BREAKPOINT
        config = common.read_and_validate_config()
        common.config = config
        log_dir = os.path.abspath(config['log_directory'])
        common.init_logging(
            log_dir,
            'simulation.log',
            int(config['log_level']))

        self.parse_args()

        m = Manager()
        servers_json_file = common.config['servers_file']
        m.pmm.add_physical_hosts_args = self.load_json(servers_json_file)
        #m.pmm.add_physical_hosts_args = {'pms': [ \
        #    {'id': '1',
        #     'specpower': 'power_ssj2008-20121031-00575.html',
        #    }, \
        #    {'id': '2',
        #     'specpower': 'power_ssj2008-20121031-00575.html',
        #    }, \
        #]}
        m.pmm.add_physical_hosts_factory = host_factory
        m.pmm.add_physical_hosts_callback = host_callback
        m.pmm.add_physical_hosts()

        vms_json_file = common.config['vms_file']
        m.vmm.add_virtual_machines_args = self.load_json(vms_json_file)
        #m.vmm.add_virtual_machines_args = {'vms': [
        #    {'id': '1', 'flavor': 'small', 'trace': {\
        #        'cpu': 'planetlab-workload-traces/20110409/146-179_surfsnel_dsl_internl_net_root',
        #        'mem': 'planetlab-workload-traces/20110420/plgmu4_ite_gmu_edu_rnp_dcc_ufjf',
        #        'disk': 'planetlab-workload-traces/20110409/host4-plb_loria_fr_uw_oneswarm',
        #        'net': 'planetlab-workload-traces/20110309/planetlab1_fct_ualg_pt_root',
        #    }}, \
        #{'id': '2', 'flavor': 'small', 'trace': { \
        #        'cpu': 'planetlab-workload-traces/20110420/plgmu4_ite_gmu_edu_rnp_dcc_ufjf',
        #        'mem': 'planetlab-workload-traces/20110409/146-179_surfsnel_dsl_internl_net_root',
        #        'disk': 'planetlab-workload-traces/20110409/host4-plb_loria_fr_uw_oneswarm',
        #        'net': 'planetlab-workload-traces/20110409/146-179_surfsnel_dsl_internl_net_root',
        #    }}, \
        #]}
        m.vmm.add_virtual_machines_factory = vm_factory
        m.vmm.add_virtual_machines_callback = vm_callback
        m.vm_distrubutor = m.set_vm_distributor(vm_distributor_strategy_user, m)
        m.vmm.add_virtual_machines()
        #m.start()

        s = Simulator()
        pms_scenarios = [self.pmcount]
        vms_scenarios = range(self.vmstart, self.vmstop, self.vmstep)

        #pms_scenarios = range(20, 50, 10)
        #vms_scenarios = range(16, 64, 16)


        m_eu = copy.deepcopy(m)
        m_ksp = copy.deepcopy(m)
        m_ksp_mem = copy.deepcopy(m)
        m_ksp_net_graph = copy.deepcopy(m)
        m_ec = copy.deepcopy(m)
        m_ec_net = copy.deepcopy(m)
        m_ec_net_graph = copy.deepcopy(m)

        if self.simulate_eu:
            from pycloudsim.strategies.energyunaware import EnergyUnawareStrategyPlacement
            strategy = EnergyUnawareStrategyPlacement()
            log.info('=== STRATEGY START: {}'.format(strategy.__class__.__name__))
            s.simulate_strategy(strategy, m_eu, pms_scenarios, vms_scenarios)
            log.info('=== STRATEGY END: {}'.format(strategy.__class__.__name__))

        if self.simulate_ksp:
            from pycloudsim.strategies.iteratedksp import OpenOptStrategyPlacement
            strategy = OpenOptStrategyPlacement()
            log.info('=== STRATEGY START: {}'.format(strategy.__class__.__name__))
            s.simulate_strategy(strategy, m_ksp, pms_scenarios, vms_scenarios)
            log.info('=== STRATEGY END: {}'.format(strategy.__class__.__name__))

        if self.simulate_ksp_mem:
            from pycloudsim.strategies.iteratedkspmem import OpenOptStrategyPlacementMem
            strategy = OpenOptStrategyPlacementMem()
            log.info('=== STRATEGY START: {}'.format(strategy.__class__.__name__))
            s.simulate_strategy(strategy, m_ksp_mem, pms_scenarios, vms_scenarios)
            log.info('=== STRATEGY END: {}'.format(strategy.__class__.__name__))

        if self.simulate_ksp_net_graph:
            from pycloudsim.strategies.iteratedkspnetgraph import OpenOptStrategyPlacementNetGraph
            strategy = OpenOptStrategyPlacementNetGraph()
            log.info('=== STRATEGY START: {}'.format(strategy.__class__.__name__))
            s.simulate_strategy(strategy, m_ksp_net_graph, pms_scenarios, vms_scenarios)
            log.info('=== STRATEGY END: {}'.format(strategy.__class__.__name__))

        if self.simulate_ec:
            from pycloudsim.strategies.iteratedec import EvolutionaryComputationStrategyPlacement
            strategy = EvolutionaryComputationStrategyPlacement()
            log.info('=== STRATEGY START: {}'.format(strategy.__class__.__name__))
            s.simulate_strategy(strategy, m_ec, pms_scenarios, vms_scenarios)
            log.info('=== STRATEGY END: {}'.format(strategy.__class__.__name__))

        if self.simulate_ec_net:
            from pycloudsim.strategies.iteratedecnet import EvolutionaryComputationStrategyPlacementNet
            strategy = EvolutionaryComputationStrategyPlacementNet()
            log.info('=== STRATEGY START: {}'.format(strategy.__class__.__name__))
            s.simulate_strategy(strategy, m_ec_net, pms_scenarios, vms_scenarios)
            log.info('=== STRATEGY END: {}'.format(strategy.__class__.__name__))

        if self.simulate_ec_net_graph:
            from pycloudsim.strategies.iteratedecnetgraph import EvolutionaryComputationStrategyPlacementNetGraph
            strategy = EvolutionaryComputationStrategyPlacementNetGraph()
            log.info('=== STRATEGY START: {}'.format(strategy.__class__.__name__))
            s.simulate_strategy(strategy, m_ec_net_graph, pms_scenarios, vms_scenarios)
            log.info('=== STRATEGY END: {}'.format(strategy.__class__.__name__))

        print('done')

if __name__ == "__main__":
    pcs = pycloudsim()
    pcs.run()
