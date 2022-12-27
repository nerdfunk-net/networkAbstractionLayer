import os
from fastapi import APIRouter
from fastapi import Request
from ..sot.nautobot import get_devices, get_graph_ql, get_device_id
from ..helper import helper


router = APIRouter(
    prefix="/getdevice",
    tags=["getdevice"],
    responses={404: {"description": "Not found"}},
)

@router.get("/ip", tags=["getdevice"])
async def get_ip_of_devices(request: Request):
    """

    Args:
        request: nautobot filter

    Returns:
        list of IP addresses
    """

    if request.query_params is not None:
        request_args = dict(request.query_params)
        return get_graph_ql('ipaddress_by_name_site_role_summary', request_args)
    else:
        return get_graph_ql('ipaddress_by_name_site_role_summary', {'name':''})

@router.get("/ip/{device}", tags=["getdevice"])
async def get_ip_of_device(device: str):
    """

    Args:

    Returns:
        primary IP of device or None if not existing
    """
    request_args = {'name': device}
    data = get_graph_ql('ipaddress_by_name_site_role_summary', request_args)
    return helper.get_value_from_dict(data, ['data', 'devices', 0, 'primary_ip4', 'address'])

@router.get("/{device}", tags=["getdevice"])
async def get_device(device: str, query: str | None = None):
    """

    Args:
        device: name of device
        query: either graphql or api

    Returns: json of specified device

    """

    result = {'filter': {'name': device}, 'count': 0}
    if query == 'graphql':
        result['query'] = query
        device_id = get_device_id(device)
        if device_id != 0:
            data = get_graph_ql('hldm',{'device_id':device_id})
        else:
            data = ""
    else:
        result['query'] = 'api'
        data = get_devices({'name':device})

    if data:
        result['count'] = len(data)
        result['result'] = data
        return result

@router.get("/", tags=["getdevice"])
async def get_filtered_devices(request: Request):
    """
    returns device<p>
    Args:
        <br><b>request:</b> the 'nautobot' filter<p>
        <br><b>examples</b>:
        <br>http://127.0.0.1:8000/getdevice/?name=hostname&model=router<p>
        <br>name=devicename
        <br>role=rolename
        <br>model=device type slug
    <p>Returns:
        the device as json
    """
    request_args = dict(request.query_params)
    result = {'filter': request_args, 'count': 0}

    if request_args:
        data = get_devices(request_args)
    else:
        data = get_devices({'name': ''})

    if data is not None:
            result['count'] = len(data)
            result['result'] = data
            return result

    return {}
