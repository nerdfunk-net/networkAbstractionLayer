from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, validator
from ..sot.nautobot import add_device, add_interface, add_address
from typing import Optional



DEFAULT_MANUFACTURER = "cisco"

router = APIRouter(
    prefix="/onboarding",
    tags=["onboarding"],
    responses={404: {"description": "Not found"}},
)

# our base class contains all mandatory data we need to add
# a device to nautobot
class AddDeviceModel(BaseModel):
    name: str
    site: str
    role: str
    devicetype: str
    manufacturer: Optional[str]
    status: str
    config: Optional[str]

class AddInterfaceModel(BaseModel):
    name: str
    interface: str
    interfacetype: str

class AddAddressModel(BaseModel):
    name: str
    interface: str
    address: str

@router.post("/adddevice", tags=["onboarding"])
async def add_device_to_sot(config: AddDeviceModel):

    result = add_device(
        config.name,
        config.site,
        config.role,
        config.devicetype,
        config.manufacturer,
        config.status)

    return result

@router.post("/addinterface", tags=["onboarding"])
async def add_device_to_sot(config: AddInterfaceModel):

    result = add_interface(
        config.name,
        config.interface,
        config.interfacetype)

    return result

@router.post("/addaddress", tags=["onboarding"])
async def add_device_to_sot(config: AddAddressModel):

    result = add_address(
        config.name,
        config.interface,
        config.address)

    return result