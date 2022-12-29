from scrapli import Scrapli
from ..sot import nautobot as sot
from ..helper import helper


def get_device(host, request_args={}):
    """

    Args:
        host:
        request_args:

    Returns:

    """

    nal_config = helper.read_config()
    result = {'success': True}

    # check which profile to use
    profile = 'default'
    if 'profile' in request_args:
        profile = request_args['profile']
    account = helper.get_profile(nal_config, profile)
    if not account['success']:
        result.update({'success': False,
                       'reason': "wrong password, salt or encryption key",
                       'profile': profile,
                       'config': None})
        return (None, result)

    # get IP and platform from sot
    (primary_ip, napalm_driver) = sot.get_polling_properties(host)
    # if we do not get any primary IP we use the hostname instead
    if primary_ip is None:
        primary_ip = host

    # we have to map the napalm driver to our srapli driver / platform
    #
    # napalm | scrapli
    # -------|--------
    # ios    | cisco_iosxe
    # iosxr  | cisco_iosxr
    # nxos   | cisco_nxos

    mapping = {'ios': 'cisco_iosxe',
               'iosxr': 'cisco_iosxr',
               'nxos': 'cisco_nxos'
               }
    platform = mapping.get(napalm_driver)
    if platform is None:
        result.update({'success': False,
                       'username': account['username'],
                       'reason': "got wrong napalm driver %s" % napalm_driver,
                       'config': None})
        return (None, result)

    # initialize scrapli
    # use
    #
    # ssh_config_file: True
    #
    # to avoid login problems with old systems
    # add the follwoing config to ~/.ssh/ssh_config
    #
    # KexAlgorithms diffie-hellman-group-exchange-sha1,diffie-hellman-group14-sha1
    # HostKeyAlgorithms ssh-rsa

    device = {
        "host": primary_ip,
        "auth_username": account['username'],
        "auth_password": account['password'],
        "auth_strict_key": False,
        "platform": platform,
        "ssh_config_file": "~/.ssh/ssh_config"
    }

    return device, result


def show_command(host, command, request_args={}):

    (device, result) = get_device(host, request_args)
    if not result['success']:
        return result

    command = "show cdp neighbors"
    conn = Scrapli(**device)
    conn.open()
    response = conn.send_command("show %s" % command)
    result.update({'success': True,
                   'structured_result': response.genie_parse_output(),
                   'result': response.result})

    return result


def get_device_config(host, configtype, request_args={}):
    """

    Args:
        host:
        configtype:
        request_args:

    Returns:
        result (success, reason if false, used username and config)
    """

    (device, result) = get_device(host, request_args)
    if not result['success']:
        return result

    ctype = "running-config"
    if configtype == "startup":
        ctype = "startup-config"

    conn = Scrapli(**device)
    conn.open()
    response = conn.send_command("show %s" % ctype)
    result.update({'success': True,
                   'config': response.result})

    return result
