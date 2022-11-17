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

def add_device(name, site, role, devicetype, manufacturer, status):

    """
    adds device to nautobot

    Args:
        name:
        site:
        role:
        devicetype:
        manufacturer:
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
            return {'status': False, 'reason':'unknown site %s' % site}
        else:
            site_id = nb.dcim.sites.get(slug=site).id
        # check role
        if nb.dcim.device_roles.get(slug=role) == None:
            return {'status': False, 'reason': 'unknown role %s' % role}
        else:
            role_id = nb.dcim.device_roles.get(slug=role).id
        # check type
        if nb.dcim.device_types.get(slug=devicetype) == None:
            return {'status': False, 'reason': 'unknown type %s' % type}
        else:
            devicetype_id = nb.dcim.device_types.get(slug=devicetype).id
        # check manufacturer
        if nb.dcim.manufacturers.get(slug=manufacturer) == None:
            return {'status': False, 'reason': 'unknown manufacturer %s' % manufacturer}
        else:
            manufacturer_id = nb.dcim.manufacturers.get(slug=manufacturer).id

        try:
            nb_device = nb.dcim.devices.create(
                name=name,
                manufacturer=manufacturer_id,
                site=site_id,
                device_role=role_id,
                device_type=devicetype_id,
                status=status,
                )

            return {'success': True,'message':'device %s added to sot' % name}
        except:
            return {'success': False, 'reason': 'got exception'}
    else:
        return {'success': False,'reason':'device already in sot'}

def add_interface(name, interface, interfacetype):
    """

    Args:
        name: name of device
        interface: name of interface
        interfacetype: interface type eg. Loopback

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
                type=interfacetype
            )
            return {'success': True, 'message': 'interface %s added to sot' % interface}
        except:
            return {'success': False, 'reason': 'got exception'}
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
        except:
            return {'success': False, 'reason': 'got exception'}
    else:
        return {'success': False, 'reason': 'unknown interface %s' % interface}
