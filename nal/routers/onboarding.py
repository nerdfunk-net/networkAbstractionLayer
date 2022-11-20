from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, validator
from ..sot import nautobot as sot
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
    platform: Optional[str]
    status: str
    config: Optional[str]

class AddInterfaceModel(BaseModel):
    # mandatory
    name: str
    interface: str
    interfacetype: str
    # optional
    description: Optional[str] = ''

    class Config:
        validate_assignment = True
        @validator('description')
        def set_description(cls, description):
            return description or ''

class AddAddressModel(BaseModel):
    name: str
    interface: str
    address: str

class AddVlanModel(BaseModel):
    vid: str
    name: str
    status: str
    site: Optional[str] = ''

class UpdatePrimaryModel(BaseModel):
    name: str
    address: str

class UpdateInterfaceModel(BaseModel):
    name: str
    interface: str
    config: str

class UpdateDeviceModel(BaseModel):
    name: str
    config: str

@router.post("/adddevice", tags=["onboarding"])
async def add_device_to_sot(config: AddDeviceModel):

    result = sot.add_device(
        config.name,
        config.site,
        config.role,
        config.devicetype,
        config.manufacturer,
        config.platform,
        config.status)

    return result

@router.post("/addinterface", tags=["onboarding"])
async def add_device_to_sot(config: AddInterfaceModel):

    result = sot.add_interface(
        config.name,
        config.interface,
        config.interfacetype,
        config.description
    )

    return result

@router.post("/addaddress", tags=["onboarding"])
async def add_device_to_sot(config: AddAddressModel):

    result = sot.add_address(
        config.name,
        config.interface,
        config.address)

    return result

@router.post("/addvlan", tags=["onboarding"])
async def add_vlan_to_sot(config: AddVlanModel):
    result = sot.add_vlan(
        config.vid,
        config.name,
        config.status,
        config.site)

    return result
@router.post("/updateprimary", tags=["onboarding"])
async def update_primary_address(config: UpdatePrimaryModel):
    result = sot.update_primary_adress(
        config.name,
        config.address
    )

    return result
@router.post("/updateinterface", tags=["onboarding"])
async def update_interface(config: UpdateInterfaceModel):

    result = sot.update_interface_values(config.dict())
    return result

@router.post("/updatedevice", tags=["onboarding"])
async def update_interface(config: UpdateDeviceModel):

    result = sot.update_device_values(config.dict())
    return result

@router.get("/getchoice/{item}", tags=["onboarding"])
async def get_choice(item: str):

    return sot.get_choices(item)
