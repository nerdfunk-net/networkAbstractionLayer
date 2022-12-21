from fastapi import APIRouter, Request
from enum import Enum
from ..sot import nautobot
from ..templates.main import render_config, get_section
from ..templates.diff import get_diff
from ..config.nal import read_config, get_account
from ..config.devicehandling import get_device_config


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
    starting = "starting"
    backup = "backup"


@router.get("/diff/{device}/{old}/{new}", tags=["getconfig"])
async def get_config_diff(device: str, old: Configtype, new: Configtype):
    """
    returns diff between two configs
    Args:
        device: hostname
        old: intended, backup, running or starting
        new: intended, backup, running or starting

    Returns:
        diff between two configs
    """
    return get_diff(device, old, new)


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
        <br><b>configtype:</b> intended, backup, running or starting
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
        <br><b>configtype:</b> intended, backup, running or starting
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
    result = {'device': device, 'configtype': configtype}

    if configtype == 'intended':
        device_config = nautobot.get_low_level_data_model(device=device, query='hldm')
        config = render_config(device, device_config)
    elif configtype == 'running':
        nal_config = read_config()
        profile = 'default'
        if 'profile' in request_args:
            profile = request_args['profile']
        account = get_account(nal_config, profile)
        config = get_device_config(device,
                                   account['username'],
                                   account['password'])

    elif configtype == 'starting':
        config = "starting"
    elif configtype == "backup":
        config = "backup"

    if len(section) > 0:
        result['section'] = section
        result['config'] = get_section(config, section)
    else:
        result['configtype'] = configtype
        result['config'] = config

    return result
