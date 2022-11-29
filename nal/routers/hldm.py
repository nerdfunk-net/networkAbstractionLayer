from fastapi import APIRouter
from ..sot import nautobot

# define router
router = APIRouter(
    prefix="/hldm",
    tags=["hldm"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{device}/", tags=["hldm"])
async def get_high_level_data_model(device: str):
    """
    returns high level data model<p>
    Args:
        <br><b>device:</b> hostname of the device
    Returns:
        json containing the high level data model
    """
    return nautobot.get_high_level_data_model(device)
