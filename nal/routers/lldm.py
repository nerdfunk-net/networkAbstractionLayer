from fastapi import APIRouter
from ..sot import nautobot

# define router
router = APIRouter(
    prefix="/lldm",
    tags=["lldm"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{device}/")
async def get_low_level_data_model(device: str):
    """
    returns high level data model<p>
    Args:
        <br><b>device:</b> hostname of the device
    Returns:
        json containing the high level data model
    """
    return nautobot.get_low_level_data_model(device)
