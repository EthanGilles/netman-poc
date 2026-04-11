import requests

PROMETHEUS_URL = "http://localhost:9090"
SNMP_TARGET = "198.51.100.102"


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
    """Check that Prometheus successfully scraped the SNMP target."""
    results = _query(f'up{{job="snmp", instance="{SNMP_TARGET}"}}')
    assert results, f"No 'up' metric found for SNMP target {SNMP_TARGET}"
    value = results[0]["value"][1]
    assert value == "1", (
        f"SNMP target {SNMP_TARGET} is not up (up={value}). "
        "Check snmp_exporter and router SNMP config."
    )


def test_snmp_metrics_present():
    """Check that interface metrics are being collected from the router."""
    results = _query(f'ifHCInOctets{{instance="{SNMP_TARGET}"}}')
    assert results, (
        f"No ifHCInOctets metrics found for {SNMP_TARGET}. "
        "SNMP exporter may not be scraping correctly."
    )
