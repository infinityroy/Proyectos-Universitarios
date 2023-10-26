from pathlib import Path
import yaml

# pip install pyyaml
def load_yaml(path):
    config = dict()
    f = Path(path)
    f.touch(exist_ok=True)
    with open(path, 'r+') as f:
        data = yaml.safe_load(f)

    return data

def save_yaml(data, path):
    with open(path, 'w') as f:
        yaml.dump(data, f)