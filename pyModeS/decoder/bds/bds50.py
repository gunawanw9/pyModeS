# ------------------------------------------
# BDS 5,0
# Track and turn report
# ------------------------------------------

from pyModeS import common


def is50(msg):
    """Check if a message is likely to be BDS code 5,0
    (Track and turn report)

    Args:
        msg (str): 28 hexdigits string

    Returns:
        bool: True or False
    """

    if common.allzeros(msg):
        return False

    d = common.hex2bin(common.data(msg))

    # status bit 1, 12, 24, 35, 46

    if common.wrongstatus(d, 1, 3, 11):
        return False

    if common.wrongstatus(d, 12, 13, 23):
        return False

    if common.wrongstatus(d, 24, 25, 34):
        return False

    if common.wrongstatus(d, 35, 36, 45):
        return False

    if common.wrongstatus(d, 46, 47, 56):
        return False

    roll = roll50(msg)
    if (roll is not None) and abs(roll) > 60:
        return False

    gs = gs50(msg)
    if gs is not None and gs > 600:
        return False

    tas = tas50(msg)
    if tas is not None and tas > 500:
        return False

    if (gs is not None) and (tas is not None) and (abs(tas - gs) > 200):
        return False

    return True


def roll50(msg):
    """Roll angle, BDS 5,0 message

    Args:
        msg (str): 28 hexdigits (BDS50) string

    Returns:
        float: angle in degrees,
               negative->left wing down, positive->right wing down
    """
    d = common.hex2bin(common.data(msg))

    if d[0] == "0":
        return None

    sign = int(d[1])  # 1 -> left wing down
    value = common.bin2int(d[2:11])

    if sign:
        value = value - 512

    angle = value * 45.0 / 256.0  # degree
    return round(angle, 1)


def trk50(msg):
    """True track angle, BDS 5,0 message

    Args:
        msg (str): 28 hexdigits (BDS50) string

    Returns:
        float: angle in degrees to true north (from 0 to 360)
    """
    d = common.hex2bin(common.data(msg))

    if d[11] == "0":
        return None

    sign = int(d[12])  # 1 -> west
    value = common.bin2int(d[13:23])

    if sign:
        value = value - 1024

    trk = value * 90.0 / 512.0

    # convert from [-180, 180] to [0, 360]
    if trk < 0:
        trk = 360 + trk

    return round(trk, 3)


def gs50(msg):
    """Ground speed, BDS 5,0 message

    Args:
        msg (str): 28 hexdigits (BDS50) string

    Returns:
        int: ground speed in knots
    """
    d = common.hex2bin(common.data(msg))

    if d[23] == "0":
        return None

    spd = common.bin2int(d[24:34]) * 2  # kts
    return spd


def rtrk50(msg):
    """Track angle rate, BDS 5,0 message

    Args:
        msg (str): 28 hexdigits (BDS50) string

    Returns:
        float: angle rate in degrees/second
    """
    d = common.hex2bin(common.data(msg))

    if d[34] == "0":
        return None

    if d[36:45] == "111111111":
        return None

    sign = int(d[35])  # 1 -> negative value, two's complement
    value = common.bin2int(d[36:45])
    if sign:
        value = value - 512

    angle = value * 8.0 / 256.0  # degree / sec
    return round(angle, 3)


def tas50(msg):
    """Aircraft true airspeed, BDS 5,0 message

    Args:
        msg (str): 28 hexdigits (BDS50) string

    Returns:
        int: true airspeed in knots
    """
    d = common.hex2bin(common.data(msg))

    if d[45] == "0":
        return None

    tas = common.bin2int(d[46:56]) * 2  # kts
    return tas
