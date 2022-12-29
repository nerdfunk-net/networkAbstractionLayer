from pynautobot import api
from ..helper import helper
from ..sot import businesslogic


def get_site(query_filter):
    """
    returns site using specified filter
    Args:
        query_filter:
        r_type:

    Returns:

    """
    config = helper.read_config()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])
    nb.http_session.verify = False

    nb_site = nb.dcim.site.filter(**query_filter)
    return nb_site


def get_devices(query_filter):
    """
    gets API data of one or multiple devices depending on a filter

    Args:
        query_filter:

    Returns:
        json/object with device
    """
    config = helper.read_config()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])
    nb.http_session.verify = False

    nb_device = nb.dcim.devices.filter(**query_filter)
    return nb_device


def get_device(device):
    """
    gets API data of a single device using its slug

    Args:
        device:

    Returns:

    """
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])
    nb.http_session.verify = False

    return getDevices({'name':device})


def get_graph_ql(query, variables={}):
    """
    runs query and returns data
    Args:
        query: name of the query
        variables: variables defined in query

    Returns:
        json object containing query data
    """
    config = helper.read_config()
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
    config = helper.read_config()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])
    nb_device = nb.dcim.devices.get(name=device)
    if nb_device:
        return nb.dcim.devices.get(name=device).id
    else:
        return None


def get_high_level_data_model(device, query='hldm'):
    """

    the high level data model (hldm) is the nautobot model including
    tags and custom fields

    Args:
        device: hostname
        query: name of the graph ql query

    Returns: json containing the hldm

    """
    config = helper.read_config()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])
    # get ID of the device
    nb_device = nb.dcim.devices.get(name=device)
    if nb_device:
        device_id = nb.dcim.devices.get(name=device).id
        variables = {"device_id": device_id}
        return nb.graphql.query(
            query=config['nautobot'][query],
            variables=variables).json
    else:
        return {'error': True, 'reason': 'unknown device'}


def get_low_level_data_model(device: object, query: object = 'hldm') -> object:
    """

    Args:
        device:
        query:

    Returns:

    """

    hldm = get_high_level_data_model(device, query)
    lldm = businesslogic.business_logic(device, hldm)

    return lldm


def get_polling_properties(device):
    """
    get primary IP and platform from sot

    Args:
        device: hostname

    Returns:
        primary ip and platform of device

    """

    primary = None
    platform = None

    request_args = {'name': device}
    data = get_graph_ql('polling_properties_by_name_site_role_summary', request_args)
    cidr = helper.get_value_from_dict(data, ['data', 'devices', 0, 'primary_ip4', 'address'])
    # nautobot returns the IP as cidr ('/' included)
    if cidr is not None and '/' in cidr:
        primary = cidr.split('/')[0]
    else:
        primary = cidr

    platform = helper.get_value_from_dict(data, ['data', 'devices', 0, 'platform', 'slug'])

    return primary, platform
