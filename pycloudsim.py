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
from pycloudsim.model.phisicalmachine import PhysicalMachine
from pycloudsim.specs.power_ssj2008 import SpecParser
import argparse
import logging
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
    hostname_list = kwargs['ids']
    result = []
    for host in hostname_list:
#        result += ['host {}'.format(host)]
#        print('Creating host {}'.format(host))
        h = PhysicalMachine(host)
        # FIXME: Specs could be singletons
        h.specs = SpecParser()
        # TODO: Fix hardcoded paths
        h.specs.set_directory('/home/vagrant/research/pycloudsim-simulation/power-models')
        h.specs.parse('power_ssj2008-20121031-00575.html')
        # TODO: Parse: and Net
        h.cpu_freq = h.specs.cpu_freq
        h.cores = h.specs.cores
        h.threads = h.specs.threads
        h.mem = 24*1024
        h.net = 1000
    return result

def host_callback(arg):
    print(arg)

def vm_factory(**kwargs):
    vms_list = kwargs['ids']
    flavor = kwargs['flavor']
    m = kwargs['manager']
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
        result += ['vm {}'.format(vm)]
        log.info('Creating vm {}, with flavor {}'.format(vm, flavor))
        import os
        log.info('The current working directory is {}'.format(os.getcwd()))
        working_dir = '../'
        cpu_gen = FileTraceGenerator(working_dir + trace_table[index][0])
        mem_gen = FileTraceGenerator(working_dir + trace_table[index][1])
        disk_gen = FileTraceGenerator(working_dir + trace_table[index][2])
        net_gen = FileTraceGenerator(working_dir + trace_table[index][3])
        index += 1
        vmi = VirtualMachineThread(vm, flavor)#, cpu_gen, mem_gen, disk_gen, net_gen)
        vmi.set_cpu_gen(cpu_gen)
        vmi.set_mem_gen(mem_gen)
        vmi.set_disk_gen(disk_gen)
        vmi.set_net_gen(net_gen)
        m.add_virtual_machine(vmi)
#        vmi.start()
    return result

def vm_distributor_strategy_user(*kwarg, **kwargs):
    #vms_list = kwargs['vm_distributor_strategy']
    m = kwarg[0]
#    m = kwargs['manager']

def vm_callback(arg):
    print(arg)

def get_default_arg(default_value, arg):
    if arg is None:
        return default_value
    else:
        return arg

if __name__ == "__main__":
    # ./ pycloudsim.py -h 72 -vma 16 -vmo 304 -vme 16
    #   -t planetlab-workload-traces/merkur_planetlab_haw-hamburg_de_ yale_p4p
    #   -o results/72-bla
    # ./ simuplot.py
    parser = argparse.ArgumentParser(description='A VM distribution/placement simulator.')
    parser.add_argument('-pm', '--pmcount', help='Number of physical machines', required=False)
    parser.add_argument('-vma', '--vmstart', help='Start number of VMs (def: 16)', required=False)
    parser.add_argument('-vmo', '--vmstop', help='Stop number of VMs (def: 304)', required=False)
    parser.add_argument('-vme', '--vmstep', help='Increment step number of VMs (def: 16)', required=False)
    parser.add_argument('-t', '--vmtrace', help='Full path to trace file', required=True)
    parser.add_argument('-o', '--output', help='Output path', required=True)
    parser.add_argument('-seu', '--simeu', help='Simulate Energy Unaware', required=False)
    parser.add_argument('-sksp', '--simksp', help='Simulate Iterated-KSP', required=False)
    parser.add_argument('-skspmem', '--simkspmem', help='Simulate Iterated-KSP-CPU', required=False)
    parser.add_argument('-skspnetgraph', '--simkspnetgraph', help='Simulate Iterated-KSP-Net-Graph', required=False)
    parser.add_argument('-sec', '--simec', help='Simulate Iterated-EC', required=False)
    parser.add_argument('-secnet', '--simecnet', help='Simulate Iterated-EC-Net', required=False)
    parser.add_argument('-secnetgraph', '--simecnetgraph', help='Simulate Iterated-EC-Net-Graph', required=False)
    args = parser.parse_args()

    pmcount = int(get_default_arg(72, args.pmcount))
    vmstart = int(get_default_arg(16, args.vmstart))
    vmstop = int(get_default_arg(304, args.vmstop))
    vmstep = int(get_default_arg(16, args.vmstep))
    trace_file = get_default_arg('planetlab-workload-traces/merkur_planetlab_haw-hamburg_de_yale_p4p', args.vmtrace)
    output_path = get_default_arg('results/path', args.output)
    simulate_eu = bool(get_default_arg(0, args.simeu))
    simulate_ksp = bool(get_default_arg(0, args.simksp))
    simulate_ksp_mem = bool(get_default_arg(0, args.simkspmem))
    simulate_ksp_net_graph = bool(get_default_arg(0, args.simkspnetgraph))
    simulate_ec = bool(get_default_arg(0, args.simec))
    simulate_ec_net = bool(get_default_arg(0, args.simecnet))
    simulate_ec_net_graph = bool(get_default_arg(0, args.simecnetgraph))

    m = Manager()
    m.add_physical_hosts_factory = host_factory
    m.add_physical_hosts_args = {'ids': ['h1', 'h2', 'h3', 'h4']}
    m.add_physical_hosts_callback = host_callback

    m.add_physical_hosts()

    m.add_virtual_machines_factory = vm_factory
    m.add_virtual_machines_args = {'ids': ['vm1', 'vm2', 'vm3', 'vm4'], 'flavor': 'small', 'manager': m}
    m.add_virtual_machines_callback = vm_callback
    m.vm_distrubutor = m.set_vm_distributor(vm_distributor_strategy_user, m)
    m.add_virtual_machines()
    m.start()

    import ipdb; ipdb.set_trace() # BREAKPOINT
    s = Simulator()

    pms_scenarios = [pmcount]
    vms_scenarios = range(vmstart, vmstop, vmstep)

    #pms_scenarios = range(20, 50, 10)
    #vms_scenarios = range(16, 64, 16)

    if simulate_eu:
        from pycloudsim.strategies.energyunaware import EnergyUnawareStrategyPlacement
        strategy = EnergyUnawareStrategyPlacement()
        s.simulate_strategy(strategy, trace_file, pms_scenarios, vms_scenarios)

    if simulate_ksp:
        from pycloudsim.strategies.iteratedksp import OpenOptStrategyPlacement
        strategy = OpenOptStrategyPlacement()
        s.simulate_strategy(strategy, trace_file, pms_scenarios, vms_scenarios)

    if simulate_ksp_mem:
        from pycloudsim.strategies.iteratedkspmem import OpenOptStrategyPlacementMem
        strategy = OpenOptStrategyPlacementMem()
        s.simulate_strategy(strategy, trace_file, pms_scenarios, vms_scenarios)

    if simulate_ksp_net_graph:
        from pycloudsim.strategies.iteratedkspnetgraph import OpenOptStrategyPlacementNetGraph
        strategy = OpenOptStrategyPlacementNetGraph()
        s.simulate_strategy(strategy, trace_file, pms_scenarios, vms_scenarios)

    if simulate_ec:
        from pycloudsim.strategies.iteratedec import EvolutionaryComputationStrategyPlacement
        strategy = EvolutionaryComputationStrategyPlacement()
        s.simulate_strategy(strategy, trace_file, pms_scenarios, vms_scenarios)

    if simulate_ec_net:
        from pycloudsim.strategies.iteratedecnet import EvolutionaryComputationStrategyPlacementNet
        strategy = EvolutionaryComputationStrategyPlacementNet()
        s.simulate_strategy(strategy, trace_file, pms_scenarios, vms_scenarios)

    if simulate_ec_net_graph:
        from pycloudsim.strategies.iteratedecnetgraph import EvolutionaryComputationStrategyPlacementNetGraph
        strategy = EvolutionaryComputationStrategyPlacementNetGraph()
        s.simulate_strategy(strategy, trace_file, pms_scenarios, vms_scenarios)

    print('done')
