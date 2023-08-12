import toml

def load_config(path):
    with open(path, "r") as f:
        return toml.load(f)