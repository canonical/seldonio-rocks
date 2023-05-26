# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Checks out charm repository into `charm_repo`. Updated metadata.yaml with reference to locally
# built ROCK. Executes integration tests.
#

from pathlib import Path

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

    # verify that all artifacts are in correct locations
    subprocess.run(["docker", "run", f"{LOCAL_ROCK_IMAGE}", "exec", "ls", "/opt/seldon-core-operator/manager"], check=True)
    subprocess.run(["docker", "run", f"{LOCAL_ROCK_IMAGE}", "exec", "ls", "/tmp/operator-resources/service.yaml"], check=True)
    subprocess.run(["docker", "run", f"{LOCAL_ROCK_IMAGE}", "exec", "ls", "/tmp/operator-resources/configmap.yaml"], check=True)
    subprocess.run(["docker", "run", f"{LOCAL_ROCK_IMAGE}", "exec", "ls", "/tmp/operator-resources/validate.yaml"], check=True)
    subprocess.run(["docker", "run", f"{LOCAL_ROCK_IMAGE}", "exec", "ls", "/tmp/operator-resources/crd-v1.yaml"], check=True)

