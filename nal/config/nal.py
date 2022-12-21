import yaml


config_file = "./nal.yaml"


def read_config():
    """
    read config from file
    Returns: json
    """
    with open(config_file) as f:
        return yaml.safe_load(f.read())


def get_account(config, profilename='default'):
    """

    Args:
        config:
        profilename:

    Returns: account as dict

    """

    if 'accounts' in config:
        if 'devices' in config['accounts']:
            if profilename in config['accounts']['devices']:
                return config['accounts']['devices'][profilename]

    return None
