from pynautobot import api
from ..helper import helper

"""
 +------+-----+------------------------+
 + id   |  0  |  added to sot          |
 +      |  1  |  already in sot        |
 +      |  2  |  item updated          |
 +      |  3  |  no changes            |
 +------+-----+------------------------+
"""


def add_site(name, slug, status):

    config = helper.read_config()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    nb_site = nb.dcim.sites.get(slug=slug)
    if nb_site is not None:
        return {'success': False, 'error': 'site %s already in sot' % name}

    try:
        nb_site = nb.dcim.sites.create(
            name=name,
            slug=slug,
            status=status,
        )
        return {'success': True, 'message': 'site %s added to sot' % name}
    except Exception as exc:
        return {'success': False, 'error': 'got exception %s' % exc}


def add_device(name, site, role, devicetype, manufacturer, platform, status='active'):

    """
    add device to nautobot

    Args:
        name:
        site:
        role:
        devicetype:
        manufacturer:
        platform:
        status:

    Returns:
        result with success (true, false) and error if success: false
    """

    config = helper.read_config()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    # first check if the device is already present
    nb_device = nb.dcim.devices.get(name=name)
    if not nb_device:
        # check site
        nb_site = nb.dcim.sites.get(slug=site)
        if nb_site is None:
            return {'success': False,
                    'error': 'unknown site %s' % site}

        # check role
        nb_role = nb.dcim.device_roles.get(slug=role)
        if nb_role is None:
            return {'success': False,
                    'error': 'unknown role %s' % role}

        # check device type
        nb_devicetype = nb.dcim.device_types.get(slug=devicetype)
        if nb_devicetype is None:
            return {'success': False,
                    'error': 'unknown type %s' % devicetype}

        # check manufacturer
        nb_manufacturer = nb.dcim.manufacturers.get(slug=manufacturer)
        if nb_manufacturer is None:
            return {'success': False,
                    'error': 'unknown manufacturer %s' % manufacturer}

        # check platform
        nb_platform = nb.dcim.platforms.get(slug=platform)
        if nb_platform is None:
            return {'success': False,
                    'error': 'unknown platform %s' % platform}

        try:
            nb_device = nb.dcim.devices.create(
                name=name,
                manufacturer=nb_manufacturer.id,
                platform=nb_platform.id,
                site=nb_site.id,
                device_role=nb_role.id,
                device_type=nb_devicetype.id,
                status=status,
                )

            return {'success': True,
                    'id': 0,
                    'log': 'device %s added to sot' % name}
        except Exception as exc:
            return {'success': False,
                    'error': 'got exception %s' % exc}
    else:
        return {'success': True,
                'id': 1,
                'log': 'device already in sot'}


def add_interface(name, interface, interfacetype, enabled=True, description="None"):
    """

    Args:
        name: name of device
        interface: name of interface
        interfacetype: interface type eg. Loopback
        enabled: shutdown or not
        description: description

    Returns:
        json containing result
    """
    config = helper.read_config()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    # get device id
    nb_device = nb.dcim.devices.get(name=name)
    if not nb_device:
        return {'success': False,
                'error': 'unknown device'}

    # check if interface is already part of device
    nb_interface = nb.dcim.interfaces.get(
        device_id=nb_device.id,
        name=interface
    )

    # add interface
    if not nb_interface:
        try:
            nb_interface = nb.dcim.interfaces.create(
                device=nb_device.id,
                name=interface,
                description=description,
                type=interfacetype,
                enabled=enabled
            )
            return {'success': True,
                    'id': 0,
                    'log': 'interface %s added to sot' % interface}
        except Exception as exc:
            return {'success': False,
                    'error': 'got exception %s' % exc}
    else:
        return {'success': True,
                'id': 1,
                'log': 'interface already in sot'}


def add_address(name, interface, address):

    config = helper.read_config()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    # get device id
    nb_device = nb.dcim.devices.get(name=name)
    if not nb_device:
        return {'success': False,
                'error': 'unknown device %s' % name}

    # get ip address
    nb_ipadd = nb.ipam.ip_addresses.get(
        address=address
    )
    if nb_ipadd:
        return {'success': True,
                'id': 1,
                'log': 'ip address already in sot'}

    # check if interface is known
    nb_interface = nb.dcim.interfaces.get(
        device_id=nb_device.id,
        name=interface
    )

    # if it is a new address add it
    if nb_interface:
        try:
            nb_ipadd = nb.ipam.ip_addresses.create(
                address=address,
                status='Active',
                assigned_object_type="dcim.interface",
                assigned_object_id=nb.dcim.interfaces.get(
                    device=name,
                    name=interface).id
            )
            return {'success': True,
                    'id': 0,
                    'log': 'address %s added to sot' % address}
        except Exception as exc:
            return {'success': False,
                    'error': 'got exception %s' % exc}
    else:
        return {'success': False,
                'error': 'unknown interface %s' % interface}


def add_vlan(vid, name, status, site):

    config = helper.read_config()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    (nb_vlan, success) = get_vlan(nb, vid, site)
    if not success:
        return {'success': False,
                'error': 'unknown site %s' % site}

    if not nb_vlan:
        try:
            if site is None:
                nb_vlan = nb.ipam.vlans.create(
                    name=name,
                    vid=vid,
                    status=status
                )
            else:
                nb_vlan = nb.ipam.vlans.create(
                    site=nb.dcim.sites.get(slug=site).id,
                    name=name,
                    vid=vid,
                    status=status
                )
            return {'success': True,
                    'id': 0,
                    'log': 'vlan %s/%s added to sot' % (name, vid)}
        except Exception as exc:
            return {'success': False,
                    'error': 'got exception %s' % exc}
    else:
        return {'success': True,
                'id': 1,
                'log': 'vlan already in sot'}


def add_manufacturer(name, slug):

    config = helper.read_config()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    nb_manufacturer = nb.dcim.manufacturers.get(slug=slug)
    if nb_manufacturer:
        return {'success': False,
                'id': 1,
                'log': 'manufacturer %s already in sot' % name}

    try:
        nb_manufacturer = nb.dcim.manufacturers.create(
            name=name,
            slug=slug,
        )
        return {'success': True,
                'id': 0,
                'message': 'manufacturer added to sot' % name}
    except Exception as exc:
        return {'success': False,
                'error': 'got exception %s' % exc}


def add_platform(name, slug, description, manufacturer, napalm_driver="", napalm_args=""):

    config = helper.read_config()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    nb_platform = nb.dcim.platforms.get(slug=slug)
    if nb_platform:
        return {'success': True,
                'id': 1,
                'log': 'platform %s already in sot' % name}

    manufacturer_id = None
    if len(manufacturer) > 0:
        nb_manufacturer = nb.dcim.manufacturers.get(slug=slug)
        if nb_manufacturer is None:
            return {'success': False,
                    'error': 'manufacturer %s is not in sot' % manufacturer}
        manufacturer_id = nb_manufacturer.id

    try:
        nb_platform = nb.dcim.platforms.create(
            name=name,
            slug=slug,
            description=description,
            manufacturer=manufacturer_id,
            napalm_driver=napalm_driver,
            napalm_args=napalm_args
        )
        return {'success': True,
                'id': 0,
                'log': 'platform %s added to sot' % name}
    except Exception as exc:
        return {'success': False,
                'error': 'got exception %s' % exc}


def update_interface_values(name, interface, newconfig):

    config = helper.read_config()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])
    values = ', '.join(map(str, newconfig.values()))

    # get device
    nb_device = nb.dcim.devices.get(name=name)
    if not nb_device:
        return {'success': False,
                'error': 'unknown device'}

    # get interface
    interface = nb.dcim.interfaces.get(
        device_id=nb_device.id,
        name=interface
    )
    if interface is None:
        return {'success': False,
                'error': 'unknown interface %s' % interface}

    if 'lag' in newconfig:
        lag_interface = nb.dcim.interfaces.get(
            device_id=nb_device.id,
            name=newconfig['lag']
        )
        # now set LAG interface
        interface.lag = lag_interface

    if 'mode' in newconfig:
        interface.mode = newconfig['mode']

    if 'untagged' in newconfig:
        (untagged_vlan, success) = get_vlan(nb, newconfig['untagged'], newconfig['site'])
        if success and untagged_vlan is not None:
            interface.untagged_vlan = untagged_vlan
        else:
            return {'success': False,
                    'error': 'unknown untagged vlan'}

    if 'tagged' in newconfig:
        vlans = newconfig['tagged'].split(",")
        tagged = []
        for vlan in vlans:
            (tv, success) = get_vlan(nb, vlan, newconfig['site'])
            if success and tv is not None:
                tagged.append(tv)
            else:
                return {'success': False,
                        'error': 'unknown tagged vlan %s' % vlan}
        interface.tagged_vlans = tagged

    if 'tags' in newconfig:
        if newconfig['tags'] == "":
            interface.tags = []
        else:
            try:
                tags = [nb.extras.tags.get(name=tag).id for tag in newconfig["tags"].split(',')]
                interface.tags = tags
            except Exception as exc:
                return {'success': False,
                        'error': 'unknown tag found; exception: %s' % exc}

    try:
        success = interface.save()
    except Exception as exc:
        return {'success': False,
                'error': 'got exception %s' % exc}

    if success:
        return {'success': True,
                'id': 2,
                'log': 'interface updated (%s)' % values}
    else:
        return {'success': True,
                'id': 3,
                'error': 'no changes made on interface'}


def update_device_values(name, newconfig):

    config = helper.read_config()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])
    values = ', '.join(map(str, newconfig.values()))

    # get device
    nb_device = nb.dcim.devices.get(name=name)
    if not nb_device:
        return {'success': False,
                'error': 'unknown device %s' % name}

    if 'name' in newconfig:
        nb_device.name = newconfig['name']

    if 'slug' in newconfig:
        nb_device.slug = newconfig['slug']

    if 'device_type' in newconfig:
        nb_devicetype = nb.dcim.device_types.get(slug=newconfig['device_type'])
        if nb_devicetype is None:
            return {'success': False,
                    'error': 'unknown type %s' % newconfig['device_type']}
        nb_device.device_type = nb_devicetype.id

    if 'device_role' in newconfig:
        nb_role = nb.dcim.device_roles.get(slug=newconfig['device_role'])
        if nb_role is None:
            return {'success': False,
                    'error': 'unknown role %s' % newconfig['device_role']}
        nb_device.device_role = nb_role.id

    if 'serial' in newconfig:
        nb_device.serial = newconfig['serial']

    if 'site' in newconfig:
        nb_site = nb.dcim.sites.get(slug=newconfig['site'])
        if nb_site is None:
            return {'success': False,
                    'error': 'unknown site %s' % newconfig['site']}
        nb_device.site = nb_site

    if 'location' in newconfig:
        nb_location = nb.dcim.locations.get(slug=newconfig['location'])
        if nb_location is None:
            return {'success': False,
                    'error': 'unknown location %s' % newconfig['location']}
        nb_device.location = nb_location.id

    if 'manufacturer' in newconfig:
        nb_manufacturer = nb.dcim.manufacturers.get(slug=newconfig['manufacturer'])
        if nb_manufacturer is None:
            return {'success': False,
                    'error': 'unknown manufacturer %s' % newconfig['manufacturer']}
        nb_device.manufacturer = nb_manufacturer.id

    if 'platform' in newconfig:
        nb_platform = nb.dcim.platforms.get(slug=newconfig['platform'])
        if nb_platform is None:
            return {'success': False,
                    'error': 'unknown platform %s' % newconfig['platform']}
        nb_device.platform = nb_platform.id

    if 'primary_ip4' in newconfig:
        nb_ipadd = nb.ipam.ip_addresses.get(
            address=newconfig['primary_ip4']
        )

        if nb_ipadd is None:
            # unknown IP. Let's add it and assign it to device
            nb_ipadd = nb.ipam.ip_addresses.create(
                address=newconfig['primary_ip4'],
                status='active',
                assigned_object_type="dcim.interface",
                assigned_object_id=nb.dcim.interfaces.get(
                    device=nb_device,
                    name=newconfig["interface"]).id
            )
        nb_device.primary_ip4 = nb_ipadd.id

    if 'comments' in newconfig:
        nb_device.comments = newconfig['comments']

    if 'tags' in newconfig:
        if newconfig['tags'] == "":
            nb_device.tags = []
        else:
            tags = [nb.extras.tags.get(name=tag).id for tag in newconfig["tags"].split(',')]
            nb_device.tags = tags

    if 'status' in newconfig:
        nb_device.status = newconfig['status']

    try:
        success = nb_device.save()
    except Exception as exc:
        return {'success': False,
                'error': 'got exception %s' % exc}

    if success:
        return {'success': True,
                'id': 2,
                'log': 'device updated (%s)' % values}
    else:
        return {'success': True,
                'id': 3,
                'log': 'no changes made to device'}


def update_site_values(slug, newconfig):

    config = helper.read_config()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    nb_site = nb.dcim.sites.get(slug=slug)
    if nb_site is  None:
        return {'success': False,
                'error': 'site %s is not in sot' % name}

    if 'slug' in newconfig:
        nb_site.slug = newconfig['slug']
    if 'name' in newconfig:
        nb_site.name = newconfig['name']
    if 'asn' in newconfig:
        nb_site.asn = newconfig['asn']
    if "time_zone" in newconfig:
        nb_site.time_zone = newconfig["time_zone"]
    if "description" in newconfig:
        nb_site.description = newconfig["description"]
    if "physical_address" in newconfig:
        nb_site.physical_address = newconfig["physical_address"]
    if "shipping_address" in newconfig:
        nb_site.shipping_address = newconfig["shipping_address"]
    if "latitude" in newconfig:
        nb_site.latitude = newconfig["latitude"]
    if "longitude" in newconfig:
        nb_site.longitude = newconfig["longitude"]
    if "contact_name" in newconfig:
        nb_site.contact_name = newconfig["contact_name"]
    if "contact_phone" in newconfig:
        nb_site.contact_phone = newconfig["contact_phone"]
    if "contact_email" in newconfig:
        nb_site.contact_email = newconfig["contact_email"]
    if "comments" in newconfig:
        nb_site.comments = newconfig["comments"]

    try:
        success = nb_site.save()
    except Exception as exc:
        return {'success': False,
                'error': 'got exception %s' % exc}

    if success:
        return {'success': True,
                'id': 2,
                'log': 'site updated'}
    else:
        return {'success': True,
                'id': 3,
                'log': 'no changes made to site'}


def update_manufacturer_values(slug, newconfig):

    config = helper.read_config()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    nb_manufacturer = nb.dcim.manufacturers.get(slug=slug)
    if nb_manufacturer is  None:
        return {'success': False,
                'error': 'manufacturer %s is not in sot' % slug}

    if 'slug' in newconfig:
        nb_manufacturer.slug = newconfig['slug']
    if 'name' in newconfig:
        nb_manufacturer.name = newconfig['name']
    if 'description' in newconfig:
        nb_manufacturer.description = newconfig['description']

    try:
        success = nb_manufacturer.save()
    except Exception as exc:
        return {'success': False,
                'error': 'got exception %s' % exc}

    if success:
        return {'success': True,
                'id': 1,
                'log': 'manufacturer updated'}
    else:
        return {'success': True,
                'id': 3,
                'log': 'no changes made to manufacturer'}


def update_platform_values(slug, newconfig):

    config = helper.read_config()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    nb_platform = nb.dcim.platforms.get(slug=slug)
    if nb_platform is  None:
        return {'success': False, 'error': 'platform %s is not in sot' % slug}

    if 'slug' in newconfig:
        nb_platform.slug = newconfig['slug']
    if 'name' in newconfig:
        nb_platform.name = newconfig['name']
    if 'description' in newconfig:
        nb_platform.description = newconfig['description']
    if 'manufacturer' in newconfig:
        nb_manufacturer = nb.dcim.manufacturers.get(slug=newconfig['manufacturer'])
        if nb_manufacturer is not None:
            nb_platform.manufacturer = nb_manufacturer.id
    if 'napalm_driver' in newconfig:
        nb_platform.napalm_driver = newconfig['napalm_driver']
    if 'napalm_args' in newconfig:
        nb_platform.napalm_args = newconfig['napalm_args']

    try:
        success = nb_platform.save()
    except Exception as exc:
        return {'success': False,
                'error': 'got exception %s' % exc}

    if success:
        return {'success': True,
                'id': 1,
                'log': 'platform updated'}
    else:
        return {'success': True,
                'id': 3,
                'log': 'no changes made to platform'}


def update_connection_values(newconfig):

    config = helper.read_config()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    # get side a
    side_a = nb.dcim.devices.get(name=newconfig['side_a'])
    if not side_a:
        return {'success': False,
                'error': 'unknown device %s' % newconfig['side_a']}

    # get side b
    side_b = nb.dcim.devices.get(name=newconfig['side_b'])
    if not side_b:
        return {'success': False,
                'error': 'unknown device %s' % newconfig['side_b']}

    # get interface a
    interface_a = nb.dcim.interfaces.get(
        device_id=side_a.id,
        name=newconfig['interface_a']
    )
    if interface_a is None:
        return {'success': False,
                'error': 'unknown interface %s' % newconfig['interface_a']}

    # get interface b
    interface_b = nb.dcim.interfaces.get(
        device_id=side_b.id,
        name=newconfig['interface_b']
    )
    if interface_b is None:
        return {'success': False,
                'error': 'unknown interface %s' % newconfig['interface_b']}

    cable = nb.dcim.cables.get(
            termination_a_type="dcim.interface",
            termination_a_id=interface_a.id,
            termination_b_type="dcim.interface",
            termination_b_id=interface_b.id,
        )

    if cable is None:
        try:
            # now create connection
            nb.dcim.cables.create(
                termination_a_type="dcim.interface",
                termination_a_id=interface_a.id,
                termination_b_type="dcim.interface",
                termination_b_id=interface_b.id,
                type="cat5e",
                status="connected"
            )
            return {'success': True,
                    'id': 0,
                    'log': 'connection added to sot'}
        except Exception as exc:
            return {'success': False,
                    'error': 'got exception %s' % exc}
    else:
        return {'success': True,
                'id': 1,
                'log': 'cable already in sot'}


def get_choices(item):

    config = helper.read_config()
    nb = api(url=config['nautobot']['url'], token=config['nautobot']['token'])

    if item == 'device':
        return nb.dcim.devices.choices()
    elif item == "interfaces":
        return nb.dcim.interfaces.choices()


def get_vlan(nb, vid, site=""):

    if len(site) > 0:
        # site specific VLAN
        if nb.dcim.sites.get(slug=site) == None:
            return (None, False)
        else:
            site_id = nb.dcim.sites.get(slug=site).id
            nb_vlan = nb.ipam.vlans.get(
                site=site_id,
                vid=vid,
            )
    else:
        # global VLAN
        nb_vlan = nb.ipam.vlans.get(
            vid=vid,
        )

    return (nb_vlan, True)

#
# def update_device_json(name, newconfig):
#
#     print(newconfig)
#     return {}