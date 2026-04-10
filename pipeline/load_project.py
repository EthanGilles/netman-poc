#!/usr/bin/env python3
import json
import time
from pathlib import Path

import requests

from utils import close_project, get_auth, get_base_url, get_env


def get_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def resolve_project_path(project_path: str) -> Path:
    project_file = Path(project_path)
    if not project_file.is_absolute():
        project_file = get_repo_root() / project_file
    return project_file.expanduser().resolve()


def parse_gns3_file(project_file: Path) -> dict:
    with open(project_file) as f:
        return json.load(f)


def find_project_by_id(base_url, project_id, auth=None):
    response = requests.get(f"{base_url}/projects", timeout=30, auth=auth)
    response.raise_for_status()
    for project in response.json():
        if project.get("project_id") == project_id:
            return project
    return None


def create_project(base_url, project_id, project_name, auth=None):
    url = f"{base_url}/projects"
    payload = {"project_id": project_id, "name": project_name}
    response = requests.post(url, json=payload, timeout=30, auth=auth)
    response.raise_for_status()
    print(f"Created project '{project_name}' ({project_id})")
    return response.json()


def open_project(base_url, project_id, auth=None):
    url = f"{base_url}/projects/{project_id}/open"
    for attempt in range(10):
        response = requests.post(url, timeout=30, auth=auth)
        if response.status_code in (200, 201):
            print(f"Opened project {project_id}")
            return response.json()
        if response.status_code == 409:
            print(f"Open failed (409): {response.text}")
            print(f"Retrying ({attempt + 1}/10)...")
            time.sleep(2)
            continue
        print(f"Open failed ({response.status_code}): {response.text}")
        response.raise_for_status()
    raise SystemExit(f"Failed to open project {project_id} after retries")


def link_project_dir(project_id, project_file: Path):
    """Symlink the GNS3 project directory to the repo workspace directory.
    This avoids copying files — GNS3 reads the .gns3 file directly from the repo."""
    projects_dir = Path.home() / "GNS3" / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)
    link = projects_dir / project_id

    if link.is_symlink():
        if link.resolve() == project_file.parent.resolve():
            print(f"Symlink already correct: {link}")
            return
        link.unlink()
        print(f"Removed stale symlink {link}")
    elif link.exists():
        # Real directory exists — replace with symlink so GNS3 uses the repo's files
        import shutil
        shutil.rmtree(link)
        print(f"Replaced existing project directory with symlink: {link}")

    link.symlink_to(project_file.parent)
    print(f"Linked {link} -> {project_file.parent}")


def import_project(base_url, project_path, auth=None):
    project_file = resolve_project_path(project_path)
    if not project_file.exists():
        raise SystemExit(f"Project file not found: {project_file}")

    gns3_data = parse_gns3_file(project_file)
    project_id = gns3_data["project_id"]
    project_name = gns3_data["name"]
    print(f"Loading project '{project_name}' (ID: {project_id})")

    # Point GNS3's project directory at the repo workspace — no file copying
    link_project_dir(project_id, project_file)

    # Check if project already exists on the server
    existing = find_project_by_id(base_url, project_id, auth=auth)
    if existing:
        status = existing.get('status', 'unknown')
        print(f"Project exists on server (status: {status})")
        if status == 'opened':
            close_project(base_url, project_id, auth=auth)
    else:
        print("Project not found on server, creating...")
        create_project(base_url, project_id, project_name, auth=auth)
        close_project(base_url, project_id, auth=auth)

    project = open_project(base_url, project_id, auth=auth)
    return project


def main():
    base_url = get_base_url()
    auth = get_auth()
    project_path = get_env("GNS3_PROJECT_PATH", 1, default=str(get_repo_root() / "PoC.gns3"))
    if not project_path:
        raise SystemExit("GNS3_PROJECT_PATH is required")

    print(f"Importing project from {project_path}")
    data = import_project(base_url, project_path, auth=auth)
    print("Project loaded successfully:")
    print(f"  Name:   {data.get('name')}")
    print(f"  ID:     {data.get('project_id')}")
    print(f"  Status: {data.get('status')}")

    # Write project_id to file for next step
    with open("project_id.txt", "w") as f:
        f.write(data["project_id"])
    print(f"PROJECT_ID={data['project_id']}")


if __name__ == "__main__":
    main()

