import yaml


config_file = "./nal.yaml"


def read_config():
    """
    read config from file
    Returns: json
    """
    with open(config_file) as f:
        return yaml.safe_load(f.read())


def get_value_from_dict(dictionary, keys):

    if dictionary is None:
        return None

    nested_dict = dictionary

    for key in keys:
        try:
            nested_dict = nested_dict[key]
        except KeyError as e:
            return None
        except IndexError as e:
            return None

    return nested_dict



