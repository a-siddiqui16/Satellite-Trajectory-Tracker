# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.integrate import ode
# from math import sqrt
# from propagator.orbit_propagator import OrbitPropagator as OP
# from propagator import planetary_data
# from propagator import n_orbits
# # from auth import login_gui, password_hash

# plt.style.use('dark_background')

# cb = planetary_data.earth

# #timespan
# tspan = 100 * 60.0

# #timestamp
# dt = 10.0 #I have found that a larger number is less accurate

# if __name__ == "__main__":
#     # r_mag = cb["radius"] + 500.0
#     # v_mag = sqrt(cb["mu"] / r_mag)
 

#     # #initial position and velocity vectors
#     # r0 = np.array([r_mag, 0, 0])
#     # v0 = np.array([0, v_mag, 0])

#     # r_mag = cb["radius"] + 1000.0
#     # v_mag = sqrt(cb["mu"] / r_mag) * 1.1
#     # r00 = np.array([r_mag, 0, 0])
#     # v00 = np.array([0, v_mag, 5]) #Experimenting with inclination and eccentricity

#     # #Plotting second orbit
#     # op = OP(r0, v0, tspan, dt)
#     # op0 = OP(r00, v00, tspan, dt)

#     # op.propagate_orbit()
#     # op0.propagate_orbit()

#     # n_orbits.plot_n_orbits([op.rs, op0.rs], labels=['0', '1'], show_plot=True)


#     #Testing example TLE Data for ISS
#     #Line 1: 1 25544U 98067A   22001.74462497  .00001435  00000-0  34779-4 0  9992
#     #Line 2: 2 25544  51.6464  24.2704 0004064  69.5467 290.6355 15.48835264296862

#     #a, e, i, ta, aop, raan = coes
#     c0 = [cb["radius"]+414.0, 0.0004064, 51.6464, 0.0, 69.5467, 24.2704]

#     #GEO
#     c1 = [cb["radius"]+35800, 0.0, 0.0, 0.0, 0.0, 0.0]

#     op0 = OP(c0, tspan, dt, coes=True)
#     op1 = OP(c1, tspan, dt, coes=True)

#     op0.propagate_orbit()
#     op1.propagate_orbit()

#     n_orbits.plot_n_orbits([op0.rs, op1.rs], labels=['ISS', 'GEO'], show_plot=True)
    

import sys
import os

# Add current directory and subdirectories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'auth'))
sys.path.insert(0, os.path.join(current_dir, 'gui'))

from auth.login_gui import LoginWindow
from gui.main_system import MainSystemGUI

if __name__ == "__main__":
    # Show login window first
    login_window = LoginWindow()
    login_successful, username = login_window.run()

    # If login successful, show main system
    if login_successful:
        main_system = MainSystemGUI(username)
        main_system.run()