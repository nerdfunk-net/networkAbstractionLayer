import jinja2
from ..config.nal import readConfig


additional_newline = ["interface"]


def get_section(config, section):
    """
    returns specified section of rendered config
    Args:
        config: rendered config
        section: name of section to look at

    Returns:
        specified section as string
    """

    result = ""
    active = False
    was_active = False

    lines = config.split('\n')
    for line in lines:
        # check if section ends
        if active:
            if not line.startswith(' '):
                active = False
                was_active = True
        # check if section starts
        if line.startswith(section):
            active = True
            if section in additional_newline:
                result = result + '\n'
        # print line if section is still active
        if active:
            result = result + line + '\n'

    return result


def render_config(device, device_config):

    """

    Args:
        device: host or ip of device
        config: config as json

    Returns:
        intended config as json or text

    """

    # set default values
    config = readConfig()
    if 'platform' in device_config['data']['device']:
        device_platform = device_config['data']['device']['platform']['slug']
    else:
        return {'sucecss': False, 'reason': 'no plattform specified'}

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

    # render template
    return template.render(device_config['data']['device'])

