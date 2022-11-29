from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, validator
from ..sot import nautobot as sot
from ..sot import onboarding as onboarding
from typing import Optional


router = APIRouter(
    prefix="/onboarding",
    tags=["onboarding"],
    responses={404: {"description": "Not found"}},
)


class AddSiteModel(BaseModel):
    name: str
    slug: str
    status: str


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
    enabled: Optional[bool] = True
    description: Optional[str] = ''

    class Config:
        validate_assignment = True
        @validator('description')
        def set_description(cls, description):
            return description or ''
        @validator('enabled')
        def set_enabled(cls, enabled):
            return enabled or True


class AddAddressModel(BaseModel):
    name: str
    interface: str
    address: str


class AddPlatformModelModel(BaseModel):
    name: str
    slug: str
    description: Optional[str] = ''
    manufacturer: Optional[str] = ''
    napalm_driver: Optional[str] = ''
    napalm_args: Optional[str] = ''


class NameAndSlugModel(BaseModel):
    name: str
    slug: str


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
    config: dict


class NameAndConfigModel(BaseModel):
    name: str
    config: dict


class SlugAndConfigModel(BaseModel):
    slug: str
    config: dict


@router.post("/addsite", tags=["onboarding"])
async def add_site_to_sot(config: AddSiteModel):

    result = onboarding.add_site(
        config.name,
        config.slug,
        config.status)

    return result


@router.post("/adddevice", tags=["onboarding"])
async def add_device_to_sot(config: AddDeviceModel):

    result = onboarding.add_device(
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

    result = onboarding.add_interface(
        config.name,
        config.interface,
        config.interfacetype,
        config.enabled,
        config.description
    )

    return result


@router.post("/addaddress", tags=["onboarding"])
async def add_device_to_sot(config: AddAddressModel):

    result = onboarding.add_address(
        config.name,
        config.interface,
        config.address)

    return result


@router.post("/addvlan", tags=["onboarding"])
async def add_vlan_to_sot(config: AddVlanModel):
    result = onboarding.add_vlan(
        config.vid,
        config.name,
        config.status,
        config.site)

    return result


@router.post("/addmanufacturer", tags=["onboarding"])
async def add_manufacturer_to_sot(config: NameAndSlugModel):
    result = onboarding.add_manufacturer(
        config.name,
        config.slug)

    return result


@router.post("/addplatform", tags=["onboarding"])
async def add_platform_to_sot(config: AddPlatformModelModel):
    result = onboarding.add_platform(
        config.name,
        config.slug,
        config.description,
        config.manufacturer,
        config.napalm_driver,
        config.napalm_args)

    return result


@router.post("/updateprimary", tags=["onboarding"])
async def update_primary_address(config: UpdatePrimaryModel):
    result = onboarding.update_primary_adress(
        config.name,
        config.address
    )

    return result


@router.post("/updateinterface", tags=["onboarding"])
async def update_interface(config: UpdateInterfaceModel):

    result = onboarding.update_interface_values(
        config.name,
        config.interface,
        config.config
    )
    return result


@router.post("/updatedevice", tags=["onboarding"])
async def update_interface(config: NameAndConfigModel):

    result = onboarding.update_device_values(
        config.name,
        config.config
    )
    return result


@router.post("/updatesite", tags=["onboarding"])
async def update_site(config: SlugAndConfigModel):

    result = onboarding.update_site_values(
        config.slug,
        config.config
    )
    return result


@router.post("/updatemanufacturer", tags=["onboarding"])
async def update_manufacturer(config: SlugAndConfigModel):

    result = onboarding.update_manufacturer_values(
        config.slug,
        config.config
    )
    return result


@router.post("/updateplatform", tags=["onboarding"])
async def update_platform(config: SlugAndConfigModel):

    result = onboarding.update_platform_values(
        config.slug,
        config.config
    )
    return result


@router.get("/getchoice/{item}", tags=["onboarding"])
async def get_choice(item: str):

    return onboarding.get_choices(item)
