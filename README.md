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

Your GNS3 credentials can be found in the server config:

```bash
cat ~/.config/GNS3/2.2/gns3_server.conf
```

If your local server has no authentication enabled, omit the env vars:

```bash
python3 pipeline/load_project.py
```

This creates a symlink so GNS3's project directory points at your repo clone. After this you can open `PoC.gns3` directly from the repo and all saves will go back into git automatically.

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
