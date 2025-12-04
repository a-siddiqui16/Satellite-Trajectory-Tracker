# keplerian_propagator.py
# Full, self-contained Keplerian propagator with TLE fetch, parsing, propagation, and VPython visualization.

import math
import requests
from datetime import datetime, timedelta, timezone
from vpython import canvas, sphere, vector, rate, label, color, textures, distant_light, wtext

# -----------------------------------
# Constants
# -----------------------------------
MU_EARTH = 398600.4418  # km^3/s^2
TWOPI = 2.0 * math.pi
WGS84_A = 6378.137      # km
WGS84_F = 1 / 298.257223563
WGS84_E2 = WGS84_F * (2 - WGS84_F)

# -----------------------------------
# Utility helpers
# -----------------------------------
def deg2rad(d): return d * math.pi / 180.0
def rad2deg(r): return r * 180.0 / math.pi

def wrap_to_2pi(x):
    x = math.fmod(x, TWOPI)
    return x if x >= 0 else x + TWOPI

# -----------------------------------
# TLE fetch and parse
# -----------------------------------
def fetch_satellite_tle(norad_id):
    url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=tle"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    lines = [l for l in resp.text.splitlines() if l.strip()]
    if len(lines) < 3:
        raise ValueError("TLE fetch returned incomplete data")
    return norad_id, lines[0].strip(), lines[1].strip(), lines[2].strip()

def parse_tle_lines(line1, line2):
    # Epoch YYDDD.ddd
    epoch_year = int(line1[18:20])
    epoch_year += 2000 if epoch_year < 57 else 1900
    epoch_day = float(line1[20:32])
    epoch = datetime(epoch_year, 1, 1, tzinfo=timezone.utc) + timedelta(days=epoch_day - 1)

    inc_deg = float(line2[8:16])
    raan_deg = float(line2[17:25])
    ecc_str = line2[26:33].strip()
    e = float(f"0.{ecc_str}")
    argp_deg = float(line2[34:42])
    M_deg = float(line2[43:51])
    n_rev_per_day = float(line2[52:63])

    n_rad_s = n_rev_per_day * TWOPI / 86400.0
    a_km = (MU_EARTH / (n_rad_s**2)) ** (1.0 / 3.0)

    return {
        "epoch": epoch,
        "a_km": a_km,
        "e": e,
        "inc_rad": deg2rad(inc_deg),
        "raan_rad": deg2rad(raan_deg),
        "argp_rad": deg2rad(argp_deg),
        "M0_rad": deg2rad(M_deg),
    }

# -----------------------------------
# Kepler solver and anomalies
# -----------------------------------
def kepler_E_from_M(M, e, tol=1e-10, max_iter=50):
    M = wrap_to_2pi(M)
    E = M if e < 0.8 else math.pi
    for _ in range(max_iter):
        f = E - e * math.sin(E) - M
        fp = 1 - e * math.cos(E)
        dE = -f / fp
        E += dE
        if abs(dE) < tol:
            break
    return E

def true_anomaly_from_E(E, e):
    beta = math.sqrt((1 + e) / (1 - e))
    v = 2.0 * math.atan2(beta * math.tan(E / 2.0), 1.0)
    return wrap_to_2pi(v)

# -----------------------------------
# Frame transforms and Earth rotation
# -----------------------------------
def perifocal_to_eci(r_pf, v_pf, inc, raan, argp):
    cO, sO = math.cos(raan), math.sin(raan)
    ci, si = math.cos(inc), math.sin(inc)
    cw, sw = math.cos(argp), math.sin(argp)
    R = [
        [cO*cw - sO*sw*ci, -cO*sw - sO*cw*ci, sO*si],
        [sO*cw + cO*sw*ci, -sO*sw + cO*cw*ci, -cO*si],
        [sw*si,             cw*si,              ci    ]
    ]
    def matmul(Rm, v):
        return [
            Rm[0][0]*v[0] + Rm[0][1]*v[1] + Rm[0][2]*v[2],
            Rm[1][0]*v[0] + Rm[1][1]*v[1] + Rm[1][2]*v[2],
            Rm[2][0]*v[0] + Rm[2][1]*v[1] + Rm[2][2]*v[2],
        ]
    return matmul(R, r_pf), matmul(R, v_pf)

def gmst_from_datetime(dt):
    Y, M, D = dt.year, dt.month, dt.day
    h, m, s = dt.hour, dt.minute, dt.second + dt.microsecond/1e6
    if M <= 2:
        Y -= 1
        M += 12
    A = math.floor(Y / 100)
    B = 2 - A + math.floor(A / 4)
    JD = math.floor(365.25 * (Y + 4716)) + math.floor(30.6001 * (M + 1)) + D + B - 1524.5
    JD += (h + m/60 + s/3600) / 24.0
    T = (JD - 2451545.0) / 36525.0
    gmst_deg = 280.46061837 + 360.98564736629 * (JD - 2451545.0) + 0.000387933*T*T - T*T*T/38710000.0
    return deg2rad(gmst_deg % 360.0)

def eci_to_ecef(r_eci, gmst):
    cg, sg = math.cos(gmst), math.sin(gmst)
    x = cg * r_eci[0] + sg * r_eci[1]
    y = -sg * r_eci[0] + cg * r_eci[1]
    z = r_eci[2]
    return [x, y, z]

def ecef_to_geodetic(r_ecef):
    x, y, z = r_ecef
    lon = math.atan2(y, x)
    r = math.hypot(x, y)
    lat = math.atan2(z, r * (1 - WGS84_E2))
    for _ in range(6):
        sin_lat = math.sin(lat)
        N = WGS84_A / math.sqrt(1 - WGS84_E2 * sin_lat * sin_lat)
        alt = r / math.cos(lat) - N
        lat = math.atan2(z, r * (1 - WGS84_E2 * N / (N + alt)))
    sin_lat = math.sin(lat)
    N = WGS84_A / math.sqrt(1 - WGS84_E2 * sin_lat * sin_lat)
    alt = r / math.cos(lat) - N
    return rad2deg(lat), rad2deg(lon), alt

# -----------------------------------
# Core Keplerian propagator
# -----------------------------------
def propagate_kepler_from_elements(a_km, e, inc_rad, raan_rad, argp_rad, M0_rad, epoch_dt, when_dt):
    n = math.sqrt(MU_EARTH / (a_km**3))  # rad/s
    dt_sec = (when_dt - epoch_dt).total_seconds()
    M = wrap_to_2pi(M0_rad + n * dt_sec)

    E = kepler_E_from_M(M, e)
    v = true_anomaly_from_E(E, e)

    r_mag = a_km * (1 - e * math.cos(E))
    r_pf = [r_mag * math.cos(v), r_mag * math.sin(v), 0.0]

    sqrt_mu_a = math.sqrt(MU_EARTH / a_km)
    rdot = sqrt_mu_a * e * math.sin(E) / (1 - e * math.cos(E))
    thetadot = sqrt_mu_a * math.sqrt(1 - e*e) / r_mag
    v_pf = [
        rdot * math.cos(v) - r_mag * thetadot * math.sin(v),
        rdot * math.sin(v) + r_mag * thetadot * math.cos(v),
        0.0
    ]

    r_eci, v_eci = perifocal_to_eci(r_pf, v_pf, inc_rad, raan_rad, argp_rad)

    gmst = gmst_from_datetime(when_dt)
    r_ecef = eci_to_ecef(r_eci, gmst)
    lat_deg, lon_deg, alt_km = ecef_to_geodetic(r_ecef)

    return {
        "time": when_dt,
        "r_eci_km": r_eci,
        "v_eci_km_s": v_eci,
        "r_ecef_km": r_ecef,
        "lat_deg": lat_deg,
        "lon_deg": lon_deg,
        "alt_km": alt_km,
    }

# -----------------------------------
# Main: fetch TLE, propagate, visualize
# -----------------------------------
def main(norad_id=25544):
    norad_id, satellite_name, tle_line1, tle_line2 = fetch_satellite_tle(norad_id)
    els = parse_tle_lines(tle_line1, tle_line2)

    scene = canvas(width=900, height=700, background=color.black)
    scene.title = f"Satellite Trajectory Tracker (Keplerian) — {satellite_name}"
    scene.append_to_caption("Satellite Info\n")
    info_box = wtext(text="Current satellite data\n")
    distant_light(direction=vector(1,1,0), color=color.yellow)

    earth = sphere(pos=vector(0,0,0), radius=6378, texture=textures.earth)
    sat = sphere(radius=13, color=color.green, make_trail=True, trail_radius=5, trail_color=color.red)
    label_box = label(pos=sat.pos, text=satellite_name, height=16, border=3, font='sans')

    while True:
        rate(60)
        now = datetime.now(timezone.utc)

        res = propagate_kepler_from_elements(
            els["a_km"], els["e"], els["inc_rad"], els["raan_rad"], els["argp_rad"], els["M0_rad"],
            els["epoch"], now
        )

        x, y, z = res["r_eci_km"]
        sat.pos = vector(x, y, z)
        label_box.pos = sat.pos + vector(0, 50, 0)

        vx, vy, vz = res["v_eci_km_s"]
        speed = math.sqrt(vx*vx + vy*vy + vz*vz)

        info_text = (
            f"{satellite_name}\n"
            f"Latitude: {res['lat_deg']:.2f}°\n"
            f"Longitude: {res['lon_deg']:.2f}°\n"
            f"Altitude: {res['alt_km']:.2f} km\n"
            f"Velocity: {speed:.2f} km/s\n"
        )
        info_box.text = info_text

if __name__ == "__main__":
    main(25544)  # ISS by default; change NORAD ID as needed


