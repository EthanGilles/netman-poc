#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth


def get_env(name, index=None, default=None):
    value = os.getenv(name)
    if value:
        return value
    if index is not None and len(sys.argv) > index:
        return sys.argv[index]
    return default


def get_base_url():
    host = get_env("GNS3_SERVER_HOST", default="127.0.0.1")
    port = get_env("GNS3_SERVER_PORT", default="3080")
    return f"http://{host}:{port}/v2"


def get_auth():
    username = get_env("GNS3_API_USERNAME")
    password = get_env("GNS3_API_PASSWORD")
    if username or password:
        if not username or not password:
            raise SystemExit("Both GNS3_API_USERNAME and GNS3_API_PASSWORD are required for API auth")
        return HTTPBasicAuth(username, password)
    return None


def get_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def resolve_project_path(project_path: str) -> Path:
    project_file = Path(project_path)
    if not project_file.is_absolute():
        project_file = get_repo_root() / project_file
    return project_file.expanduser().resolve()


def import_project(base_url, project_path, project_name=None):
    project_file = resolve_project_path(project_path)
    if not project_file.exists():
        raise SystemExit(f"Project file not found: {project_file}")

    url = f"{base_url}/projects/import"
    payload = {"path": str(project_file)}
    if project_name:
        payload["name"] = project_name

    response = requests.post(url, json=payload, auth=get_auth(), timeout=60)
    if response.ok:
        return response.json()

    raise SystemExit(
        f"Failed to import project {project_file}\n"
        f"URL: {url}\n"
        f"Status: {response.status_code}\n"
        f"Body: {response.text}"
    )


def main():
    base_url = get_base_url()
    project_path = get_env("GNS3_PROJECT_PATH", 1, default=str(get_repo_root() / "PoC.gns3"))
    if not project_path:
        raise SystemExit("GNS3_PROJECT_PATH is required")

    project_name = get_env("GNS3_PROJECT_NAME", 2)
    if not project_name:
        project_name = Path(project_path).stem

    print(f"Importing project from {project_path} into {base_url}")
    data = import_project(base_url, project_path, project_name)
    print("Project imported successfully:")
    print(data)


if __name__ == "__main__":
    main()
