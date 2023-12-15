# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Tests for required artifacts to be present in the ROCK image.
#

from charmed_kubeflow_chisme.rock import CheckRock
from pathlib import Path

import os
import logging
import random
import pytest
import string
import subprocess
import yaml

@pytest.fixture()
def rock_test_env(tmpdir):
    """Yields a temporary directory and random docker container name, then cleans them up after."""
    container_name = "".join([str(i) for i in random.choices(string.ascii_lowercase, k=8)])
    yield tmpdir, container_name

    try:
        subprocess.run(["docker", "rm", container_name])
    except Exception:
        pass

@pytest.mark.abort_on_fail
def test_rock(rock_test_env):
    """Test rock."""
    temp_dir, container_name = rock_test_env
    check_rock = CheckRock("rockcraft.yaml")
    rock_image = check_rock.get_name()
    rock_version = check_rock.get_version()
    LOCAL_ROCK_IMAGE = f"{rock_image}:{rock_version}"

    # verify that all artifacts are in correct locations
    subprocess.run(["docker", "run", LOCAL_ROCK_IMAGE, "exec", "ls", "-la", "/microservice/SKLearnServer.py"], check=True)

    # verify that rockcraft.yaml contains correct image name for PREDICTIVE_UNIT_IMAGE environment variable
    #assert CheckRock.get_environment()["PREDICTIVE_UNIT_IMAGE"].contains(LOCAL_ROCK_IMAGE)
