"""Handles the configuration of dingle"""

import os.path
import json

class DingleError(Exception):
    """Base Exception for Dingle exceptions"""

    def __init__(self, val):
        Exception.__init__(self)
        self.value = val

    def __str__(self):
        return repr(self.value)

class MissingConfigError(DingleError):
    """Exception raised when the config file is missing."""
    pass

class MissingConfigValueError(DingleError):
    """Exception raised when a configuration value is missing."""
    pass


class DingleConfig:
    """Class representing the dingle config"""

    config = None

    @staticmethod
    def configure(config_path):
        """Returns a map of configuration values by reading in
        'config_path' and parsing the JSON it contains."""
        if not os.path.exists(config_path):
            raise MissingConfigError(config_path)
        if not DingleConfig.config:
            filejson = json.load(open(config_path, 'r'))
            DingleConfig.config = DingleConfig(filejson)
        return DingleConfig.config

    def __init__(self, config):
        """Use configure() to create DingleConfig instances. 'config'
        must be a dictionary of configuration settings."""
        self.config = config

    def get(self, key):
        """Returns the value associated with 'key' in the config"""
        if not self.config.has_key(key):
            raise MissingConfigValueError(key)
        return self.config[key]

    def missing_keys(self, keys):
        """Returns a list of keys that are in 'keys' but are missing
        from the config."""
        return [k for k in keys if not self.config.has_key(k)]
