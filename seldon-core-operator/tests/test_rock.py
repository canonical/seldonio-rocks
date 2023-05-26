# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Checks out charm repository into `charm_repo`. Updated metadata.yaml with reference to locally
# built ROCK. Executes integration tests.
#

from pathlib import Path

import os
import logging
import pytest
import subprocess
import yaml
from pytest_operator.plugin import OpsTest

def read_rock_info():
    ROCKCRAFT = yaml.safe_load(Path("rockcraft.yaml").read_text())
    name = ROCKCRAFT["name"]
    version = ROCKCRAFT["version"]
    arch = list(ROCKCRAFT["platforms"].keys())[0]
    return f"{name}_{version}_{arch}:{version}"

@pytest.mark.abort_on_fail
def test_rock(ops_test: OpsTest):
    """Test rock."""
    LOCAL_ROCK_IMAGE = read_rock_info()

    # cleanup previous artifacts, if any
    subprocess.run(["docker", "rm", "rockfs"])
    subprocess.run(["rm", "-rf", "./rockfs"])
    subprocess.run(["rm", "-rf", "./rockfs.tar"])

    # create ROCK filesystem
    subprocess.run(["docker", "create", "--name=rockfs", f"{LOCAL_ROCK_IMAGE}"])
    subprocess.run(["docker", "export", "rockfs", "--output", "./rockfs.tar"])
    subprocess.run(["mkdir", "./rockfs"])
    subprocess.run(["tar", "xvf", "./rockfs.tar", "-C", "rockfs"])

    # verify that all artifacts are in correct locations
    files = os.listdir('./rockfs/opt/seldon-core-operator/')
    assert "manager" in files

    files = os.listdir('./rockfs//tmp/operator-resources/')
    assert "service.yaml" in files
    assert "configmap.yaml" in files
    assert "validate.yaml" in files
    assert "crd-v1.yaml" in files

    # cleanup
    subprocess.run(["docker", "rm", "rockfs"])
    subprocess.run(["rm", "-rf", "./rockfs"])
    subprocess.run(["rm", "-rf", "./rockfs.tar"])