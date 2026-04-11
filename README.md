# netman-poc

Network Management and Automation PoC using GNS3.

## Prerequisites

- GNS3 installed and running
- The IOS image `c7200-adventerprisek9-mz.152-4.M7.image` in `~/GNS3/images/dynamips/` (get this from the project owner — too large for git)
- Python 3: `pip install -r pipeline/requirements.txt`

## First-time setup

With GNS3 open and running, run this once from the repo root:

```bash
GNS3_API_USERNAME=<your-gns3-username> GNS3_API_PASSWORD=<your-gns3-password> python3 pipeline/load_project.py
```

You can find your GNS3 credentials in the server config:

```bash
cat ~/.config/GNS3/2.2/gns3_server.conf
```

This creates a symlink so GNS3's project directory points at your repo clone. After that you can open `PoC.gns3` directly from the repo and all saves will go back into git automatically.

## Making changes

1. Open `PoC.gns3` in GNS3
2. Make your changes (topology, router configs, etc.)
3. On any router you configure, save the config:
   ```
   Router# copy running-config startup-config
   ```
4. Save the project in GNS3: **File → Save Project**
5. Commit and push:
   ```bash
   git add PoC.gns3 project-files/
   git commit -m "describe your change"
   git push
   ```

## CI Pipeline (Self-Hosted Runner)

This GitHub Actions pipeline runs on your laptop instead of GitHub's cloud servers.

### How it works

The pipeline targets your laptop using the `gns3` label:

```yaml
runs-on: [gns3]
```

Your laptop needs a GitHub Actions self-hosted runner registered with the `gns3` label.

### What runs on each PR to `main`

1. Starts `gns3server` locally on `127.0.0.1:3080`
2. Loads the `PoC.gns3` project from the checked-out repo
3. Boots all nodes using `pipeline/start_all_nodes.py`
4. Waits up to 5 minutes for routers to come online (pings `198.51.100.102`)
5. Runs `python src/main.py` to configure routers
6. Runs `pytest tests/` to test configurations
7. Shuts down `gns3server` and `dynamips` when done
