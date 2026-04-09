#!/usr/bin/env python3
import os
import sys

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


def close_project(base_url, project_id, auth=None):
    url = f"{base_url}/projects/{project_id}/close"
    response = requests.post(url, timeout=30, auth=auth)
    if response.status_code == 404:
        return
    response.raise_for_status()
    print(f"Closed project {project_id}")
