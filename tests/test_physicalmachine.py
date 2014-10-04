from pycloudsim.model.physicalmachine import PhysicalMachine
from pycloudsim.model.virtualmachine import VirtualMachine
from pycloudsim.specs.power_ssj2008 import SpecParser
import os

import logging
logging.disable(logging.CRITICAL)


class TestPhysicalMachine(object):
    def setUp(self):
        self.h = PhysicalMachine('0')
        self.h.specs = SpecParser()
        self.h.specs.set_directory('../power-models')
        self.h.specs.parse('power_ssj2008-20121031-00575.html')

    def teardown(self):
        pass

    def test_cpu_idle(self):
        assert self.h.estimate_used_cpu() < 10

    def test_power_idle(self):
        assert self.h.estimate_consumed_power() == 58.1

    def test_power_one_VM(self):
        vm1 = VirtualMachine('0', 'small')
        vm1.value['cpu'] = 20
        self.h.vms.append(vm1)
        assert self.h.estimate_consumed_power() == 89.6

    def test_power_two_VMs(self):
        vm1 = VirtualMachine('0', 'small')
        vm1.value['cpu'] = 20
        vm2 = VirtualMachine('1', 'small')
        vm2.value['cpu'] = 10
        self.h.vms.append(vm1)
        self.h.vms.append(vm2)
        assert self.h.estimate_consumed_power() == 100
