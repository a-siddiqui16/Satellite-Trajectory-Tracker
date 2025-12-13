import sys
import os
import subprocess

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Change to project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Starting Satellite Tracker System...")
print("Loading login screen...\n")

# Run the login GUI directly as a subprocess
try:
    subprocess.run([sys.executable, 'auth/login_gui.py'])
except Exception as e:
    print(f"Error: {e}")