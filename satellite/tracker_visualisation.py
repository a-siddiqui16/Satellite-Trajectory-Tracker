from vpython import *
from skyfield.api import EarthSatellite, load, wgs84
from tle_fetcher import fetch_satellite_tle
from orbital_calculations import classify_orbit

earth_radius_km = 6378
satellite_size = 50
trail_size = 10


ts = load.timescale()


norad_id = int(input("ENTER NORAD ID: "))
satellite_data = fetch_satellite_tle(norad_id)


def calculate_speed(velocity):
    return (velocity[0]**2 + velocity[1]**2 + velocity[2]**2) ** 0.5

if satellite_data:

    norad_id, satellite_name, tle_line1, tle_line2 = satellite_data
    satellite_object = EarthSatellite(tle_line1, tle_line2, satellite_name, ts)
    orbit_type, altitude, inclination = classify_orbit(satellite_object)


    scene = canvas(width=900, height=700, background=color.black)
    scene.title = "Satellite Trajectory Tracker"
    scene.append_to_caption("satellite Info\n")
    info_box = wtext(text="Current satellite data\n")


    distant_light(direction=vec(1,1,0), color=color.yellow)
    earth = sphere(pos=vector(0,0,0), radius=earth_radius_km, texture=textures.earth)

    satellite_dot = sphere(radius=satellite_size, color=color.green, make_trail=True, trail_radius=trail_size, trail_color=color.red)
    info_label = label(pos=satellite_dot.pos, text='', height=16, border=3, font='sans')
    
    while True:
        rate(60)


        t = ts.now()

        #Getting ECI coordinates from TLE Data
        geocentric = satellite_object.at(t)
        x, y, z = geocentric.position.km

        satellite_dot.pos = vector(x,y,z)
        info_label.pos = satellite_dot.pos + vector(0, satellite_size, 0)

        subpoint = wgs84.subpoint(geocentric)
        lat = subpoint.latitude.degrees
        lon = subpoint.longitude.degrees
        height = subpoint.elevation.km
        velocity = geocentric.velocity.km_per_s
        speed = calculate_speed(velocity)


        #Used 2 decimal places 
        info_text = f"{satellite_name}\n"
        info_text += f"Latitude: {lat:.2f}°\n" 
        info_text += f"Longitude: {lon:.2f}°\n"
        info_text += f"Altitude: {height:.2f}\n"
        info_text += f"Velocity: {speed:.2f}\n"
        info_text += f"Orbit Type: {orbit_type}\n"

        info_box.text = info_text
        info_label.text = f"{satellite_name}"
        


else:
    print("Falied to retrieve data")



