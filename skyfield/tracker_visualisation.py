import sqlite3
from vpython import *
from skyfield.api import EarthSatellite, load, wgs84
from tle_fetcher import fetch_satellite_tle, tle_parser
from orbital_calculations import classify_orbit
from datetime import datetime


db_path = "satellite_database.db"

earth_radius_km = 6378
satellite_size = 50
trail_size = 10


def calculate_speed(velocity):
    return (velocity[0]**2 + velocity[1]**2 + velocity[2]**2) ** 0.5



def store_satellite_data(norad_id):

    satellite_data = fetch_satellite_tle(norad_id)
    if not satellite_data:
        print("Could not fetch satellite data")
        return False
    
    norad_id, satellite_name, tle_line1, tle_line2 = satellite_data
    satellite = EarthSatellite(tle_line1, tle_line2, satellite_name, ts)
    orbit_type, altitude, inclination = classify_orbit(satellite)

    

    #Extracting values so I can put them in the database
    data_parameters = tle_parser(tle_line1, tle_line2)
    eccentricity = float("0." + data_parameters['eccentricity'])
    mean_motion = float(data_parameters['mean_motion'])
    epoch_day = data_parameters['epoch_day']
    epoch_year = data_parameters['epoch_year']

    if int(epoch_year) < 57: #No satellites exist before 1957
        full_year = 2000 + int(epoch_year)   #Example # 00-56 → 2000-2056
    else:
        full_year = 1900 + int(epoch_year)   #Example 57-99 → 1957-1999
    
    epoch_date = f"{full_year}-{epoch_day}"


    try:
        with sqlite3.connect(db_path) as conn:

            c = conn.cursor()

            c.execute("""INSERT OR IGNORE INTO Satellites
                    (norad_id, satellite_name, satellite_type)
                    VALUES (?, ?, ?)""",
                    (norad_id, satellite_name, None))
            
            c.execute("""INSERT INTO TLE_Data 
                        (norad_id, tle_line1, tle_line2, orbit_type, 
                        inclination, eccentricity, mean_motion, epoch_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (norad_id, tle_line1, tle_line2, orbit_type,
                    inclination, eccentricity, mean_motion, epoch_date))
            
            conn.commit()

        return True
    
    except sqlite3.Error as e:
        print("Error")
        return False


ts = load.timescale()
norad_id = int(input("ENTER NORAD ID: "))
satellite_data = fetch_satellite_tle(norad_id)

store_satellite_data(norad_id)

# if satellite_data:

#     norad_id, satellite_name, tle_line1, tle_line2 = satellite_data
#     satellite_object = EarthSatellite(tle_line1, tle_line2, satellite_name, ts)
#     orbit_type, altitude, inclination = classify_orbit(satellite_object)


#     scene = canvas(width=900, height=700, background=color.black)
#     scene.title = "Satellite Trajectory Tracker"
#     scene.append_to_caption("Satellite Info\n")
#     info_box = wtext(text="Current satellite data\n")


#     distant_light(direction=vec(1,1,0), color=color.yellow)
#     earth = sphere(pos=vector(0,0,0), radius=earth_radius_km, texture=textures.earth)

#     satellite_dot = sphere(radius=satellite_size, color=color.green, make_trail=True, trail_radius=trail_size, trail_color=color.red)
#     info_label = label(pos=satellite_dot.pos, text='', height=16, border=3, font='sans')
    
#     while True:
#         rate(60)

#         t = ts.now()

#         #Getting ECI coordinates from TLE Data
#         geocentric = satellite_object.at(t)
#         x, y, z = geocentric.position.km

#         satellite_dot.pos = vector(x,y,z)
#         info_label.pos = satellite_dot.pos + vector(0, satellite_size, 0)

#         subpoint = wgs84.subpoint(geocentric)
#         lat = subpoint.latitude.degrees
#         lon = subpoint.longitude.degrees
#         height = subpoint.elevation.km
#         velocity = geocentric.velocity.km_per_s
#         speed = calculate_speed(velocity)


#         #Used 2 decimal places 
#         info_text = f"{satellite_name}\n"
#         info_text += f"Latitude: {lat:.2f}°\n" 
#         info_text += f"Longitude: {lon:.2f}°\n"
#         info_text += f"Altitude: {height:.2f}\n"
#         info_text += f"Velocity: {speed:.2f}\n"
#         info_text += f"Orbit Type: {orbit_type}\n"

#         info_box.text = info_text
#         info_label.text = f"{satellite_name}"
        

# else:
#     print("Falied to retrieve data")




    

