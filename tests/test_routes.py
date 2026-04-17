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


BGP = [target for target in TARGETS if target.get("name") == "R1"]
OSPF = [target for target in TARGETS if target.get("name") == "R5" or target.get("name") == "R8"]

@pytest.mark.parametrize("target", BGP, ids=lambda t: t["name"])
def test_BGP(target):
    """Test R1 (BGP)."""
    try:
        with ssh_connect(target["ip"]) as conn:
            output = conn.send_command("ping 3.3.3.3 source 1.1.1.1")
            print(output)
            assert "!" in output.lower(), (
                f"{target['name']}: ping to R2 Loopback is not available."
            )
    except NetmikoTimeoutException:
        pytest.fail(f"Ping failed from {target['name']} to BGP Neighbor.")

@pytest.mark.parametrize("target", OSPF, ids=lambda t: t["name"])
def test_OSPF(target):
    """Testing select OSPF routers."""
    try:
        with ssh_connect(target["ip"]) as conn:
            output = conn.send_command("ping 10.0.15.1")
            assert "!" in output.lower(), (
                f"{target['name']}: ping to Denver is not available."
            )
            output = conn.send_command("ping 10.0.13.1")
            assert "!" in output.lower(), (
                f"{target['name']}: ping to R2 is not available."
            )
            output = conn.send_command("ping 10.0.7.1")
            assert "!" in output.lower(), (
                f"{target['name']}: ping to R6 is not available."
            )
    except NetmikoTimeoutException:
        pytest.fail(f"Ping failed from {target['name']} to OSPF neighbor.")


