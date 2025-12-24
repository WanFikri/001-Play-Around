#!/usr/bin/env python3

import csv
import json
import sys

inventory = {
    "_meta": {
        "hostvars": {}
    },
    "windows": {
        "hosts": []
    },
    "linux": {
        "hosts": []
    }
}

CSV_FILE = "winRM.csv"

try:
    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            hostname = row["hostname"].strip()
            ip = row["ip"].strip()

            # Basic validation
            if not hostname or not ip:
                continue

            # Auto-grouping logic
            if hostname.lower().startswith("win"):
                group = "windows"
            elif hostname.lower().startswith("lin"):
                group = "linux"
            else:
                group = "ungrouped"
                inventory.setdefault("ungrouped", {"hosts": []})

            inventory[group]["hosts"].append(hostname)

            inventory["_meta"]["hostvars"][hostname] = {
                "ansible_host": ip
            }

except FileNotFoundError:
    print(json.dumps(inventory))
    sys.exit(0)

print(json.dumps(inventory, indent=2))
