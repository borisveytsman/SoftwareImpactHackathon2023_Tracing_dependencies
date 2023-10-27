# SPDX-FileCopyrightText: 2023 Brown, E. M., Nesbitt, A., Hébert-Dufresne, L., Veytsman, B., Pimentel, J. F., Druskat, S., Mietchen, D.
#
# SPDX-License-Identifier: MIT

import sys
import csv
import json
import argparse
import os

import pandas as pd
from io import StringIO
from collections import defaultdict

from stdlib_list import stdlib_list

import extract_imports


class PackageExtractorConfig:

    def __init__(self, import_cut=1, strategy="mostdownloaded", use_bq=False):
        # alternative strategy: all
        self.import_cut = import_cut
        self.inverse_map = defaultdict(list) 
        self.download_count = {}
        self.pypi_heuristic_map = defaultdict(list) 

        if use_bq:
            pypi_packages = pd.read_csv("pypi-bq-results.csv")
            for i, row in pypi_packages.iterrows():
                self.download_count[str(row["project_name"])] = int(row["num_downloads"])
                self._populate_package_list(
                    self.pypi_heuristic_map, str(row["project_name"]).lower(),
                    str(row["project_name"]), strategy
                )

        with open("pypi_importmap.json", "r") as f:
            pypi_map = json.load(f)
            for key, values in pypi_map.items():
                for value in values:
                    self._populate_package_list(self.inverse_map, value, key, strategy)

    def _populate_package_list(self, dic, key, value, strategy):
        if strategy == "all" or key not in dic:
            dic[key].append(value)
        elif strategy == "mostdownloaded":
            existing_count = self.download_count.get(dic[key][0], 0)
            new_count = self.download_count.get(value, 0)
            if new_count > existing_count:
                dic[key].clear()
                dic[key].append(value)

def import_data_to_package(data, config=None):
    config = config or PackageExtractorConfig()
    result = []
    for import_def in data:
        if import_def["local"] >= config.import_cut:
            continue
        if import_def["name"] in stdlib_list():
            result.append({
                "name": "<builtin>",
                "filename": import_def['filename'],
                "filetype": import_def['filetype'],
                "fromtype": "import",
                "mode": "builtin_module_names",
                "importname": import_def["name"]
            })
        elif packages := config.inverse_map.get(import_def["name"], []):
            for package in packages:
                result.append({
                    "name": package,
                    "filename": import_def['filename'],
                    "filetype": import_def['filetype'],
                    "fromtype": "import",
                    "mode": "pypi_map",
                    "importname": import_def["name"]
                })
        elif packages := config.pypi_heuristic_map.get(import_def["name"].lower(), []):
            for package in packages:
                result.append({
                    "name": package,
                    "filename": import_def['filename'],
                    "filetype": import_def['filetype'],
                    "fromtype": "import",
                    "mode": "pypi_heuristic",
                    "importname": import_def["name"]
                })
        else:
            result.append({
                "name": "<unknown>",
                "filename": import_def['filename'],
                "filetype": import_def['filetype'],
                "fromtype": "import",
                "mode": "unknown",
                "importname": import_def["name"]
            })

    return result


def extract_packages_from_source_file(path, project_path=None, config=None):
    data = extract_imports.extract_from_file(path, project_path)
    return import_data_to_package(data, config=config)

def extract_from_file(path, project_path=None, config=None):
    return extract_packages_from_source_file(path, project_path, config)

def extract_from_directory(path, config=None):
    config = config or PackageExtractorConfig()
    result = []
    for root, dirs, files in os.walk(path):
        for filename in files:
            fullpath = os.path.join(root, filename)
            if ".ipynb_checkpoints" in filename:
                continue
            partial_result = []
            if fullpath.endswith('.ipynb') or fullpath.endswith('.py'):
                partial_result = extract_packages_from_source_file(fullpath, path, config)
            result += partial_result
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Package extractor')
    parser.add_argument("source")
    parser.add_argument("--csv", help="output result as csv",
                    action="store_true")

    args = parser.parse_args()
    if os.path.isfile(args.source):
        data = extract_from_file(args.source)
    else:
        data = extract_from_directory(args.source)

    if args.csv:
        df = pd.DataFrame.from_records(data)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        print(csv_buffer.getvalue())
