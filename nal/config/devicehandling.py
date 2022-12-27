import napalm


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
