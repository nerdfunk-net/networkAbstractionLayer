from pynautobot import api
from ..config.nal import readConfig


PYTHONWARNINGS="ignore:Unverified HTTPS request"

def getSite (filter):
    """
    returns site using specified filter
    Args:
        filter:
        r_type:

    Returns:

    """
    config = readConfig()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])
    nb.http_session.verify = False

    nb_site = nb.dcim.site.filter(**filter)
    return nb_site

def getDevices (filter):
    """
    gets API data of one or multiple devices depending on a filter

    Args:
        filter:

    Returns:
        json/object with device
    """
    config = readConfig()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])
    nb.http_session.verify = False

    nb_device = nb.dcim.devices.filter(**filter)
    return nb_device

def getDevice (device):
    """
    gets API data of a single device using its slug

    Args:
        device:

    Returns:

    """
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])
    nb.http_session.verify = False

    return getDevices({'name':device})

def get_intended_config (device, query='intended_config'):

    """
    Returns result of the specified graphQL query

    :param device:
    :return: json
    """
    config = readConfig()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])
    # get ID of the device
    nb_device = nb.dcim.devices.get(name=device)
    if nb_device:
        id = nb.dcim.devices.get(name=device).id
        variables = {"device_id": id}
        return nb.graphql.query(
            query=config['nautobot'][query],
            variables=variables).json
    else:
        return {'error': True, 'reason':'unknown device'}

def get_graph_ql (query, variables = {}):
    """
    runs query and returns data
    Args:
        query: name of the query
        variables: variables defined in query

    Returns:
        json object containing query data
    """
    config = readConfig()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])
    return nb.graphql.query(
        query=config['nautobot'][query],
        variables=variables).json

def get_device_id(device):
    """
    returns device id of specified device
    Args:
        device: hostname

    Returns:
        id (str) of device
    """
    # get ID of the device
    config = readConfig()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])
    nb_device = nb.dcim.devices.get(name=device)
    if nb_device:
        return nb.dcim.devices.get(name=device).id
    else:
        return 0

def add_device(name, site, role, devicetype, manufacturer, platform, status='active'):

    """
    adds device to nautobot

    Args:
        name:
        site:
        role:
        devicetype:
        manufacturer:
        platform:
        status:

    Returns:
        json containing result
    """

    config = readConfig()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    # first check if the device is already present
    nb_device = nb.dcim.devices.get(name=name)
    if not nb_device:
        # check site
        nb_site = nb.dcim.sites.get(slug=site)
        if nb_site is None:
            return {'success': False, 'reason': 'unknown site %s' % site}

        # check role
        nb_role = nb.dcim.device_roles.get(slug=role)
        if nb_role is None:
            return {'success': False, 'reason': 'unknown role %s' % role}

        # check device type
        nb_devicetype = nb.dcim.device_types.get(slug=devicetype)
        if nb_devicetype is None:
            return {'success': False, 'reason': 'unknown type %s' % devicetype}

        # check manufacturer
        nb_manufacturer = nb.dcim.manufacturers.get(slug=manufacturer)
        if nb_manufacturer is None:
            return {'success': False, 'reason': 'unknown manufacturer %s' % manufacturer}

        # check platform
        nb_platform = nb.dcim.platforms.get(slug=platform)
        if nb_platform is None:
            return {'success': False, 'reason': 'unknown platform %s' % platform}

        try:
            nb_device = nb.dcim.devices.create(
                name=name,
                manufacturer=nb_manufacturer.id,
                platform=nb_platform.id,
                site=nb_site.id,
                device_role=nb_role.id,
                device_type=nb_devicetype.id,
                status=status,
                )

            return {'success': True,'message':'device %s added to sot' % name}
        except Exception as exc:
            return {'success': False, 'reason': 'got exception %s' % exc}
    else:
        return {'success': False,'reason':'device already in sot'}

def add_interface(name, interface, interfacetype, enabled=True, description="None"):
    """

    Args:
        name: name of device
        interface: name of interface
        interfacetype: interface type eg. Loopback
        enabled: shutdown or not
        description: description

    Returns:
        json containing result
    """
    config = readConfig()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    # get device id
    nb_device = nb.dcim.devices.get(name=name)
    if not nb_device:
        return {'success': False,'reason':'unknown device'}

    # check if interface is already part of device
    nb_interface = nb.dcim.interfaces.get(
        device_id=nb_device.id,
        name=interface
    )

    # add interface
    if not nb_interface:
        try:
            nb_interface = nb.dcim.interfaces.create(
                device=nb_device.id,
                name=interface,
                description=description,
                type=interfacetype,
                enabled=enabled
            )
            return {'success': True, 'message': 'interface %s added to sot' % interface}
        except Exception as exc:
            return {'success': False, 'reason': 'got exception %s' % exc}
    else:
        return {'success': False, 'reason': 'interface already in sot'}

def add_address(name, interface, address):

    config = readConfig()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    # get device id
    nb_device = nb.dcim.devices.get(name=name)
    if not nb_device:
        return {'success': False, 'reason': 'unknown device'}

    # get ip address
    nb_ipadd = nb.ipam.ip_addresses.get(
        address=address
    )

    if nb_ipadd:
        return {'success': False,'reason':'ip address already in sot'}

    # check if interface is known
    nb_interface = nb.dcim.interfaces.get(
        device_id=nb_device.id,
        name=interface
    )

    # if it is a new address add it
    if nb_interface:
        try:
            nb_ipadd = nb.ipam.ip_addresses.create(
                address=address,
                status='Active',
                assigned_object_type="dcim.interface",
                assigned_object_id=nb.dcim.interfaces.get(
                    device=name,
                    name=interface).id
            )
            return {'success': True, 'message': 'address %s added to sot' % address}
        except Exception as exc:
            return {'success': False, 'reason': 'got exception %s' % exc}
    else:
        return {'success': False, 'reason': 'unknown interface %s' % interface}

def add_vlan(vid, name, status, site):

    config = readConfig()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    (nb_vlan, success) = get_vlan(nb, vid, site)
    if not success:
        return {'success': False, 'reason': 'unknown site %s' % site}

    if not nb_vlan:
        try:
            if site is None:
                nb_vlan = nb.ipam.vlans.create(
                    name=name,
                    vid=vid,
                    status=status
                )
            else:
                nb_vlan = nb.ipam.vlans.create(
                    site=nb.dcim.sites.get(slug=site).id,
                    name=name,
                    vid=vid,
                    status=status
                )
            return {'success': True, 'message': 'vlan %s/%s added to sot' % (name, vid)}
        except Exception as exc:
            return {'success': False, 'reason': 'got exception %s' % exc}
    else:
        return {'success': False, 'reason': 'vlan already in sot'}

def update_interface_values(name, interface, newconfig):

    config = readConfig()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    # get device
    nb_device = nb.dcim.devices.get(name=name)
    if not nb_device:
        return {'success': False, 'reason': 'unknown device'}

    # get interface
    interface = nb.dcim.interfaces.get(
        device_id=nb_device.id,
        name=interface
    )
    if interface is None:
        return {'success': False, 'reason': 'unknown interface %s' % interface}

    if 'lag' in newconfig:
        lag_interface = nb.dcim.interfaces.get(
            device_id=nb_device.id,
            name=newconfig['lag']
        )
        # now set LAG interface
        interface.lag = lag_interface

    if 'mode' in newconfig:
        interface.mode = newconfig['mode']

    if 'untagged' in newconfig:
        (untagged_vlan, success) = get_vlan(nb, newconfig['untagged'], newconfig['site'])
        if success and untagged_vlan is not None:
            interface.untagged_vlan = untagged_vlan
        else:
            return {'success': False, 'reason': 'unknown untagged vlan'}

    if 'tagged' in newconfig:
        vlans = newconfig['tagged'].split(",")
        tagged = []
        for vlan in vlans:
            (tv, success) = get_vlan(nb, vlan, newconfig['site'])
            if success and tv is not None:
                tagged.append(tv)
            else:
                return {'success': False, 'reason': 'unknown tagged vlan %s' % vlan}
        interface.tagged_vlans = tagged

    if 'tags' in newconfig:
        if newconfig['tags'] == "":
            interface.tags = []
        else:
            try:
                tags = [nb.extras.tags.get(name=tag).id for tag in newconfig["tags"].split(',')]
                interface.tags = tags
            except Exception as exc:
                return {'success': False, 'reason': 'unknown tag found; exception: %s' % exc}

    try:
        success = interface.save()
    except Exception as exc:
        return {'success': False, 'reason': 'got exception %s' % exc}

    if success:
        return {'success': True, 'message': 'interface updated'}
    else:
        return {'success': False, 'reason': 'interface not updated (values identical?)'}

def update_device_values(name, newconfig):

    config = readConfig()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    # get device
    nb_device = nb.dcim.devices.get(name=name)
    if not nb_device:
        return {'success': False, 'reason': 'unknown device %s' % name}

    if 'name' in newconfig:
        nb_device.name = newconfig['name']

    if 'device_type' in newconfig:
        nb_devicetype = nb.dcim.device_types.get(slug=newconfig['device_type'])
        if nb_devicetype is None:
            return {'success': False, 'reason': 'unknown type %s' % newconfig['device_type']}
        nb_device.device_type = nb_devicetype.id

    if 'device_role' in newconfig:
        nb_role = nb.dcim.device_roles.get(slug=newconfig['device_role'])
        if nb_role is None:
            return {'success': False, 'reason': 'unknown role %s' % newconfig['device_role']}
        nb_device.device_role = nb_role.id

    if 'serial' in newconfig:
        nb_device.serial = newconfig['serial']

    if 'site' in newconfig:
        nb_site = nb.dcim.sites.get(slug=newconfig['site'])
        if nb_site is None:
            return {'success': False, 'reason': 'unknown site %s' % newconfig['site']}
        nb_device.site = nb_site

    if 'location' in newconfig:
        nb_location = nb.dcim.locations.get(slug=newconfig['location'])
        if nb_location is None:
            return {'success': False, 'reason': 'unknown location %s' % newconfig['location']}
        nb_device.location = nb_location.id

    if 'manufacturer' in newconfig:
        nb_manufacturer = nb.dcim.manufacturers.get(slug=newconfig['manufacturer'])
        if nb_manufacturer is None:
            return {'success': False, 'reason': 'unknown manufacturer %s' % newconfig['manufacturer']}
        nb_device.manufacturer = nb_manufacturer.id

    if 'platform' in newconfig:
        nb_platform = nb.dcim.platforms.get(slug=newconfig['platform'])
        if nb_platform is None:
            return {'success': False, 'reason': 'unknown platform %s' % newconfig['platform']}
        nb_device.platform = nb_platform.id

    if 'primary_ip4' in newconfig:
        nb_ipadd = nb.ipam.ip_addresses.get(
            address=newconfig['primary_ip4']
        )
        if nb_ipadd is None:
            return {'success': False, 'reason': 'unknown ipv4 address %s' % newconfig['primary_ip4']}
        nb_device.primary_ip4 = nb_ipadd.id

    if 'comments' in newconfig:
        nb_device.comments = newconfig['comments']

    if 'tags' in newconfig:
        if newconfig['tags'] == "":
            nb_device.tags = []
        else:
            tags = [nb.extras.tags.get(name=tag).id for tag in newconfig["tags"].split(',')]
            nb_device.tags = tags

    if 'status' in newconfig:
        nb_device.status = newconfig['status']

    try:
        success = nb_device.save()
    except Exception as exc:
        return {'success': False, 'reason': 'got exception %s' % exc}

    if success:
        return {'success': True, 'message': 'device updated'}
    else:
        return {'success': False, 'message': 'device not updated (values identical?)'}
def get_choices(item):

    config = readConfig()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    if item == 'device':
        return nb.dcim.devices.choices()
    elif item == "interfaces":
        return nb.dcim.interfaces.choices()

def get_vlan(nb, vid, site=""):

    if len(site) > 0:
        # site specific VLAN
        if nb.dcim.sites.get(slug=site) == None:
            return (None, False)
        else:
            site_id = nb.dcim.sites.get(slug=site).id
            nb_vlan = nb.ipam.vlans.get(
                site=site_id,
                vid=vid,
            )
    else:
        # global VLAN
        nb_vlan = nb.ipam.vlans.get(
            vid=vid,
        )

    return (nb_vlan, True)

def update_device_json(name, newconfig):

    print (newconfig)
    return {}