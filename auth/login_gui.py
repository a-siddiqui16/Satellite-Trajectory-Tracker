import re
import sqlite3
import tkinter as tk
from tkinter import messagebox
from string import punctuation
from password_hash import hash_password, verify_password
import sys
import os

# Handle imports whether running as script or module
try:
    from .password_hash import hash_password, verify_password
except ImportError:
    # If relative import fails, try absolute import
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from auth.password_hash import hash_password, verify_password


#Function for password validation based on my SMART objectives
def check_password(password):

    errors = []

    if len(password) < 8:
        errors.append("at least 8 characters long")

    if not re.search(r'[A-Z]', password):
        errors.append("at least one uppercase letter")

    if not re.search(r'[a-z]', password):
        errors.append("at least one lowercase letter")

    if not re.search(r'[0-9]', password):
        errors.append("at least one number")

    has_special = False
    for char in password:
        if char in punctuation:
            has_special = True
            break

    if not has_special:
        errors.append("at least one special character")

    if errors:
        error_message = errors
        return False, error_message
    
    return True, "Password is valid"

password = input()

print(check_password(password))

