#!/usr/bin/env python3
import requests

from utils import close_project, get_auth, get_base_url, get_env


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

    # Get project details (load_project.py already opened it)
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
