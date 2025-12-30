import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import ode
from propagator.orbit_propagator import OrbitPropagator as OP
from propagator import planetary_data
plt.style.use('dark_background')

cb = planetary_data.earth

if __name__ == "__main__":
    r_mag = cb["radius"] + 500.0
    v_mag = np.sqrt(cb["mu"] / r_mag)

    #initial position and velocity vectors
    r0 = np.array([r_mag, 0, 0])
    v0 = np.array([0, v_mag, 0])

    #timespan
    tspan = 100 * 60.0

    #timestamp
    dt = 10.0

    op = OP(r0, v0, tspan, dt)
    op.propagate_orbit()
    op.plot_3d(show_plot=True)


