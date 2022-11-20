from pynautobot import api
from ..config.nal import readConfig
import json


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

def add_device(name, site, role, devicetype, manufacturer, platform, status):

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
        if nb.dcim.sites.get(slug=site) == None:
            return {'success': False, 'reason':'unknown site %s' % site}
        else:
            site_id = nb.dcim.sites.get(slug=site).id
        # check role
        if nb.dcim.device_roles.get(slug=role) == None:
            return {'success': False, 'reason': 'unknown role %s' % role}
        else:
            role_id = nb.dcim.device_roles.get(slug=role).id
        # check type
        if nb.dcim.device_types.get(slug=devicetype) == None:
            return {'success': False, 'reason': 'unknown type %s' % type}
        else:
            devicetype_id = nb.dcim.device_types.get(slug=devicetype).id
        # check manufacturer
        if nb.dcim.manufacturers.get(slug=manufacturer) == None:
            return {'success': False, 'reason': 'unknown manufacturer %s' % manufacturer}
        else:
            manufacturer_id = nb.dcim.manufacturers.get(slug=manufacturer).id
        # check platform
        if nb.dcim.platforms.get(slug=platform) == None:
            return {'success': False, 'reason': 'unknown platform %s' % platform}
        else:
            platform_id = nb.dcim.platforms.get(slug=platform).id

        try:
            nb_device = nb.dcim.devices.create(
                name=name,
                manufacturer=manufacturer_id,
                platform=platform_id,
                site=site_id,
                device_role=role_id,
                device_type=devicetype_id,
                status=status,
                )

            return {'success': True,'message':'device %s added to sot' % name}
        except Exception as exc:
            return {'success': False, 'reason': 'got exception %s' % exc}
    else:
        return {'success': False,'reason':'device already in sot'}

def add_interface(name, interface, interfacetype, description="None"):
    """

    Args:
        name: name of device
        interface: name of interface
        interfacetype: interface type eg. Loopback
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
                type=interfacetype
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

    # if new address add it
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
            if site_id is None:
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
def update_primary_adress(name, address):

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

    nb_device.primary_ip4 = nb_ipadd
    nb_device.save()
    return {'success': True, 'message': 'address is primary'}

def update_interface_values(interface_config):

    config = readConfig()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    # the newconfig contains a 'config' json variable
    try:
        newconfig = json.loads(interface_config['config'])
    except Exception as exc:
        return {'success': False, 'reason': 'not a valid json config' % exc}

    # get device
    nb_device = nb.dcim.devices.get(name=interface_config['name'])
    if not nb_device:
        return {'success': False, 'reason': 'unknown device'}

    # get interface
    interface = nb.dcim.interfaces.get(
            device_id=nb_device.id,
            name=interface_config['interface']
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
        interface.save()

    if 'mode' in newconfig:
        interface.mode = newconfig['mode']
        interface.save()

    if 'untagged' in newconfig:
        (untagged_vlan, success) = get_vlan(nb, newconfig['untagged'], newconfig['site'])
        if success and untagged_vlan is not None:
            interface.untagged_vlan = untagged_vlan
            interface.save()
        else:
            return {'success': False, 'reason': 'unknown untagged vlan'}

    if 'tags' in newconfig:
        try:
            tags = [nb.extras.tags.get(name=tag).id for tag in newconfig["tags"].split(',')]
            print (tags)
            interface.tags = tags
            interface.save()
        except Exception as exc:
            return {'success': False, 'reason': 'unknown tag found; exception: %s' % exc}

    return {'success': True, 'message': 'interface updated'}

def update_device_values(interface_config):

    config = readConfig()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    # get device id
    nb_device = nb.dcim.devices.get(name=interface_config['name'])
    if not nb_device:
        return {'success': False, 'reason': 'unknown device'}

    if 'tags' in newconfig:
        tags = [ nb.extras.tags.get(name=tag).id for tag in newconfig["tags"] ]
        nb_device.tags = tags
        nb_device.save()

    return {'success': True, 'message': 'device updated'}
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