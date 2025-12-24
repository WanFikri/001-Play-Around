#!/usr/bin/env python3

import json
import csv
import os

def get_inventory():
    inventory = {
        'windows_winrm': {'hosts': []},
        '_meta': {'hostvars': {}}
    }

    csv_path = 'winRM.csv'

    if os.path.exists(csv_path):
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                host = row['hostname'].strip()
                ip = row['ip'].strip()

                inventory['windows_winrm']['hosts'].append(host)
                inventory['_meta']['hostvars'][host] = {
                    'ansible_host': ip
                }

    return inventory

if __name__ == "__main__":
    print(json.dumps(get_inventory(), indent=2))
