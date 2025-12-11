import requests

def fetch_satellite_tle(norad_id):

    #Built URL that fetches TLE data for any satellite
    url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=tle"

    response = requests.get(url)

    if response.status_code == 200:

        data = response.text
        lines = data.split('\n')

        satellite_name = lines[0].strip()
        tle_line1 = lines[1].strip()
        tle_line2 = lines[2].strip()

        return norad_id, satellite_name, tle_line1, tle_line2
    
    else:
        print(response.status_code)


