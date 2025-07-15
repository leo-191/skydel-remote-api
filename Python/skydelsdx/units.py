#!/usr/bin/env python3

import math

ESMAJ = 6378137.0 # Semi-major axis of Earth, meters
EFLAT = 0.00335281066474
ESMIN = ESMAJ * (1.0 - EFLAT)
EECC_SQUARED = (((ESMAJ*ESMAJ) - (ESMIN*ESMIN)) / (ESMAJ*ESMAJ))
Pi    = 3.1415926535898 # Pi used in the GPS coordinate

def toRadian(degree: float) -> float:
  return degree / 180.0 * Pi

def toDegree(radian: float) -> float:
  return radian / Pi * 180.0

class Lla:
  """A geodetic (Latitude Longitude Altitude, LLA) coordinate.
  """
  def __init__(self, lat: float, lon: float, alt: float = 0) -> None:
    """
    Parameters
    ----------
    lat : float
        Latitude in radians
    lon : float
        Longitude in radians
    alt : float, optional
        Altitude in meters, by default 0
    """
    self.lat = lat
    self.lon = lon
    self.alt = alt

  def addEnu(self, enu: "Enu") -> "Lla":
    """Convert an ENU coordinate point to an LLA coordinate point with the current coordinate point as the origin.

    Parameters
    ----------
    enu : Enu
        An ENU coordinate point to be converted.

    Returns
    -------
    Lla
        The converted coordinates in LLA format.
    """
    return enu.toLla(self)

  def toEcef(self) -> "Ecef":
    """Convert the LLA coordinate point into an ECEF coordinate point.

    Returns
    -------
    Ecef
        The converted coordinates in ECEF format.
    """
    cos_lat = math.cos(self.lat)
    tmp = (1-EFLAT)*(1-EFLAT)
    ex2 = (2-EFLAT)*EFLAT/tmp
    c = ESMAJ*math.sqrt(1+ex2)
    n = c/math.sqrt(1+ex2*cos_lat*cos_lat)
    return Ecef((n+self.alt)*cos_lat*math.cos(self.lon),(n+self.alt)*cos_lat*math.sin(self.lon), (tmp*n+self.alt)*math.sin(self.lat))

  def toEnu(self, origin: "Lla"):
    return Enu((self.lon - origin.lon) * ESMAJ * math.cos(self.lat),  (self.lat - origin.lat) * ESMAJ, self.alt - origin.alt)

  def latDeg(self) -> float:
    return toDegree(self.lat)

  def lonDeg(self) -> float:
    return toDegree(self.lon)

  def __str__(self):
   return u"%.7fdeg, %.7fdeg, %.2fm" % (self.latDeg(), self.lonDeg(), self.alt)

  def __add__(self, other):
    return Lla(self.lat + other.lat, self.lon + other.lon, self.alt + other.alt)

  def __eq__(self, other):
    return self.lat == other.lat and self.lon == other.lon and self.alt == other.alt

  def __ne__(self, other):
    return not (self == other)

class Enu:
  """An ENU (East, North, Up) coordinate.
  """
  def __init__(self, east:float, north: float, up: float=0):
    """
    Parameters
    ----------
    east : float
        East deviation in meters
    north : float
        North deviation in meters
    up : float, optional
        Up deviation in meters, by default 0
    """
    self.east = east
    self.north = north
    self.up = up

  def toEcef(self, originLla: Lla) -> "Ecef":
    """Convert the ENU coordinate points to an ECEF coordinate points based on the specified origin coordinates.

    Parameters
    ----------
    originLla : Lla
        The origin coordinates in LLA format.
        This serves as the reference point for the ENU coordinate system.

    Returns
    -------
    Ecef
        The converted coordinates in ECEF format.
    """
    originEcef = originLla.toEcef()
    sinLon = math.sin(originLla.lon)
    cosLon = math.cos(originLla.lon)
    sinLat = math.sin(originLla.lat)
    cosLat = math.cos(originLla.lat)

    x = -sinLon * self.east - sinLat * cosLon * self.north + cosLat * cosLon * self.up + originEcef.x
    y = cosLon * self.east - sinLat * sinLon * self.north + cosLat * sinLon * self.up + originEcef.y
    z = cosLat * self.north + sinLat * self.up + originEcef.z

    return Ecef(x, y, z)

  def toLla(self, originLla: Lla) -> Lla:
    """Convert an ENU coordinate points to an LLA coordinate points based on the specified origin coordinates.

    Parameters
    ----------
    originLla : Lla
        The origin coordinates in LLA format.
        This serves as the reference point for the ENU coordinate system.

    Returns
    -------
    Lla
        The converted coordinates in LLA format.
    """
    return self.toEcef(originLla).toLla()

  def __str__(self):
    return "%.2fm East, %.2fm North, %.2fm Up" % (self.east, self.north, self.up)

  def __add__(self, other):
    return Enu(self.east + other.east, self.north + other.north, self.up + other.up)

  def __eq__(self, other):
    return self.east == other.east and self.north == other.north and self.up == other.up

  def __ne__(self, other):
    return not (self == other)

class Ecef:
  """An ECEF (Earth Centered-Earth Fixed) coordinate.
  """
  def __init__(self, x: float, y: float, z: float) -> None:
    self.x = x
    self.y = y
    self.z = z

  def toLla(self) -> Lla:
    dist_to_z = math.sqrt(self.x*self.x + self.y*self.y)
    lat = math.atan2(self.z, (1 - EECC_SQUARED) * dist_to_z)
    for i in range(1, 5):
      sin_lat = math.sin(lat)
      radius_p = ESMAJ / math.sqrt(1.0 - EECC_SQUARED * sin_lat * sin_lat)
      lat = math.atan2(self.z + EECC_SQUARED * radius_p * sin_lat, dist_to_z)
    lon = math.atan2(self.y, self.x)
    if toDegree(lat) < -85 or toDegree(lat) > 85:
      L = self.z + EECC_SQUARED * radius_p * math.sin(lat)
      alt = L / math.sin(lat) - radius_p
    else:
      alt = dist_to_z / math.cos(lat) - radius_p
    return Lla(lat, lon, alt)

  def __str__(self):
   return u"%.2fm, %.2fm, %.2fm" % (self.x, self.y, self.z)

  def __add__(self, other):
    return Lla(self.x + other.x, self.y + other.y, self.z + other.z)

  def __eq__(self, other):
    return self.x == other.x and self.y == other.y and self.z == other.z

  def __ne__(self, other):
    return not (self == other)

class Attitude:
  def __init__(self, yaw: float, pitch: float, roll: float) -> None:
    """
    Parameters
    ----------
    yaw : float
        Yaw in radians
    pitch : float
        Pitch in radians
    roll : float
        Roll in radians
    """
    self.yaw = yaw
    self.pitch = pitch
    self.roll = roll

  def __str__(self):
    return u"%.2fdeg, %.2fdeg, %.2fdeg" % (self.yawDeg(), self.pitchDeg(), self.rollDeg())

  def __add__(self, other):
    return Attitude(self.yaw + other.yaw, self.pitch + other.pitch, self.roll + other.roll)

  def __eq__(self, other):
    return self.yaw == other.yaw and self.pitch == other.pitch and self.roll == other.roll

  def __ne__(self, other):
    return not (self == other)

  def yawDeg(self):
    return toDegree(self.yaw)

  def pitchDeg(self):
    return toDegree(self.pitch)

  def rollDeg(self):
    return toDegree(self.roll)

