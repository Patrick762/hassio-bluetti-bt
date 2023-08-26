"""Tools."""

def mac_loggable(mac: str) -> str:
    """Remove parts of the mac address for logging."""
    splitted = mac.split(":")
    return "XX:XX:XX:XX:XX:" + splitted[-1]

def unique_id_loggable(unique_id: str) -> str:
    """Remove parts of the unique id for logging."""
    splitted = unique_id.split("_", maxsplit=1)
    serial = splitted[0][:6]
    return serial + "XXXXXXXXXX" + splitted[1]
