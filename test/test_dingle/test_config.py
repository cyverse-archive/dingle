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
    #assert cfg.missing_keys(['test1', 'test2', 'test3', 'list_of_repos']) == []
    #assert cfg.missing_keys(['foo', 'bar']) == ['foo', 'bar']
    assert cfg.get('test1') == "this is a test"
    assert cfg.get('test2') == "this is a test2"
    assert cfg.get('test3') == ["hooray1", "hooray2"]
    assert cfg.get('list_of_repos') == [
        "git@github.com:iPlantCollaborativeOpenSource/Nibblonian.git",
        "git@github.com:iPlantCollaborativeOpenSource/NotificationAgent.git",
        "git@github.com:iPlantCollaborativeOpenSource/Clavin.git",
        "git@github.com:iPlantCollaborativeOpenSource/CAS-Extensions.git",
        "git@github.com:iPlantCollaborativeOpenSource/iplant-buggalo.git",
        "git@github.com:iPlantCollaborativeOpenSource/de-database-schema.git",
        "git@github.com:iPlantCollaborativeOpenSource/kameleon.git",
        "git@github.com:iPlantCollaborativeOpenSource/facepalm.git",
        "git@github.com:iPlantCollaborativeOpenSource/OSM.git",
        "git@github.com:iPlantCollaborativeOpenSource/metadactyl.git",
        "git@github.com:iPlantCollaborativeOpenSource/metadactyl-clj.git",
        "git@github.com:iPlantCollaborativeOpenSource/iplant-email.git",
        "git@github.com:iPlantCollaborativeOpenSource/JEX.git",
        "git@github.com:iPlantCollaborativeOpenSource/Panopticon.git",
        "git@github.com:iPlantCollaborativeOpenSource/filetool.git",
        "git@github.com:iPlantCollaborativeOpenSource/Scruffian.git",
        "git@github.com:iPlantCollaborativeOpenSource/Donkey.git",
        "git@github.com:iPlantCollaborativeOpenSource/Conrad.git",
        "git@github.com:iPlantCollaborativeOpenSource/buggalo.git",
        "git@github.com:iPlantCollaborativeOpenSource/kifshare.git",
        "git@github.com:iPlantCollaborativeOpenSource/clockwork.git"
    ]
