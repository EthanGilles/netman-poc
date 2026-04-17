#!/usr/bin/env python3
"""
Topology server for Grafana Node Graph panel.
Serves nodes/edges JSON from the GNS3 lab topology.
Queries Prometheus to color monitored routers green (up) or red (down).

Run:  python3 monitoring/topology_server.py
Port: 8765
"""

import json
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

PROMETHEUS_URL = "http://localhost:9090"

# ── Static node definitions ───────────────────────────────────────────────────
# Monitored routers (SNMP) get live up/down color from Prometheus.
# Non-monitored nodes (Internet, Denver) are always shown as neutral.
NODES = [
    {"id": "R1",        "title": "R1",        "subTitle": "BGP 65001 / OSPF", "mainStat": "198.51.100.101", "monitored": True},
    {"id": "R2",        "title": "R2",        "subTitle": "OSPF",             "mainStat": "198.51.100.102", "monitored": True},
    {"id": "R3",        "title": "R3",        "subTitle": "OSPF Core",        "mainStat": "198.51.100.103", "monitored": True},
    {"id": "R4",        "title": "R4",        "subTitle": "OSPF Core",        "mainStat": "198.51.100.104", "monitored": True},
    {"id": "R5",        "title": "R5",        "subTitle": "OSPF Access",      "mainStat": "198.51.100.105", "monitored": True},
    {"id": "R6",        "title": "R6",        "subTitle": "OSPF Access",      "mainStat": "198.51.100.106", "monitored": True},
    {"id": "R7",        "title": "R7",        "subTitle": "OSPF Access",      "mainStat": "198.51.100.107", "monitored": True},
    {"id": "R8",        "title": "R8",        "subTitle": "OSPF Access",      "mainStat": "198.51.100.108", "monitored": True},
    {"id": "Internet",  "title": "Internet",  "subTitle": "BGP 65002",        "mainStat": "8.8.8.8",        "monitored": False},
    {"id": "Denver-R1", "title": "Denver-R1", "subTitle": "BGP 65003 / OSPF", "mainStat": "10.0.14.2",      "monitored": False},
    {"id": "Denver-R2", "title": "Denver-R2", "subTitle": "OSPF",             "mainStat": "10.0.15.2",      "monitored": False},
]

EDGES = [
    {"id": "R3-R4",         "source": "R3",        "target": "R4",        "mainStat": "10.0.6.x  OSPF"},
    {"id": "R1-R3",         "source": "R1",        "target": "R3",        "mainStat": "10.0.1.x  OSPF"},
    {"id": "R3-R5",         "source": "R3",        "target": "R5",        "mainStat": "10.0.5.x  OSPF"},
    {"id": "R3-R6",         "source": "R3",        "target": "R6",        "mainStat": "10.0.7.x  OSPF"},
    {"id": "R3-R7",         "source": "R3",        "target": "R7",        "mainStat": "OSPF"},
    {"id": "R3-R8",         "source": "R3",        "target": "R8",        "mainStat": "10.0.11.x OSPF"},
    {"id": "R2-R4",         "source": "R2",        "target": "R4",        "mainStat": "10.0.13.x OSPF"},
    {"id": "R4-R5",         "source": "R4",        "target": "R5",        "mainStat": "10.0.4.x  OSPF"},
    {"id": "R4-R6",         "source": "R4",        "target": "R6",        "mainStat": "10.0.8.x  OSPF"},
    {"id": "R4-R7",         "source": "R4",        "target": "R7",        "mainStat": "OSPF"},
    {"id": "R4-R8",         "source": "R4",        "target": "R8",        "mainStat": "10.0.12.x OSPF"},
    {"id": "R1-Internet",   "source": "R1",        "target": "Internet",  "mainStat": "10.0.2.x  BGP"},
    {"id": "Int-Denver-R1", "source": "Internet",  "target": "Denver-R1", "mainStat": "10.0.14.x BGP"},
    {"id": "DR1-DR2",       "source": "Denver-R1", "target": "Denver-R2", "mainStat": "10.0.15.x OSPF"},
]


def get_router_status():
    """Query Prometheus for SNMP exporter up/down status per router name."""
    url = f"{PROMETHEUS_URL}/api/v1/query?query=up%7Bjob%3D%22snmp_exporter%22%7D"
    try:
        with urllib.request.urlopen(url, timeout=2) as r:
            data = json.loads(r.read())
        status = {}
        for result in data.get("data", {}).get("result", []):
            name = result["metric"].get("name", "")
            value = int(float(result["value"][1]))
            if name:
                status[name] = value
        return status
    except Exception:
        return {}


def build_nodes():
    """Return nodes with live arc__up / arc__down fields from Prometheus."""
    status = get_router_status()
    nodes = []
    for n in NODES:
        node = {k: v for k, v in n.items() if k != "monitored"}
        if n["monitored"]:
            up = status.get(n["id"], -1)
            if up == 1:
                node["arc__up"]   = 1
                node["arc__down"] = 0
            elif up == 0:
                node["arc__up"]   = 0
                node["arc__down"] = 1
            else:
                # Prometheus unreachable or no data yet — show neutral
                node["arc__up"]   = 0.5
                node["arc__down"] = 0.5
        else:
            node["arc__up"]   = 1
            node["arc__down"] = 0
        nodes.append(node)
    return nodes


class TopologyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/nodes":
            data = build_nodes()
        elif self.path == "/edges":
            data = EDGES
        else:
            self.send_response(404)
            self.end_headers()
            return

        body = json.dumps(data, indent=2).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.end_headers()

    def log_message(self, fmt, *args):
        pass  # suppress per-request noise


if __name__ == "__main__":
    port = 8765
    server = HTTPServer(("localhost", port), TopologyHandler)
    print(f"Topology server running on http://localhost:{port}")
    print("  GET /nodes  — routers with live up/down status from Prometheus")
    print("  GET /edges  — link list")
    print("Press Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
