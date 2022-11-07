import yaml


config_file = "./nal.yaml"

def readConfig():
    """
    read config from file
    Returns: json

    """
    with open(config_file) as f:
        return yaml.safe_load(f.read())
