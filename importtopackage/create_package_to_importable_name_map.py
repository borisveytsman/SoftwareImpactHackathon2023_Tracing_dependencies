import json
import os

import pandas as pd
from johnnydep import JohnnyDist

df = pd.read_csv("/dbfs/hackathon/data/software_mentions/doi_10.5061_dryad/linked/normalized/pypi_df.csv")

if os.path.exists("pypi_importmap.json"):
    with open("pypi_importmap", "r") as f:
        pypi_map = json.load(f)
else:
    pypi_map = {}
if os.path.exists("pypi_importmap_errors.json"):
    with open("pypi_importmap", "r") as f:
        errors = set(json.load(f))
else:
    errors = set()

retry_errors = False
save_every = 100

count = 0
for pypi_name in df["mapped_to"]:
    if pypi_name in pypi_map:
        continue
    if pypi_name in errors:
        if retry_errors:
            errors.remove(pypi_name)
        else:
            continue
    try:
        dist = JohnnyDist(pypi_name)
        pypi_map[pypi_name] = dist.import_names
    except:
        errors.add(pypi_name)
    count += 1
    if count % save_every == 0:
        with open("pypi_importmap.json", "w") as f:
            json.dump(pypi_map, f)
        with open("pypi_importmap_errors.json", "w") as f:
            json.dump(list(errors), f)
        