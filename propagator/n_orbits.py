import numpy as np
import matplotlib as plt
from propagator import planetary_data

d2r = np.pi/100.0
cb = planetary_data.earth

def plot_n_orbits(rs, labels, show_plot=False, save_plot=False, title="Many Orbits"):

        #3D plot screen to be represented to the user
        fig = plt.figure(figsize=(10,10))
        ax = fig.add_subplot(111,projection='3d')
        
        n = 0
        #plot trajectory and starting point
        for r in rs:
            ax.plot(r[:,0], r[:,1], r[:,2], label=labels[n])
            ax.plot([r[0,0]], [r[0,1]], [r[0,2]],'ko')
            n += 1 #Determines which orbit is being displayed

        #plot earth
        r_plot = cb["radius"]

        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi, 50)
        x = cb["radius"] * np.outer(np.cos(u), np.sin(v))
        y = cb["radius"] * np.outer(np.sin(u), np.sin(v))
        z = cb["radius"] * np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_wireframe(x, y, z, color = "k", linewidth = 0.25)

        #set labels
        max_val = np.max(np.abs(r))
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