import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from skyfield.api import EarthSatellite, load
import sys
import os

#Add directories to path (Used AI to fix import issues)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
skyfield_dir = os.path.join(parent_dir, 'skyfield')
tle_fetcher_dir = os.path.join(parent_dir, 'tle_fetcher')
sys.path.insert(0, parent_dir)
sys.path.insert(0, skyfield_dir)
sys.path.insert(0, tle_fetcher_dir)


import skyfield
import tle_fetcher
import orbital_calculations
from propagator.orbit_propagator import OrbitPropagator
from propagator import planetary_data
plt.style.use('dark_background')

class MainSystemGUI:

    def __init__(self, username):
        self.username = username
        self.window = tk.Tk()
        self.window.title("Satellite Trajectory Tracker")
        self.window.geometry('1920x1080')
        self.window.configure(bg='#333333')
        self.ts = load.timescale()

        #Header
        header_frame = tk.Frame(self.window, bg='#1373CC', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame, text="Satellite Trajectory Tracker", bg='#1373CC', fg="#FFFFFF", font=("Arial", 24, "bold")
            )


        title_label.pack(pady=20)

        #Welcome message
        welcome_frame = tk.Frame(self.window, bg='#333333')
        welcome_frame.pack(pady=20)

        welcome_label = tk.Label(
            welcome_frame,text=f"Welcome, {username}!",bg='#333333',fg="#FFFFFF",font=("Arial", 16)
            )
        welcome_label.pack()

        #Input box
        input_frame = tk.Frame(self.window, bg='#333333')
        input_frame.pack(pady=30)

        norad_label = tk.Label(
            input_frame,text="Enter NORAD ID:",bg='#333333',fg="#FFFFFF",font=("Arial", 14)
            )
        norad_label.grid(row=0, column=0, padx=10, pady=10)

        self.norad_entry = tk.Entry(
            input_frame, font=("Arial", 14), width=20
            )
        

        self.norad_entry.grid(row=0, column=1, padx=10, pady=10)

        track_button = tk.Button(
            input_frame,text="Track Satellite",command=self.track_satellite,bg="#1373CC",fg="#FFFFFF",font=("Arial", 14),width=15,height=5
            )
        
        track_button.grid(row=0, column=2, padx=10, pady=10)

        #Added example NORAD ID's for user to experiment with
        info_frame = tk.Frame(self.window, bg='#333333')
        info_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        info_label = tk.Label(
            info_frame,text="Common NORAD IDs:\n\nISS: 25544\nHubble: 20580\nGPS BIIA-10: 22877",bg='#333333',fg="#AAAAAA",font=("Arial", 12),justify=tk.LEFT
            )
        info_label.pack(pady=20)

    def track_satellite(self):

        norad_id_str = self.norad_entry.get().strip()

        if not norad_id_str:
            messagebox.showerror("Error", "Invalid NORAD ID")
            return

        try:
            norad_id = int(norad_id_str)

        except ValueError:
            messagebox.showerror("Error", "Invalid NORAD ID")
            return

        #Fetch TLE data
        satellite_data = tle_fetcher.fetch_satellite_tle(norad_id)

        if not satellite_data:
            messagebox.showerror("Error", f"Could not fetch data for NORAD ID: {norad_id}")
            return

        norad_id, satellite_name, tle_line1, tle_line2 = satellite_data

        #Create satellite object
        satellite = EarthSatellite(tle_line1, tle_line2, satellite_name, self.ts)
        orbit_type, altitude, inclination = orbital_calculations.classify_orbit(satellite)

        #Orbit parameters for satellite
        info_message = f"Satellite: {satellite_name}\n"
        info_message += f"NORAD ID: {norad_id}\n"
        info_message += f"Orbit Type: {orbit_type}\n"
        info_message += f"Altitude: {altitude:.2f} km\n"
        info_message += f"Inclination: {inclination:.2f}°\n\n"

        messagebox.showinfo("Satellite Info", info_message)

        #Visualize orbit
        self.visualize_orbit(satellite_name, altitude, inclination)

    def visualize_orbit(self, satellite_name, altitude, inclination):
        cb = planetary_data.earth

        #Classical orbital elements (COES): [a, e, i, ta, aop, raan]
        coes = [cb["radius"] + altitude, 0.0001, inclination, 0.0, 0.0, 0.0]

        tspan = 100 * 60.0  #100 minutes
        dt = 10.0 #Found that a smaller timespan = higher accuracy

        op = OrbitPropagator(coes, tspan, dt, coes=True)
        op.propagate_orbit()

        #Visualization window
        visualisaton_window = tk.Toplevel(self.window)
        visualisaton_window.title(f"Orbit Visualization - {satellite_name}")
        visualisaton_window.geometry('1280x720')
        visualisaton_window.configure(bg='#333333')

        #Create matplotlib plot
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        #Plot trajectory
        ax.plot(op.rs[:, 0], op.rs[:, 1], op.rs[:, 2], 'c-', linewidth=1.5, label=satellite_name)
        ax.plot([op.rs[0, 0]], [op.rs[0, 1]], [op.rs[0, 2]], 'go', markersize=8, label='Inital Satellite Position')

        #Plot Earth
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi, 50)
        x = cb["radius"] * np.outer(np.cos(u), np.sin(v))
        y = cb["radius"] * np.outer(np.sin(u), np.sin(v))
        z = cb["radius"] * np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_wireframe(x, y, z, color="k", linewidth=0.3, alpha=0.3)

        #Set labels and limits
        max_val = np.max(np.abs(op.rs))
        ax.set_xlim([-max_val, max_val])
        ax.set_ylim([-max_val, max_val])
        ax.set_zlim([-max_val, max_val])

        ax.set_xlabel('X (km)', fontsize=10)
        ax.set_ylabel('Y (km)', fontsize=10)
        ax.set_zlabel('Z (km)', fontsize=10)

        ax.set_title(f'{satellite_name} Orbital Trajectory', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')

        #Embed matplotlib in tkinter
        canvas = FigureCanvasTkAgg(fig, master=visualisaton_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run(self):
        self.window.mainloop()