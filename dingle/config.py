"""Handles the configuration of dingle"""

import os.path
import json
import types
from dingle.utils import err_exit

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
            DingleConfig.config = DingleConfig(filejson, config_path)
        return DingleConfig.config

    def __init__(self, config, path):
        """Use configure() to create DingleConfig instances. 'config'
        must be a dictionary of configuration settings."""
        self.config = config
        self.path = path

    def get(self, key):
        """Returns the value associated with 'key' in the config"""
        if not self.config.has_key(key):
            raise MissingConfigValueError(key)
        return self.config[key]

    def missing_keys(self, keys):
        """Returns a list of keys that are in 'keys' but are missing
        from the config."""
        return [k for k in keys if not self.config.has_key(k)]

    def _validate_keys(self, keys):
        """Validates the keys in 'cfg'."""
        missing_cfgs = self.missing_keys(keys)
        if missing_cfgs:
            err_str = "%s is missing the following settings:" % self.path
            for missing_cfg in missing_cfgs:
                err_str = err_str + "\t%s\n" % missing_cfg
            err_exit(err_str)

    def _validate_types(self, typemap):
        """Validates the types of the values in 'cfg'"""
        err_tmpl = "%s is of type %s and should be of type %s in %s.\n"
        err_str = ""
        for cfg_key, cfg_type in typemap.iteritems():
            if not type(self.get(cfg_key)) is cfg_type:
                err_str = err_str + err_tmpl % \
                    (cfg_key, type(self.get(cfg_key)), cfg_type, self.path)
        if err_str:
            err_exit(err_str)

    def validate_config(self):
        """Validates the already parsed config file 'cfg'."""
        required_configs = {
            "staging_dir" : types.UnicodeType,
            "yum_repo_host" : types.UnicodeType,
            "yum_dev_dir" : types.UnicodeType,
            "yum_qa_dir" : types.UnicodeType,
            "yum_stage_dir" : types.UnicodeType,
            "yum_prod_dir" : types.UnicodeType,
            "rpm_names" : types.ListType,
            "prereq_repos" : types.ListType,
            "list_of_repos" : types.ListType
        }
        self._validate_keys(required_configs.keys())
        self._validate_types(required_configs)
