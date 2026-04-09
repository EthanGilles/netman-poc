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


def find_project(base_url, project_name=None, project_id=None, auth=None):
    response = requests.get(f"{base_url}/projects", timeout=30, auth=auth)
    response.raise_for_status()
    projects = response.json()

    if project_id:
        for project in projects:
            if project.get("project_id") == project_id:
                return project
        raise SystemExit(f"Project with ID {project_id} not found")

    if project_name:
        for project in projects:
            if project.get("name") == project_name:
                return project

    if len(projects) == 1:
        return projects[0]

    raise SystemExit(
        "Unable to locate a single GNS3 project. "
        "Set GNS3_PROJECT_NAME, GNS3_PROJECT_ID, or ensure the server contains only one project."
    )


def start_node(base_url, project_id, node_id, auth=None):
    url = f"{base_url}/projects/{project_id}/nodes/{node_id}/start"
    response = requests.post(url, timeout=30, auth=auth)
    response.raise_for_status()
    return response.json() if response.text else {}


def close_project(base_url, project_id, auth=None):
    url = f"{base_url}/projects/{project_id}/close"
    response = requests.post(url, timeout=30, auth=auth)
    if response.status_code == 404:
        return
    response.raise_for_status()
    print(f"Closed project {project_id}")


def open_project(base_url, project_id, auth=None):
    url = f"{base_url}/projects/{project_id}/open"
    response = requests.post(url, timeout=30, auth=auth)
    if response.status_code == 409:
        # Already open — close and reopen so this session owns it
        print("Project already open, closing and reopening...")
        close_project(base_url, project_id, auth=auth)
        response = requests.post(url, timeout=30, auth=auth)
    response.raise_for_status()
    return response.json()


def main():
    base_url = get_base_url()
    auth = get_auth()

    # Read project_id from file written by load_project.py
    try:
        with open("project_id.txt", "r") as f:
            project_id = f.read().strip()
    except FileNotFoundError:
        raise SystemExit("project_id.txt not found. Run load_project.py first.")

    print(f"Opening project {project_id}")
    open_project(base_url, project_id, auth=auth)
    print("Project opened successfully")
    
    # Get project details
    project = find_project(base_url, None, project_id, auth=auth)
    
    print(f"Starting nodes for project {project.get('name')} ({project_id})")
    response = requests.get(f"{base_url}/projects/{project_id}/nodes", timeout=30, auth=auth)
    response.raise_for_status()
    nodes = response.json()

    if not nodes:
        print("No nodes found in the project.")
        return

    for node in nodes:
        node_id = node.get("node_id") or node.get("id")
        if not node_id:
            print(f"Skipping node with missing id: {node}")
            continue

        print(f"Starting node {node.get('name', node_id)} ({node_id})")
        try:
            result = start_node(base_url, project_id, node_id, auth=auth)
            print(f"Started node {node_id}: {result}")
        except Exception as e:
            print(f"Failed to start node {node_id}: {e}")


if __name__ == "__main__":
    main()
