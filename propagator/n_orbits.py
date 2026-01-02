import numpy as np
import matplotlib.pyplot as plt
from propagator import planetary_data
import math as m

d2r = np.pi/100.0


def plot_n_orbits(rs, labels, cb=planetary_data.earth, show_plot=False, save_plot=False, title="Many Orbits"):

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


#Algorithm to take classical orbital elements

def coes2rv(coes, deg=False, mu=planetary_data.earth['mu']):
     
    if deg:
        a, e, i, ta, aop, raan = coes
        i*= d2r
        ta*= d2r
        aop*= d2r
        raan*= d2r
    else:
         a, e, i, ta, aop, raan = coes

    E = ecc_anomaly([ta, e], 'tae')

    r_norm = a * (1-e**2)/(1+e * np.cos(ta))

    #calculating r and v vectors in perifocal frame
    r_perif = r_norm * np.array([m.cos(ta), m.sin(ta), 0])
    v_perif = m.sqrt(mu * a)/r_norm * np.array([-m.sin(E), m.cos(E) * m.sqrt(1-e**2), 0])
    
    #rotation matrix
    perif2eci = np.transpose(eci2perif(raan, aop, i))

    #calculate r and v vectors in inetertal frame
    r = np.dot(perif2eci, r_perif)
    v = np.dot(perif2eci, v_perif)

    return r, v


#ECI to perifocal rotation matrix
def eci2perif(raan, aop, i):
    row0 = [-m.sin(raan)*m.cos(i)*m.sin(aop) + m.cos(raan)*m.cos(aop), m.cos(raan)*m.cos(i)*m.sin(aop) + m.sin(raan)*m.cos(aop), m.sin(i)*m.sin(aop)]
    row1 = [-m.sin(raan)*m.cos(i)*m.cos(aop) - m.cos(raan)*m.sin(aop),m.cos(raan)*m.cos(i)*m.cos(aop) - m.sin(raan)*m.sin(aop), m.sin(i)*m.cos(aop)]
    row2 = [m.sin(raan)*m.sin(i), -m.cos(raan)*m.sin(i), m.cos(i)]

    return np.array([row0, row1, row2])


def ecc_anomaly(arr, method, tol=1e-8):
    if method == "newton":

        #Iteratively Finding E via Newton's Method
        Me, e = arr
        if Me < np.pi / 2.0: 
            E0 = Me+e/2.0
        else:
            E0 = Me-e

        for n in range(200): #Number of steps
            ratio = (E0-e * np.sin(E0)-Me) / (1-e*np.cos(E0))
            if abs(ratio) < tol:
                if n == 0:
                    return E0
                else:
                    return E1
            else:
                E1 = E0-ratio
                E0 = E1

        return False

    elif method == "tae":
        ta, e = arr
        return 2 * m.atan(m.sqrt(1-e) / (1+e)) * m.tan(ta/2.0)
    
    else:
        print("Invalid method")
