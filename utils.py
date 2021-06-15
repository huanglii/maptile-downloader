from math import floor, pi, log, tan, atan, exp


def wgs_to_mercator(x, y):
    """
    WGS-84 to Web Mercator
    :param x: longitude
    :param y: latitude
    :return:
    """
    y = 85.0511287798 if y > 85.0511287798 else y
    y = -85.0511287798 if y < -85.0511287798 else y

    x2 = x * 20037508.34 / 180
    y2 = log(tan((90 + y) * pi / 360)) / (pi / 180)
    y2 = y2 * 20037508.34 / 180
    return x2, y2


def mercator_to_wgs(x, y):
    """
    Web Mercator to WGS-84
    :param x: x
    :param y: y
    :return:
    """
    x2 = x / 20037508.34 * 180
    y2 = y / 20037508.34 * 180
    y2 = 180 / pi * (2 * atan(exp(y2 * pi / 180)) - pi / 2)
    return x2, y2


# Get tile coordinates in Google Maps based on latitude and longitude of WGS-84
def wgs_to_tile(lon, lat, zoom):
    """
    Get google-style tile cooridinate from geographical coordinate
    lon : Longittude
    lat : Latitude
    zoom : zoom
    """
    def is_num(n):
        return isinstance(n, int) or isinstance(n, float)

    if not (is_num(lon) and is_num(lat)):
        raise TypeError("lon and lat must be int or float!")

    if not isinstance(zoom, int) or zoom < 0 or zoom > 20:
        raise TypeError("zoom must be int and between 0 to 20.")

    if lon < 0:
        lon = 180 + lon
    else:
        lon += 180
    lon /= 360  # make lon to (0,1)

    lat = 85.0511287798 if lat > 85.0511287798 else lat
    lat = -85.0511287798 if lat < -85.0511287798 else lat
    lat = log(tan((90 + lat) * pi / 360)) / (pi / 180)
    lat /= 180  # make lat to (-1,1)
    lat = 1 - (lat + 1) / 2  # make lat to (0,1) and left top is 0-point

    num = 2 ** zoom
    x = floor(lon * num)
    y = floor(lat * num)
    return x, y
