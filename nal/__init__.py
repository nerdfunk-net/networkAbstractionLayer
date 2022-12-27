"""
The network abstraction layer is the interface between the SOT (nautobot
and other databases and your miniapps.

There are several routers included:

getconfig:
getconfig includes all interfaces to get the desired config (intended,
running or startup) from a device.

getdevice:
getdevice includes all interfaces to get a list of devices using either
graphql or the nautobot api. You can use filters to filter the number of
devices.

getter:
getter includes all interfaces to get data from github.

hldm:
hldml includes all interfaces to get the high level data model of a device.

lldm:
lldm includes all interfaces to get the low level data model of a device.
The lldm configuration is obtained by:
 1. getting the nautobot data model
 2. enrich this config with other data like github or ipam
 3. using the enriched config and your business logic to build the lldm
Together with the jinja2 templates, the lldm can be used to create your device config.

onboarding:
onboarding includes all interfaces to add new devices to your SOT or to update some data of a device.

"""