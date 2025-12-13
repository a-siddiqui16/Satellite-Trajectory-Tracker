from skyfield.api import EarthSatellite, load
from tle_fetcher import fetch_satellite_tle
import math

ts = load.timescale()

satellite_id = input("Enter NORAD ID: ")
satellite_info = fetch_satellite_tle(satellite_id)

satellite_name = satellite_info[name]
line1 = satellite_info[line1]
line2 = satellite_info[line2]

#Create satellite object
satellite = EarthSatellite(line1, line2, satellite_name, ts)

def classify_orbit(sat):

    #Orbital parameters
    i = sat.model.inclo * 180 / 3.14159  #inclination (degrees)
    n = sat.model.no_kozai * 60 * 24 / (2 * math.pi)  #rev/day

    mu = 398600.4418  #Earth's gravitational parameter

    a = (mu ** (1 / 3)) / ((2 * 3.14159 * n / 86400) ** (2 / 3))  #semi-major axis (km)
    h = a - 6371  #approximate altitude (km)

    #Orbit type classification
    if h < 2000:
        orbit = "LEO (Low Earth Orbit)"
    elif h < 35786:
        orbit = "MEO (Medium Earth Orbit)"
    elif abs(h - 35786) < 500:
        orbit = "GEO (Geostationary Orbit)"
    else:
        orbit = "HEO (High Earth Orbit)"

    #Inclination
    if abs(i - 90) < 5:
        orbit += "Polar"
    elif 97 < i < 99:
        orbit += "Sun-Synchronous"

    return orbit, h, i

#Pass the full satellite object and retrieve the orbit type
orbit_type = classify_orbit(satellite)

print()


