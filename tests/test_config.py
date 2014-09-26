import pycloudsim.config as config

import logging
logging.disable(logging.CRITICAL)


class TestConfig(object):
    def test_read_default_config(self):
        paths = [config.DEFAULT_CONFIG_PATH]
        print paths
        test_config = config.read_config(paths)
        assert config.validate_config(test_config, config.REQUIRED_FIELDS)
