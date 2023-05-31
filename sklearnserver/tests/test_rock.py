# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Tests for required artifacts to be present in the ROCK image.
#

from pathlib import Path

import os
import logging
import random
import pytest
import string
import subprocess
import yaml
from pytest_operator.plugin import OpsTest

def read_rock_info():
    ROCKCRAFT = yaml.safe_load(Path("rockcraft.yaml").read_text())
    name = ROCKCRAFT["name"]
    version = ROCKCRAFT["version"]
    arch = list(ROCKCRAFT["platforms"].keys())[0]
    return f"{name}_{version}_{arch}:{version}"

@pytest.fixture()
def rock_test_env():
    """Yields a temporary directory and random docker container name, then cleans them up after."""
    container_name = "".join([str(i) for i in random.choices(string.ascii_lowercase, k=8)])
    yield container_name

    try:
        subprocess.run(["docker", "rm", container_name])
    except Exception:
        pass

@pytest.mark.abort_on_fail
def test_rock(ops_test: OpsTest, rock_test_env):
    """Test rock."""
    container_name = rock_test_env
    LOCAL_ROCK_IMAGE = read_rock_info()

    # verify that all artifacts are in correct locations
    subprocess.run(["docker", "run", LOCAL_ROCK_IMAGE, "exec", "ls", "-la", "/microservice/SKLearnServer.py"], check=True)
