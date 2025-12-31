import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import ode
from propagator import planetary_data
from propagator import n_orbits
import math

pi = math.pi
cb = planetary_data.earth

class OrbitPropagator:

    def __init__(self, state0, tspan, dt, coes=False, cb=planetary_data.earth):

        if coes:
            self.r0, self.v0 =n_orbits.coes2rv(state0, deg=True, mu=cb['mu'])
        else:
            self.r0 = state0[:3]
            self.v0 = state0[3:]

        self.tspan = tspan
        self.dt = dt 
        self.cb = cb

        self.n_steps = int(np.ceil(self.tspan / self.dt))

        #initialise variables   
        self.ys = np.zeros((self.n_steps, 6)) #6 states, 60 rows wide by 6 columns
        self.ts = np.zeros((self.n_steps, 1))

        #intial conditions
        self.y0 = np.concatenate((self.r0, self.v0))
        self.ys[0] = np.array(self.y0)
        self.step = 1

        #solver
        self.solver = ode(self.diffy_q)
        self.solver.set_integrator('lsoda') #fastest ODE according to the tutorial
        self.solver.set_initial_value(self.y0, 0)


    def propagate_orbit(self):

        #propagate orbit

        while self.solver.successful() and self.step < self.n_steps:
            self.solver.integrate(self.solver.t + self.dt)
            self.ts[self.step] = self.solver.t #step will be initially set to one, so use a variable to not override the conditons
            self.ys[self.step] = self.solver.y
            self.step += 1

        self.rs = self.ys[:, :3] #all the rows in column 1 and 2
        self.vs = self.ys[:,3:]


    def diffy_q(self, t, y):

        #unpack the state
        #t -> time
        #y -> state
        #mu -> additional parameter

        rx, ry, rz, vx, vy, vz = y
        self.r = np.array([rx, ry, rz]) #Changes the format to a vector

        #norm of radius vector
        norm_r = np.linalg.norm(self.r)

        #two body acceleration
        ax = -self.cb['mu'] * rx / norm_r**3
        ay = -self.cb['mu'] * ry / norm_r**3
        az = -self.cb['mu'] * rz / norm_r**3

        return [vx, vy, vz, ax, ay, az] #derivative of precision is your velocrit

        #r is pointing from the centre of the earth to your
        # satellite and the acceleration due to gravity is going in the opposite direction so r is negative


    def plot_3d(self, show_plot=False, save_plot=False, title="Test"):

        #3D plot screen to be represented to the user
        fig = plt.figure(figsize=(10,10))
        ax = fig.add_subplot(111,projection='3d')
        
        #plot trajectory and starting point
        ax.plot(self.rs[:,0], self.rs[:,1], self.rs[:,2], 'k-')
        ax.plot([self.rs[0,0]], [self.rs[0,1]], [self.rs[0,2]],'ko')

        #plot earth
        r_plot = self.cb["radius"]

        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi, 50)
        x = self.cb["radius"] * np.outer(np.cos(u), np.sin(v))
        y = self.cb["radius"] * np.outer(np.sin(u), np.sin(v))
        z = self.cb["radius"] * np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_wireframe(x, y, z, color = "k", linewidth = 0.25)


        #check for custom axes limits
        max_val = np.max(np.abs(self.r))

        #set labels
        max_val = np.max(np.abs(self.r))
        ax.set_xlim([-max_val, max_val])
        ax.set_ylim([-max_val, max_val])
        ax.set_zlim([-max_val, max_val])

        #sets titles
        ax.set_xlabel('X (km)')
        ax.set_ylabel('Y (km)')
        ax.set_zlabel('Z (km)')

        #ax.set_aspect('equal')

        ax.set_title(title)
        plt.legend()
        plt.show()

        if show_plot:
            plt.show()
        if save_plot:
            plt.savefig(title+'.png', dpi=300)


