import json
import os
from pathlib import Path

import pytest
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException


raw = json.loads((Path(__file__).parent.parent / "monitoring" / "targets.json").read_text())
TARGETS = [{"ip": t, "name": entry["labels"]["name"]} for entry in raw for t in entry["targets"]]

SSH_USERNAME = os.getenv("SSH_USERNAME", "netman")
SSH_PASSWORD = os.getenv("SSH_PASSWORD", "password123")


def ssh_connect(ip: str):
    return ConnectHandler(
        device_type="cisco_ios",
        host=ip,
        username=SSH_USERNAME,
        password=SSH_PASSWORD,
        timeout=15,
        banner_timeout=15,
    )

# With paramertrize we can run the same test for each target in our list,
# and the test output will show which target(s) failed.
@pytest.mark.parametrize("target", TARGETS, ids=lambda t: t["name"])
def test_ssh_connect(target):
    """Verify SSH connectivity to each router."""
    try:
        with ssh_connect(target["ip"]) as conn:
            assert conn.is_alive(), f"Connection to {target['name']} ({target['ip']}) dropped immediately"
    except NetmikoAuthenticationException:
        pytest.fail(f"Authentication failed for {target['name']} ({target['ip']}) — check credentials")
    except NetmikoTimeoutException:
        pytest.fail(f"Timed out connecting to {target['name']} ({target['ip']}) — is GNS3 running?")


@pytest.mark.parametrize("target", TARGETS, ids=lambda t: t["name"])
def test_show_run(target):
    """Send 'show run' to each router and verify we get a config back."""
    try:
        with ssh_connect(target["ip"]) as conn:
            output = conn.send_command("show running-config")
            assert "hostname" in output.lower(), (
                f"{target['name']} ({target['ip']}): 'show run' output looks wrong — "
                f"no 'hostname' found. Got: {output[:200]}"
            )
    except NetmikoAuthenticationException:
        pytest.fail(f"Authentication failed for {target['name']} ({target['ip']}) — check credentials")
    except NetmikoTimeoutException:
        pytest.fail(f"Timed out connecting to {target['name']} ({target['ip']}) — is GNS3 running?")
