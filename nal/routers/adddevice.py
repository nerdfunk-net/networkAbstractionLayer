from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..sot.nautobot import add_device


# our base class contains all necessary data we need to add
# a device to nautobot
class Config(BaseModel):
    name: str
    ipv4: str
    site: str
    role: str
    type: str
    manufacturer: str
    status: str
    config: str

router = APIRouter(
    prefix="/adddevice",
    tags=["adddevice"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", tags=["adddevice"])
async def add_device_to_sot(config: Config):
    result = add_device(
        config.name,
        config.ipv4,
        config.site,
        config.role,
        config.type,
        config.manufacturer,
        config.status)

    return result