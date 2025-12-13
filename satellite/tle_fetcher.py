import requests
import time

def fetch_satellite_tle(norad_id):

    #Built URL that fetches TLE data for any satellite
    url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=tle"


    try: 
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.text.strip()

            if not data:
                print("TLE Data not found")
                return None

            lines = data.split('\n')

            if len(lines) < 3:
                print("Invalid TLE data format")
                return None

            satellite_name = lines[0].strip()
            tle_line1 = lines[1].strip()
            tle_line2 = lines[2].strip()

            return norad_id, satellite_name, tle_line1, tle_line2
    
        else:
            print(response.status_code)
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    



#Line 1: 1 25544U 98067A   22001.74462497  .00001435  00000-0  34779-4 0  9992
#Line 2: 2 25544  51.6464  24.2704 0004064  69.5467 290.6355 15.48835264296862


def tle_parser(tle_line1, tle_line2):

    #Extracting TLE Parameters and putting them into a dictionary

    return {

        #Line 1
        "satellite_number": tle_line1[2:7].strip(),
        "classification": tle_line1[7].strip(),
        "international_designator": tle_line1[9:17].strip(),
        "epoch_year": tle_line1[18:20].strip(),
        "epoch_day": tle_line1[20:32].strip(),
        "first_derivative": tle_line1[33:43].strip(),
        "second_derivative": tle_line1[44:52].strip(),
        "bstar_drag": tle_line1[53:61].strip(),
        "ephemeris_type": tle_line1[62].strip(),
        "element_number": tle_line1[64:68].strip(),

        #Line 2
        "inclination": tle_line2[8:16].strip(),
        "right_ascension": tle_line2[17:25].strip(),
        "eccentricity": tle_line2[26:33].strip(),
        "argument_of_perigee": tle_line2[34:42].strip(),
        "mean_anomaly": tle_line2[43:51].strip(),
        "mean_motion": tle_line2[52:63].strip(),
        "revolution_number": tle_line2[63:68].strip()

    }


