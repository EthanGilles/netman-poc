import json
import requests
from pathlib import Path

PROMETHEUS_URL = "http://localhost:9090"
_raw = json.loads((Path(__file__).parent.parent / "monitoring" / "targets.json").read_text())
TARGETS = [{"ip": t, "name": entry["labels"]["name"]} for entry in _raw for t in entry["targets"]]


def _query(metric: str) -> list:
    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": metric},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["data"]["result"]


def test_prometheus_reachable():
    response = requests.get(f"{PROMETHEUS_URL}/-/healthy", timeout=5)
    assert response.status_code == 200, "Prometheus is not reachable"


def test_snmp_target_up():
    """Check that Prometheus successfully scraped all SNMP targets."""
    for target in TARGETS:
        results = _query(f'up{{job="snmp_exporter", instance="{target["ip"]}}}')
        assert results, f"No 'up' metric found for {target['name']} ({target['ip']})"
        value = results[0]["value"][1]
        assert value == "1", (
            f"SNMP target {target['name']} ({target['ip']}) is not up (up={value}). "
            "Check snmp_exporter and router SNMP config."
        )


def test_snmp_metrics_present():
    """Check that interface metrics are being collected from all routers."""
    for target in TARGETS:
        results = _query(f'ifHCInOctets{{instance="{target["ip"]}}}')
        assert results, (
            f"No ifHCInOctets metrics found for {target['name']} ({target['ip']}). "
            "SNMP exporter may not be scraping correctly."
        )
