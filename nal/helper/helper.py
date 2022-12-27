import yaml
import napalm
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


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


def get_device_config(host,
                      username,
                      password,
                      configtype="running",
                      devicetype="ios",
                      port=22):
    """
    Login to device and get config
    Args:
        host:
        username:
        password:
        devicetype:
        port:

    Returns:
        device config
    """

    config = None
    result = {}

    driver = napalm.get_network_driver(devicetype)
    device = driver(
        hostname=host,
        username=username,
        password=password,
        optional_args={"port": port},
    )

    try:
        device.open()
        config = device.get_config(retrieve=configtype)[configtype]
        result['success'] = True
        result['config'] = config
    except Exception as e:
        result['success'] = False
        result['exception'] = "%s" % e
        result['config'] = None

    return result


def decrypt_password(password):
    """

    decrypts base64 password that is stored in our yaml config

    Args:
        password:

    Returns: clear password

    """
    # prepare salt
    salt_ascii = os.getenv('SALT')
    salt_bytes = str.encode(salt_ascii)

    # prepare encryption key, we need it as bytes
    encryption_key_ascii = os.getenv('ENCRYPTIONKEY')
    encryption_key_bytes = str.encode(encryption_key_ascii)

    # get password as base64 and convert it to bytes
    password_bytes = base64.b64decode(password)

    # derive key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_bytes,
        iterations=390000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(encryption_key_bytes))

    f = Fernet(key)
    # decrypt and return
    try:
        return f.decrypt(password_bytes)
    except:
        return None


def get_profile(config, profilename='default'):
    """

    Args:
        config:
        profilename:

    Returns: account as dict

    """

    result = {}

    username = get_value_from_dict(config, ['accounts',
                                            'devices',
                                            profilename,
                                            'username'])
    password = get_value_from_dict(config, ['accounts',
                                            'devices',
                                            profilename,
                                            'password'])

    clear_password = decrypt_password(password)

    if clear_password is None:
        result.update({'success': False, 'reason': 'wrong password'})
    else:
        result.update({'success': True, 'username': username, 'password': clear_password})

    return result
