"""
getconfig includes the following interfaces:

getconfig
   /diff/{device}/{old}/{new}
      returns the diff between two configs
   /{device}/
      returns the intended config of a device
   /{device}/{configtype}
      returns the intended, running or startup config of a device
   /{device}/{configtype}/{section}
      returns the intended, running or startup section of a device config
"""

from fastapi import APIRouter, Request
from enum import Enum
from ..templates.main import render_config, get_section
from ..helper import helper
from ..sot import nautobot as sot
from ..devicemanagement import scrapli as dm

# define router
router = APIRouter(
    prefix="/getconfig",
    tags=["getconfig"],
    responses={404: {"description": "Not found"}},
)


class Configtype(str, Enum):
    # which config type do we accept
    intended = "intended"
    running = "running"
    starting = "startup"
    backup = "backup"


@router.get("/diff/{device}/{old}/{new}", tags=["getconfig"])
async def get_config_diff(device: str, old: Configtype, new: Configtype):
    """
    returns diff between two configs
    Args:
        device: hostname
        old: intended, backup, running or startup
        new: intended, backup, running or startup

    Returns:
        diff between two configs
    """
    return helper.get_diff(device, old, new)


@router.get("/{device}/", tags=["getconfig"])
async def get_full_intended_config(device: str):
    """
    returns full intended config<p>
    Args:
        <br><b>device:</b> hostname of the device
    Returns:
        json containing the config
    """
    return get_config(device, "intended")


@router.get("/{device}/{configtype}", tags=["getconfig"])
async def get_full_config(device: str,
                          configtype: str,
                          request: Request):
    """
    returns full intended config of the device<p>
    Args:
        <br><b>device:</b> hostname/ip of the device
        <br><b>configtype:</b> intended, backup, running or startup
    Returns:
        json containing the config
    """

    request_args = dict(request.query_params)
    return get_config(device, configtype, "", request_args)


@router.get("/{device}/{configtype}/{section}", tags=["getconfig"])
async def get_config_of_section(device: str,
                                configtype: Configtype,
                                section: str,
                                request: Request):
    """
    returns config of the device<p>
    Args:
        <br><b>device:</b> hostname of the device
        <br><b>configtype:</b> intended, backup, running or startup
        <br><b>section:</b> section of the config eg. ntp, syslog
    Returns:
        json containing the config
    """

    request_args = dict(request.query_params)
    return get_config(device, configtype.value, section, request_args)


def get_config(device, configtype, section="", request_args=None):
    """

    Args:
        device:
        configtype:
        section:
        request_args:

    Returns:

    """

    if request_args is None:
        request_args = {}

    # set basic properties of the result dict
    result = {'device': device,
              'configtype': configtype,
              'config': None}

    if configtype == 'intended':
        device_config = sot.get_low_level_data_model(device=device, query='hldm')
        result['config'] = render_config(device, device_config)
    elif configtype == 'running' or configtype == 'startup':
        cnf = dm.get_device_config(device, configtype)
        result.update(cnf)

    elif configtype == "backup":
        config = "backup"

    if len(section) > 0:
        result['section'] = section
        result['config'] = get_section(config, section)
    else:
        result['configtype'] = configtype

    return result
