import subprocess
import sys


TARGET_IP = "198.51.100.102"


def ping(host: str, count: int = 3, timeout: int = 5) -> bool:
    result = subprocess.run(
        ["ping", "-c", str(count), "-W", str(timeout), host],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.returncode == 0


def test_gns3_router_reachable():
    assert ping(TARGET_IP), (
        f"Could not reach {TARGET_IP} — is GNS3 running and the project loaded?"
    )


if __name__ == "__main__":
    if ping(TARGET_IP):
        print(f"OK: {TARGET_IP} is reachable")
        sys.exit(0)
    else:
        print(f"FAIL: {TARGET_IP} is not reachable", file=sys.stderr)
        sys.exit(1)
