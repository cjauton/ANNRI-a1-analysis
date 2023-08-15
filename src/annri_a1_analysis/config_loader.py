import toml

def load(path):
    with open(path, "r") as f:
        return toml.load(f)