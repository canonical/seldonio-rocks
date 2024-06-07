# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Checks out charm repository into `charm_repo`. Updated metadata.yaml with reference to locally
# built rock. Executes integration tests.
#

from pathlib import Path

import os
import logging
import random
import pytest
import string
import subprocess
import yaml
from charmed_kubeflow_chisme.rock import CheckRock

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
def test_rock(rock_test_env):
    """Test rock."""
    temp_dir, container_name = rock_test_env
    check_rock = CheckRock("rockcraft.yaml")
    rock_image = check_rock.get_name()
    rock_version = check_rock.get_version()
    LOCAL_ROCK_IMAGE = f"{rock_image}:{rock_version}"

    # rockfs_tar = temp_dir.join("rockfs.tar")
    rockfs_tar = "rockfs.tar"
    rockfs_dir = temp_dir.mkdir("rockfs")

    # verify that rock service matches charm service
    rock_services = check_rock.get_services()
    assert rock_services["seldon-core"]
    assert rock_services["seldon-core"]["startup"] == "enabled"

    # create rock filesystem
    subprocess.run(["docker", "create", f"--name={container_name}", LOCAL_ROCK_IMAGE])
    subprocess.run(["docker", "export", f"{container_name}", "--output", rockfs_tar], check=True)
    subprocess.run(["tar", "xvf", rockfs_tar, "-C", rockfs_dir], check=True)

    # verify that all artifacts are in correct locations
    files = os.listdir(f"{rockfs_dir}/")
    assert "manager" in files

    files = os.listdir(f"{rockfs_dir}/tmp/operator-resources/")
    assert "service.yaml" in files
    assert "configmap.yaml" in files
    assert "validate.yaml" in files
    assert "crd-v1.yaml" in files

    subprocess.run(["rm",rockfs_tar], check=True)
