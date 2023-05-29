# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Checks out charm repository into `charm_repo`. Updated metadata.yaml with reference to locally
# built ROCK. Executes integration tests.
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
def rock_test_env(tmpdir):
    """Yields a temporary directory and random docker container name, then cleans them up after."""
    container_name = "".join([str(i) for i in random.choices(string.ascii_lowercase, k=8)])
    yield tmpdir, container_name

    try:
        subprocess.run(["docker", "rm", container_name])
    except Exception:
        pass
    # tmpdir fixture we use here should clean up the other files for us

@pytest.mark.abort_on_fail
def test_rock(ops_test: OpsTest, rock_test_env):
    """Test rock."""
    temp_dir, container_name = rock_test_env
    LOCAL_ROCK_IMAGE = read_rock_info()

    rockfs_tar = temp_dir.join("rockfs.tar")
    rockfs_dir = temp_dir.mkdir("rockfs")

    # create ROCK filesystem
    subprocess.run(["docker", "create", f"--name={container_name}", f"{LOCAL_ROCK_IMAGE}"])
    subprocess.run(["docker", "export", f"{container_name}", "--output", rockfs_tar], check=True)
    subprocess.run(["tar", "xvf", rockfs_tar, "-C", rockfs_dir], check=True)

    # verify that all artifacts are in correct locations
    files = os.listdir(f"{rockfs_dir}/opt/seldon-core-operator/")
    assert "manager" in files

    files = os.listdir(f"{rockfs_dir}/tmp/operator-resources/")
    assert "service.yaml" in files
    assert "configmap.yaml" in files
    assert "validate.yaml" in files
    assert "crd-v1.yaml" in files
