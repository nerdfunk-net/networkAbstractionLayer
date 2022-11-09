from fastapi import APIRouter
from enum import Enum
from ..nautobot.main import getGraphQL
from ..templates.main import getIntendedConfig, getSection


# define router
router = APIRouter(
    prefix="/getconfig",
    tags=["getconfig"],
    responses={404: {"description": "Not found"}},
)

# which mode do we accept
class ModelMode(str, Enum):
    intended = "intended"
    current = "current"
    backup = "backup"

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

@router.get("/{device}/{mode}", tags=["getconfig"])
async def get_full_config(device: str, mode: ModelMode):
    """
    returns full intended config of the device<p>
    Args:
        <br><b>device:</b> hostname of the device
        <br><b>mode:</b> intended, current or backup
    Returns:
        json containing the config
    """
    return get_config(device, mode.value, "")

@router.get("/{device}/{mode}/{section}", tags=["getconfig"])
async def get_config(device: str, mode: ModelMode, section: str):
    """
    returns config of the device<p>
    Args:
        <br><b>device:</b> hostname of the device
        <br><b>mode:</b> intended, current or backup
        <br><b>section:</b> section of the config eg. ntp, syslog
    Returns:
        json containing the config
    """
    return get_config(device, mode.value, section)

def get_config(device, mode, section):

    result = {}
    device_config = getGraphQL(device)
    result['device'] = device
    if mode == 'intended':
        rendered_config = getIntendedConfig(device, device_config)
    elif mode == 'current':
        result['config'] = "current"
    elif mode == "backup":
        result['config'] = "backup"

    if len(section) > 0:
        result['section'] = section
        result['config'] = getSection(rendered_config, section)
    else:
        result['config'] = rendered_config

    print (result['config'])
    return result
