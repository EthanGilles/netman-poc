import json
import subprocess
import sys
from pathlib import Path

import pytest

raw = json.loads((Path(__file__).parent.parent / "monitoring" / "targets.json").read_text())
TARGETS = [{"ip": t, "name": entry["labels"]["name"]} for entry in raw for t in entry["targets"]]


def ping(host: str, count: int = 3, timeout: int = 5) -> bool:
    result = subprocess.run(
        ["ping", "-c", str(count), "-W", str(timeout), host],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.returncode == 0


@pytest.mark.parametrize("target", TARGETS, ids=lambda t: t["name"])
def test_gns3_router_reachable(target):
    assert ping(target["ip"]), (
        f"Could not reach {target['name']} ({target['ip']}) — "
        "is GNS3 running and the project loaded?"
    )
