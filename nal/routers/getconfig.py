from fastapi import APIRouter
from enum import Enum
from ..sot import nautobot
from ..templates.main import render_config, get_section
from ..templates.diff import get_diff

# define router
router = APIRouter(
    prefix="/getconfig",
    tags=["getconfig"],
    responses={404: {"description": "Not found"}},
)


class SourceMode(str, Enum):
    # which mode do we accept
    intended = "intended"
    current = "current"
    backup = "backup"


@router.get("/diff/{device}/{old}/{new}", tags=["getconfig"])
async def get_config_dif(device: str, old: SourceMode, new: SourceMode):
    """
    returns diff between two configs
    Args:
        device: hostname
        old: intended, backup or current
        new: intended, backup or current

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
    return get_config(device, "intended", "")


@router.get("/{device}/{source}", tags=["getconfig"])
async def get_full_config(device: str):
    """
    returns full intended config of the device<p>
    Args:
        <br><b>device:</b> hostname of the device
        <br><b>mode:</b> intended, current or backup
    Returns:
        json containing the config
    """
    return get_config(device, source.value, "")


@router.get("/{device}/{source}/{section}", tags=["getconfig"])
async def get_config_of_section(device: str, source: SourceMode, section: str):
    """
    returns config of the device<p>
    Args:
        <br><b>device:</b> hostname of the device
        <br><b>mode:</b> intended, current or backup
        <br><b>section:</b> section of the config eg. ntp, syslog
    Returns:
        json containing the config
    """
    return get_config(device, source.value, section)


def get_config(device, source, section=""):

    result = {}
    result['device'] = device
    result['source'] = source

    if source == 'intended':
        device_config = nautobot.get_low_level_data_model(device, 'hldm')
        rendered_config = render_config(device, device_config)
    elif source == 'current':
        rendered_config = "current"
    elif source == "backup":
        rendered_config = "backup"

    if len(section) > 0:
        result['section'] = section
        result['config'] = get_section(rendered_config, section)
    else:
        result['config'] = rendered_config

    return result
