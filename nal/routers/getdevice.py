from fastapi import APIRouter, Depends, HTTPException
from fastapi import FastAPI, Request
from ..nautobot.main import getDevices
from ..nautobot.main import get_graph_ql
from ..nautobot.main import get_device_id


router = APIRouter(
    prefix="/getdevice",
    tags=["getdevice"],
    responses={404: {"description": "Not found"}},
)

@router.get("/ip", tags=["getconfig"])
async def get_ip_of_devices(request: Request):

    if request.query_params:
        request_args = dict(request.query_params)
        data = get_graph_ql('ipaddress_by_name_site_role_summary', request_args)
        return data
    else:
        return get_graph_ql('ipaddress_by_name_site_role_summary', {'name':''})

@router.get("/{device}", tags=["getconfig"])
async def get_device(device: str, query: str | None = None):
    """
    returns json of specified device
    Args:
        device: name of device

    Returns:
        json
    """
    result = {}
    result['filter'] = {'name':device}
    result['count'] = 0  # default if no match
    if query == 'graphql':
        result['query'] = query
        id = get_device_id(device)
        if id != 0:
            data = get_graph_ql('intended_config',{'device_id':id})
        else:
            data = ""
    else:
        result['query'] = 'api'
        data = getDevices({'name':device})

    if data:
        result['count'] = len(data)
        result['result'] = data
        return result

@router.get("/", tags=["getconfig"])
async def get_device(request: Request):
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
    result = {}
    result['filter'] = request_args
    result['count'] = 0  # default if no match

    if request_args:
        data = getDevices(request_args)
    else:
        data = getDevices({'name': ''})

    if data:
            result['count'] = len(data)
            result['result'] = data
            return result

    return {}
