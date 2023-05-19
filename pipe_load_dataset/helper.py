from typing import List
import os

def get_dataset_files(path) -> List[str]:
    if os.path.isfile(path):
        return [path]

    return sorted([os.path.join(dp, f) for dp, dn, filenames in os.walk(path) for f in filenames])
