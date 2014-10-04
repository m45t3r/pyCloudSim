from pycloudsim.specs.power_ssj2008 import SpecParser
import os

import logging
logging.disable(logging.CRITICAL)


class TestSpecsSSJ_2008(object):
    def setUp(self):
        self.specs = SpecParser()
        # TODO: Fix hardcoded paths
        self.specs.set_directory('../power-models')
        self.specs.parse('power_ssj2008-20121031-00575.html')

    def teardown(self):
        pass

    def test_cores(self):
        assert self.specs.cores == 16

    def test_cpu_freq(self):
        assert self.specs.cpu_freq == 2300

    def test_threads(self):
        assert self.specs.threads == 32

    def test_iterator_consumption_values(self):
        self.specs.next()
        assert self.specs.curr_consumption() == 171.0
        self.specs.next()
        assert self.specs.curr_consumption() == 196.0
        self.specs.next()
        assert self.specs.curr_consumption() == 146.0
        self.specs.next()
        assert self.specs.curr_consumption() == 227.0

    def test_iterator_load_values(self):
        self.specs.next()
        assert self.specs.curr_load() == 70
        self.specs.next()
        assert self.specs.curr_load() == 80
        self.specs.next()
        assert self.specs.curr_load() == 60
        self.specs.next()
        assert self.specs.curr_load() == 90

    def test_iterator_load_ratio(self):
        self.specs.next()
        assert self.specs.curr_ratio() == 6032.0
        self.specs.next()
        assert self.specs.curr_ratio() == 6018.0
        self.specs.next()
        assert self.specs.curr_ratio() == 6008.0
        self.specs.next()
        assert self.specs.curr_ratio() == 5819.0
