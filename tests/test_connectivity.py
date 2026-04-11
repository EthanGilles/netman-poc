import json
import subprocess
import sys
from pathlib import Path

_raw = json.loads((Path(__file__).parent.parent / "monitoring" / "targets.json").read_text())
TARGETS = [{"ip": t, "name": entry["labels"]["name"]} for entry in _raw for t in entry["targets"]]


def ping(host: str, count: int = 3, timeout: int = 5) -> bool:
    result = subprocess.run(
        ["ping", "-c", str(count), "-W", str(timeout), host],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.returncode == 0


def test_gns3_router_reachable():
    for target in TARGETS:
        assert ping(target["ip"]), (
            f"Could not reach {target['name']} ({target['ip']}) — "
            "is GNS3 running and the project loaded?"
        )


if __name__ == "__main__":
    failed = [t for t in TARGETS if not ping(t["ip"])]
    if failed:
        for t in failed:
            print(f"FAIL: {t['name']} ({t['ip']}) is not reachable", file=sys.stderr)
        sys.exit(1)
    for t in TARGETS:
        print(f"OK: {t['name']} ({t['ip']}) is reachable")
