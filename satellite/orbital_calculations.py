import math
from datetime import datetime, timedelta, timezone

MU_EARTH = 398600.4418
TWOPI = 2.0 * math.pi
WGS84_A = 6378.137
WGS84_F = 1 / 298.257223563
WGS84_E2 = WGS84_F * (2 - WGS84_F)

def wrap_to_2pi(x):
    x = math.fmod(x, TWOPI)
    return x if x >= 0 else x + TWOPI

def parse_tle_lines(line1, line2):
    epoch_year = int(line1[18:20])
    epoch_year += 2000 if epoch_year < 57 else 1900
    epoch_day = float(line1[20:32])
    epoch = datetime(epoch_year, 1, 1, tzinfo=timezone.utc) + timedelta(days=epoch_day - 1)

    inc_deg = float(line2[8:16]); raan_deg = float(line2[17:25])
    e = float(f"0.{line2[26:33].strip()}")
    argp_deg = float(line2[34:42]); M_deg = float(line2[43:51])
    n_rev_per_day = float(line2[52:63])
    n_rad_s = n_rev_per_day * TWOPI / 86400.0
    a_km = (MU_EARTH / (n_rad_s**2)) ** (1/3)

    return {
        "epoch": epoch, "a_km": a_km, "e": e,
        "inc_rad": math.radians(inc_deg),
        "raan_rad": math.radians(raan_deg),
        "argp_rad": math.radians(argp_deg),
        "M0_rad": math.radians(M_deg),
    }

def kepler_E_from_M(M, e, tol=1e-10, max_iter=50):
    M = wrap_to_2pi(M)
    E = M if e < 0.8 else math.pi
    for _ in range(max_iter):
        f = E - e*math.sin(E) - M
        fp = 1 - e*math.cos(E)
        dE = -f/fp
        E += dE
        if abs(dE) < tol: break
    return E

def true_anomaly_from_E(E, e):
    beta = math.sqrt((1+e)/(1-e))
    v = 2.0 * math.atan2(beta * math.tan(E/2.0), 1.0)
    return wrap_to_2pi(v)

def perifocal_to_eci(r_pf, v_pf, inc, raan, argp):
    cO, sO = math.cos(raan), math.sin(raan)
    ci, si = math.cos(inc), math.sin(inc)
    cw, sw = math.cos(argp), math.sin(argp)
    R = [
        [cO*cw - sO*sw*ci, -cO*sw - sO*cw*ci, sO*si],
        [sO*cw + cO*sw*ci, -sO*sw + cO*cw*ci, -cO*si],
        [sw*si,             cw*si,              ci    ]
    ]
    def mul(Rm, v):
        return [
            Rm[0][0]*v[0] + Rm[0][1]*v[1] + Rm[0][2]*v[2],
            Rm[1][0]*v[0] + Rm[1][1]*v[1] + Rm[1][2]*v[2],
            Rm[2][0]*v[0] + Rm[2][1]*v[1] + Rm[2][2]*v[2],
        ]
    return mul(R, r_pf), mul(R, v_pf)

def gmst_from_datetime(dt):
    Y, M, D = dt.year, dt.month, dt.day
    h, m, s = dt.hour, dt.minute, dt.second + dt.microsecond/1e6
    if M <= 2: Y -= 1; M += 12
    A = math.floor(Y / 100); B = 2 - A + math.floor(A / 4)
    JD = math.floor(365.25*(Y+4716)) + math.floor(30.6001*(M+1)) + D + B - 1524.5
    JD += (h + m/60 + s/3600) / 24.0
    T = (JD - 2451545.0) / 36525.0
    gmst_deg = 280.46061837 + 360.98564736629*(JD - 2451545.0) + 0.000387933*T*T - T*T*T/38710000.0
    return math.radians(gmst_deg % 360.0)

def eci_to_ecef(r_eci, gmst):
    cg, sg = math.cos(gmst), math.sin(gmst)
    return [cg*r_eci[0] + sg*r_eci[1], -sg*r_eci[0] + cg*r_eci[1], r_eci[2]]

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
    return math.degrees(lat), math.degrees(lon), alt

def propagate_kepler_from_elements(a_km, e, inc_rad, raan_rad, argp_rad, M0_rad, epoch_dt, when_dt):
    n = math.sqrt(MU_EARTH / (a_km**3))
    dt_sec = (when_dt - epoch_dt).total_seconds()
    M = wrap_to_2pi(M0_rad + n * dt_sec)

    E = kepler_E_from_M(M, e)
    v = true_anomaly_from_E(E, e)

    r_mag = a_km * (1 - e * math.cos(E))
    r_pf = [r_mag * math.cos(v), r_mag * math.sin(v), 0.0]

    sqrt_mu_a = math.sqrt(MU_EARTH / a_km)
    rdot = sqrt_mu_a * e * math.sin(E) / (1 - e * math.cos(E))
    thetadot = sqrt_mu_a * math.sqrt(1 - e*e) / r_mag
    v_pf = [rdot*math.cos(v) - r_mag*thetadot*math.sin(v),
            rdot*math.sin(v) + r_mag*thetadot*math.cos(v), 0.0]

    r_eci, v_eci = perifocal_to_eci(r_pf, v_pf, inc_rad, raan_rad, argp_rad)

    gmst = gmst_from_datetime(when_dt)
    r_ecef = eci_to_ecef(r_eci, gmst)
    lat_deg, lon_deg, alt_km = ecef_to_geodetic(r_ecef)

    return {"r_eci_km": r_eci, "v_eci_km_s": v_eci, "lat_deg": lat_deg, "lon_deg": lon_deg, "alt_km": alt_km}
