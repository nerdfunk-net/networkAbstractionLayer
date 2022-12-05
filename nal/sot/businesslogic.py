def business_logic(device, hldm):
    """

    Args:
        device:
        hldm:

    Returns:

    """

    # put your business logic here

    """
    the low level data model (lldm) does NOT contain any tags or custom fields.
    To get the lldm, get your high level data model (hldm) and replace all tags 
    and custom fields.
    
    e.g. if the hldm contains a tag 'ospf' on some interfaces add your ospf 
    config to the hldm interface config instead.
    
    The interface jinja template should not use any other data than 
    the interface lldm config when rendering the config.
    
    """
    lldm = hldm

    return lldm

