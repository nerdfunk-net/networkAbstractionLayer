import difflib
import os.path
from ..templates.main import renderConfig
from ..sot.nautobot import get_intended_config
from ..config.nal import readConfig



def get_diff(device, old, new):
    """
    compares two configs and returns diff
    Args:
        device: hostname
        old: old config
        new: new config

    Returns:
        diff of config
    """

    # read nal config
    config = readConfig()

    intended_config = ""
    result = {}
    result['new'] = new
    result['old'] = old

    # read intended config of device if we need it
    if old == 'intended' or new == 'intended':
        intended_config = get_intended_config(device, 'intended_config')

    if old == 'intended':
        old_config = renderConfig(device, intended_config).split('\n')
    elif old == 'backup':
        filename = "%s/%s" % (config['inventory']['backup_configs'], device)
        if os.path.isfile(filename):
            with open(filename) as f:
                old_config = f.read().splitlines()
        else:
            result['diff'] = "%s not found" % filename
            result['error'] = True
            return result

    if new == 'intended':
        new_config = renderConfig(device, intended_config).split('\n')
    elif new == 'backup':
        filename = "%s/%s" % (config['inventory']['backup_configs'], device)
        if os.path.isfile(filename):
            with open(filename) as f:
                new_config = f.read().splitlines()
        else:
            result['diff'] = "%s not found" % filename
            result['error'] = True
            return result

    result['diff'] = difflib.unified_diff(old_config, new_config, old, new)

    return result