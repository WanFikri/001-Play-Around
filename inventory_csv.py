#!/usr/bin/env python3

import csv
import json

inventory = {
    "_meta": {
        "hostvars": {}
    },
    "windows_winrm": {
        "hosts": []
    },
    "linux": {
        "hosts": []
    }
}

CSV_FILE = "winRM.csv"

with open(CSV_FILE, newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        hostname = row["hostname"].strip()
        ip = row["ip"].strip()

        if not hostname or not ip:
            continue

        if hostname.lower().startswith("win"):
            group = "windows_winrm"
        elif hostname.lower().startswith("lin"):
            group = "linux"
        else:
            continue

        inventory[group]["hosts"].append(hostname)

        inventory["_meta"]["hostvars"][hostname] = {
            "ansible_host": ip
        }

print(json.dumps(inventory, indent=2))
