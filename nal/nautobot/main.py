from pynautobot import api
from ..config.main import readConfig
import json


PYTHONWARNINGS="ignore:Unverified HTTPS request"


"""

getDevice (devicename)
getDevices (filter)
getConfig (devicename)

"""

def objectToJson(data):
    """
    converts pynautobot endpoint object to json
    """

    i: int
    returnValue = ""

    for i in range(0, len(data)):
        # it is important to use dict() instead of serialize()
        # otherwise not all data like primary_ip are returned
        returnValue += json.dumps(dict(data[i]))
    return returnValue

def getSite (filter, r_type="object"):
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
    if r_type == 'json':
        return objectToJson(nb_site)

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