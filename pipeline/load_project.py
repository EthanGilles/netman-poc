#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth
import shutil


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


def find_project(base_url, project_name, auth=None):
    response = requests.get(f"{base_url}/projects", timeout=30, auth=auth)
    response.raise_for_status()
    projects = response.json()

    for project in projects:
        if project.get("name") == project_name:
            return project

    raise SystemExit(f"Project '{project_name}' not found in GNS3 server")


def import_project(base_url, project_path, project_name=None, auth=None):
    project_file = resolve_project_path(project_path)
    if not project_file.exists():
        raise SystemExit(f"Project file not found: {project_file}")

    # Copy to GNS3 projects directory
    gns3_projects_dir = Path.home() / "GNS3" / "projects" / "PoC"
    gns3_projects_dir.mkdir(parents=True, exist_ok=True)
    target_file = gns3_projects_dir / "PoC.gns3"
    
    print(f"Copying {project_file} to {target_file}")
    shutil.copy2(project_file, target_file)
    
    # Find the project in GNS3
    project = find_project(base_url, "PoC", auth=auth)
    return project


def main():
    base_url = get_base_url()
    auth = get_auth()
    project_path = get_env("GNS3_PROJECT_PATH", 1, default=str(get_repo_root() / "PoC.gns3"))
    if not project_path:
        raise SystemExit("GNS3_PROJECT_PATH is required")

    project_name = get_env("GNS3_PROJECT_NAME", 2)
    if not project_name:
        project_name = Path(project_path).stem

    print(f"Importing project from {project_path}")
    data = import_project(base_url, project_path, project_name, auth=auth)
    print("Project imported successfully:")
    print(data)
    
    # Write project_id to file for next step
    with open("project_id.txt", "w") as f:
        f.write(data['project_id'])
    print(f"PROJECT_ID={data['project_id']}")


if __name__ == "__main__":
    main()

