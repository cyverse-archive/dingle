"""Unit tests for config.py"""

import os.path
import json
from dingle import config

TEST_CFG = "test/test_config.json"

def test_configure():
    """Tests the static configure() method on DingleConfig."""

    print os.path.exists(TEST_CFG)
    print json.loads(open(TEST_CFG, 'r').read())
    cfg = config.DingleConfig.configure(TEST_CFG)
    assert cfg.missing_keys(['test1', 'test2', 'test3', 'list_of_repos']) == []
    assert cfg.missing_keys(['foo', 'bar']) == ['foo', 'bar']
    assert cfg.get('test1') == "this is a test"
    assert cfg.get('test2') == "this is a test2"
    assert cfg.get('test3') == ["hooray1", "hooray2"]
    assert cfg.get('list_of_repos') == [
        "git@github.com:iPlantCollaborativeOpenSource/Fake.git",
        "git@github.com:iPlantCollaborativeOpenSource/Fake2.git",
    ]
