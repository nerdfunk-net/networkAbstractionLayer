import napalm


def get_device_config(host,
                      username,
                      password,
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

    driver = napalm.get_network_driver(devicetype)
    device = driver(
        hostname=host,
        username=username,
        password=password,
        optional_args={"port": port},
    )

    device.open()
    return device.get_config(retrieve='running')['running']