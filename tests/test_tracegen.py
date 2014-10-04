from pycloudsim.model.tracegen import *
import os

import logging
logging.disable(logging.CRITICAL)


class TestTraceGen(object):
    def setUp(self):
        pass
    def teardown(self):
        pass

    def test_file_based_trace_generator_first_5(self):
        assert True
        #t = FileTraceGenerator('../../planetlab-workload-traces/20110303/vn5_cse_wustl_edu_uw_oneswarm')
        #values = [t.next(), t.next(), t.next(), t.next(), t.next()]
        #assert values == [15, 11, 4, 11, 12]

    def test_file_based_trace_generator_exception(self):
        pass

    def test_file_based_trace_generator_reversed(self):
        pass
        #t = FileTraceGenerator('../../planetlab-workload-traces/20110303/vn5_cse_wustl_edu_uw_oneswarm')
        #t.set_reverse()
        #values = [t.next() for i in range(1, 288)]
        #values = [t.next(), t.next(), t.next(), t.next(), t.next()]
        #assert values == [15, 11, 4, 11, 12]

    def test_file_based_trace_generator_cyclic(self):
        pass
