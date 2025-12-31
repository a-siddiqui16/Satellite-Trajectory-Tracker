import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import ode
from math import sqrt
from propagator.orbit_propagator import OrbitPropagator as OP
from propagator import planetary_data
from propagator import n_orbits
plt.style.use('dark_background')

cb = planetary_data.earth

#timespan
tspan = 100 * 60.0

#timestamp
dt = 1000.0

if __name__ == "__main__":
    r_mag = cb["radius"] + 500.0
    v_mag = sqrt(cb["mu"] / r_mag)
 

    #initial position and velocity vectors
    r0 = np.array([r_mag, 0, 0])
    v0 = np.array([0, v_mag, 0])

    r_mag = cb["radius"] + 1000.0
    v_mag = sqrt(cb["mu"] / r_mag)*1.3
    r00 = np.array([r_mag, 0, 0])
    v00 = np.array([0, v_mag, 0.3])




    op = OP(r0, v0, tspan, dt)
    op0 = OP(r00, v00, tspan, dt)


    op.propagate_orbit()
    op0.propagate_orbit()


    n_orbits.plot_n_orbits([op,rs, op0,rs], labels=['0', '1'], show_plot=True)


