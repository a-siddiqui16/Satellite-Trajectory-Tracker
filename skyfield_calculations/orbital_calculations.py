# from skyfield.api import EarthSatellite, load
# from tle_fetcher import fetch_satellite_tle
# import math

# #Constants

# earth_radius_km = 6378
# earth_mu = 398600.4418
# geo_altitude = 35786
# pi = math.pi


# ts = load.timescale()

# def classify_orbit(sat):

#     #Orbital parameters
#     i = sat.model.inclo * 180 / pi  #inclination (degrees)
#     n = sat.model.no_kozai * 60 * 24 / (2 * pi)  #rev/day

#     mu = 398600.4418  #Earth's gravitational parameter

#     a = (mu ** (1 / 3)) / ((2 * pi * n / 86400) ** (2 / 3))  #semi-major axis (km)
#     h = a - earth_radius_km  #approximate altitude (km)

#     #Orbit type classification
#     if h < 2000:
#         orbit = "LEO (Low Earth Orbit)"
#     elif h < 35786:
#         orbit = "MEO (Medium Earth Orbit)"
#     elif abs(h - 35786) < 500:
#         orbit = "GEO (Geostationary Orbit)"
#     else:
#         orbit = "HEO (High Earth Orbit)"

#     #Inclination
#     if abs(i - 90) < 5:
#         orbit += "Polar"
#     elif 97 < i < 99:
#         orbit += "Sun-Synchronous"

#     return orbit, h, i


# def get_satellite_info(norad_id):

#     satellite_data = fetch_satellite_tle(norad_id) 

#     if not satellite_data:
#         print("Failed to retrieve satellite data")
#         return None
    
#     satellite = EarthSatellite(line1, line2, satellite_name, ts)
#     returned_norad_id, satellite_name, line1, line2 = satellite_data
#     orbit_type, altitude, inclination = classify_orbit(satellite)

#     return {
#         'norad_id': returned_norad_id,
#         'satellite_name': satellite_name,
#         'tle_line1': line1,
#         'tle_line2': line2,
#         'satellite_object': satellite,
#         'orbit_type': orbit_type,
#         'altitude_km': altitude,
#         'inclination_deg': inclination
#     }


from skyfield.api import EarthSatellite, load
from propagator import planetary_data
import math
from skyfield_calculations import tle_fetcher

cb = planetary_data.earth

#Constants
earth_radius_km = cb["radius"]
earth_mu = cb["mu"]
geo_altitude = 35786
pi = math.pi

ts = load.timescale()

def classify_orbit(sat):
    # Orbital parameters
    i = sat.model.inclo * 180 / pi  # inclination (degrees)
    n = sat.model.no_kozai * 60 * 24 / (2 * pi)  # rev/day

    mu = earth_mu

    a = (mu ** (1 / 3)) / ((2 * pi * n / 86400) ** (2 / 3))  # semi-major axis (km)
    h = a - earth_radius_km  # approximate altitude (km)

    # Orbit type classification
    if h < 2000:
        orbit = "LEO (Low Earth Orbit)"

    elif h < 35786:
        orbit = "MEO (Medium Earth Orbit)"

    elif abs(h - 35786) < 500:
        orbit = "GEO (Geostationary Orbit)"

    else:
        orbit = "HEO (High Earth Orbit)"

    # Inclination
    if abs(i - 90) < 5:
        orbit += " - Polar"

    elif 97 < i < 99:
        orbit += " - Sun-Synchronous"

    return orbit, h, i


def get_satellite_info(norad_id):
    
    satellite_data = tle_fetcher.fetch_satellite_tle(norad_id) 

    if not satellite_data:
        print("Failed to retrieve satellite data")
        return None
    
    returned_norad_id, satellite_name, line1, line2 = satellite_data
    satellite = EarthSatellite(line1, line2, satellite_name, ts)
    orbit_type, altitude, inclination = classify_orbit(satellite)

    return {
        'norad_id': returned_norad_id,
        'satellite_name': satellite_name,
        'tle_line1': line1,
        'tle_line2': line2,
        'satellite_object': satellite,
        'orbit_type': orbit_type,
        'altitude_km': altitude,
        'inclination_deg': inclination
    }


