from fastapi import APIRouter
from enum import Enum
from ..nautobot.main import get_intended_config
from ..templates.main import renderConfig, getSection
from ..templates.diff import get_diff

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

@router.get("/diff/{device}/{old}/{new}", tags=["getconfig"])
async def get_config_dif(device: str, old: ModelMode, new: ModelMode):
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

@router.get("/{device}/{mode}", tags=["getconfig"])
async def get_full_config(device: str):
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
async def get_config_of_section(device: str, mode: ModelMode, section: str):
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

def get_config(device, mode, section=""):

    result = {}
    result['device'] = device
    result['mode'] = mode

    if mode == 'intended':
        device_config = get_intended_config(device, 'intended_config')
        rendered_config = renderConfig(device, device_config)
    elif mode == 'current':
        rendered_config = "current"
    elif mode == "backup":
        rendered_config = "backup"

    if len(section) > 0:
        result['section'] = section
        result['config'] = getSection(rendered_config, section)
    else:
        result['config'] = rendered_config

    return result
