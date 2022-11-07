import jinja2
from ..config.main import readConfig


def getIntendedConfig(device, device_config):

    """

    Args:
        device: host or ip of device
        config: config as json

    Returns:
        intended config as json or text

    """

    # set default values
    config = readConfig()
    # if not platform is set we use the default platform
    device_platform = config['templates']['default']
    if 'platform' in device_config['data']['device']:
        device_platform = device_config['data']['device']['platform']['slug']
    # do we have to trim the blocks
    if 'trim_blocks' in config['templates']:
        trim_blocks = config['templates']['trim_blocks']
    else:
        trim_blocks = True

    # prepare template
    templateLoader = jinja2.FileSystemLoader(searchpath=config['templates']['directory'])
    templateEnv = jinja2.Environment(loader=templateLoader, trim_blocks=trim_blocks)
    template_file = "%s.j2" % device_platform
    template = templateEnv.get_template(template_file)

    return template.render(device_config['data']['device'])

