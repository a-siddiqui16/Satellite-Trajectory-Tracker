
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import ode #takes a differential equation
from matplotlib import image
plt.style.use('dark_background')


#Constants
earth_radius = 6378.0 #km
earth_mu = 398600.0 #earths graviational parameter #km^3 / s^2


def plot(r):

    #3D plot screen to be represented to the user
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(111,projection='3d')
    
    #plot trajectory and starting point
    ax.plot(r[:,0], r[:,1], r[:,2], 'k-')
    ax.plot([r[0,0]], [r[0,1]], [r[0,2]],'ko')

    #plot earth
    r_plot = earth_radius

    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x = earth_radius * np.outer(np.cos(u), np.sin(v))
    y = earth_radius * np.outer(np.sin(u), np.sin(v))
    z = earth_radius * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_wireframe(x, y, z, color = "k", linewidth = 0.25)


    #check for custom axes limits
    max_val = np.max(np.abs(r))

    #set labels
    max_val = np.max(np.abs(r))
    ax.set_xlim([-max_val, max_val])
    ax.set_ylim([-max_val, max_val])
    ax.set_zlim([-max_val, max_val])

    #sets titles
    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')
    ax.set_zlabel('Z (km)')

    ax.set_aspect('equal')
    ax.set_title('Trajectory . Starting Position')
    plt.legend(['Trajectory','Starting Position'])
    plt.show()


# def plot_earth(ax, radius=6371):
#     # Load Earth texture
#     img = image.imread('earth_textures.jpg') 
    
#     #generate sphere coordinates
#     u = np.linspace(0, 2 * np.pi, img.shape[1])
#     v = np.linspace(-np.pi/2, np.pi/2, img.shape[0])

#     u, v = np.meshgrid(u, v)

#     x = radius * np.cos(v) * np.cos(u)
#     y = radius * np.cos(v) * np.sin(u)
#     z = radius * np.sin(v)

#     # map texture
#     ax.plot_surface(
#         x, y, z,
#         rstride=1,
#         cstride=1,
#         facecolors=img/255,
#         linewidth=0,
#         antialiased=False
#     )




def diffy_q(t, y, mu):
    #unpack the state
    #t -> time
    #y -> state
    #mu -> additional parameter

    rx, ry, rz, vx, vy, vz = y
    r = np.array([rx, ry, rz]) #Changes the format to a vector

    #norm of radius vector
    norm_r = np.linalg.norm(r)

    #two body acceleration
    ax = -mu * rx / norm_r**3
    ay = -mu * ry / norm_r**3
    az = -mu * rz / norm_r**3

    return [vx, vy, vz, ax, ay, az] #derivative of precision is your velocrit

    #r is pointing from the centre of the earth to your
    # satellite and the acceleration due to gravity is going in the opposite direction so r is negative


if __name__ == '__main__':
    #initial conditions to be met

    r_mag = earth_radius + 500.0
    v_mag = np.sqrt(earth_mu / r_mag)

    #initial position and velocity vectors
    r0 = np.array([r_mag, 0, 0])
    v0 = np.array([0, v_mag, 0])

    #timespan
    tspan = 100 * 60.0

    #timestamp
    dt = 10.0

    #total number of steps
    n_steps = int(np.ceil(tspan / dt))

    #initialise variables   
    ys = np.zeros((n_steps, 6)) #6 states, 60 rows wide by 6 columns
    ts = np.zeros((n_steps, 1))

    #intial conditions
    y0 = np.concatenate((r0, v0))
    ys[0] = np.array(y0)
    step = 1

    #solver
    solver = ode(diffy_q)
    solver.set_integrator('lsoda') #fastest ODE according to the tutorial
    solver.set_initial_value(y0, 0)
    solver.set_f_params(earth_mu)

    #propagate orbit

    while solver.successful() and step < n_steps:
        solver.integrate(solver.t + dt)
        ts[step] = solver.t #step will be initially set to one, so use a variable to not override the conditons
        ys[step] = solver.y
        step += 1

    rs = ys[:, :3] #all the rows in column 1 and 2

    plot(rs)
