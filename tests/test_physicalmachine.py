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

    def test_place_one_VM(self):
        self.setUp()
        vm1 = VirtualMachine('0', 'small')
        vm1.value['cpu'] = 10
        vm1.value['mem'] = 20
        vm1.value['disk'] = 30
        vm1.value['net'] = 40
        self.h.place_vm(vm1)
        assert self.h.cpu == 10
        assert self.h.mem == 20
        assert self.h.disk == 30
        assert self.h.net == 40

    def test_power_one_VM(self):
        self.setUp()
        vm1 = VirtualMachine('0', 'small')
        vm1.value['cpu'] = 20
        self.h.vms.append(vm1)
        assert self.h.estimate_consumed_power() == 89.6

    def test_power_two_VMs(self):
        self.setUp()
        vm1 = VirtualMachine('0', 'small')
        vm1.value['cpu'] = 20
        vm2 = VirtualMachine('1', 'small')
        vm2.value['cpu'] = 10
        self.h.vms.append(vm1)
        self.h.vms.append(vm2)
        assert self.h.estimate_consumed_power() == 100

    def test_power_100_percent(self):
        self.setUp()
        vm1 = VirtualMachine('0', 'small')
        vm1.value['cpu'] = 100
        self.h.vms.append(vm1)
        assert self.h.estimate_consumed_power() == 269

    def test_available_resources(self):
        self.setUp()
        vm1 = VirtualMachine('0', 'small')
        vm1.value['cpu'] = 10
        vm1.value['mem'] = 20
        vm1.value['disk'] = 30
        vm1.value['net'] = 40
        self.h.place_vm(vm1)
        vm2 = VirtualMachine('1', 'small')
        vm2.value['cpu'] = 10
        vm2.value['mem'] = 20
        vm2.value['disk'] = 30
        vm2.value['net'] = 40
        self.h.place_vm(vm2)
        ar = self.h.available_resources()
        assert ar == [80, 60, 40, 20]
