import re
import sqlite3
import tkinter as tk
from tkinter import messagebox
from string import punctuation
from auth.password_hash import sha256, verify_password


db_path = "satellite_database.db"

#Function for password validation based on my SMART objectives
def check_password(password):

    errors = []

    #Length requirement (at least 8 characters)
    if len(password) < 8:
        errors.append("at least 8 characters long")

    #Password enforces that there must be an uppercase letter
    if not re.search(r'[A-Z]', password):
        errors.append("at least one uppercase letter")

    #Password enforces that there must be a lowercase letter
    if not re.search(r'[a-z]', password):
        errors.append("at least one lowercase letter")

    #Password enforces that there must be a number
    if not re.search(r'[0-9]', password):
        errors.append("at least one number")

    #Using a for loop to check for a special character
    has_special = False
    for char in password:
        if char in punctuation:
            has_special = True
            break

    if not has_special:
        errors.append("at least one special character")

    #If not all passsword rules have been fufilled, return a list of all the errors
    if errors:
        error_message = errors
        return False, error_message
    
    return True, "Password is valid"


class LoginWindow:

    def __init__(self):

        #Main login window
        self.window = tk.Tk()
        self.window.title("Login form")
        self.window.geometry('1920x1080')
        self.window.configure(bg='#333333')

        #Login status
        self.login_successful = False
        self.username = None

        frame = tk.Frame(bg='#333333')


        #Title label (Login)
        title_label = tk.Label(
            frame, text="Login", bg='#333333', fg="#1373CC", font=("Arial", 30)
        )

        #Username label and an entry box
        username_label = tk.Label(
            frame, text="Username", bg='#333333', fg="#FFFFFF", font=("Arial", 16)
        )

        self.username_entry = tk.Entry(frame, font=("Arial", 16))

        #Password label and entry box (hides characters using an asterisk "*")
        password_label = tk.Label(
            frame, text="Password", bg='#333333', fg="#FFFFFF", font=("Arial", 16)
        )

        self.password_entry = tk.Entry(frame, show="*", font=("Arial", 16))


        #Login button that activates the validate_login function
        login_button = tk.Button(
            frame, text="Login", command=self.validate_login, bg="#1373CC", fg="#FFFFFF", font=("Arial", 16), width=15
        )

        #A register button that allows an account to be created
        register_button = tk.Button(
            frame, text="Register", command=self.register_user, bg="#1373CC", fg="#FFFFFF", font=("Arial", 16), width=15
        )


        #Layout of the login page
        title_label.grid(row=0, column=0, columnspan=2, sticky="news", pady=40)

        username_label.grid(row=1, column=0, padx=20, pady=20)
        self.username_entry.grid(row=1, column=1, padx=20, pady=20)

        password_label.grid(row=2, column=0, padx=20, pady=20)
        self.password_entry.grid(row=2, column=1, padx=20, pady=20)

        login_button.grid(row=3, column=0, padx=10, pady=30, sticky="ew")
        register_button.grid(row=3, column=1, padx=10, pady=30)

        frame.pack(padx=30, pady=30)

    def validate_login(self):

        #Gets a user input
        username = self.username_entry.get()
        password = self.password_entry.get()

        #Checks whether both fields are filled
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        try:

            #Connects to database and checks user credentials
            with sqlite3.connect(db_path) as conn:
                c = conn.cursor()

                #Retrieve stored password hash for the username
                c.execute("SELECT password_hash FROM Users WHERE username = ?", 
                          (username,))
                result = c.fetchone()

                if result:
                    stored_hash = result[0]

                    #Checks that the entered password matches the stored hash
                    if verify_password(password, stored_hash):
                        messagebox.showinfo("Login Successful", f"Welcome {username}!")
                        self.login_successful = True
                        self.username = username
                        self.window.destroy()

                    else:
                        messagebox.showerror("Error", "Invalid Password")

                else:
                    messagebox.showerror("Error", "User not found")

        #Catches database errors
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def register_user(self):

        #Stores user inputs
        username = self.username_entry.get()
        password = self.password_entry.get()

        #Checks whether both fields are filled
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        #Checks whether passwors strength is valid
        is_valid, error_msg = check_password(password)

        if not is_valid:
            #Display all password errors
            error_text = "Password must have:\n" + "\n".join(f"• {error}" for error in error_msg)
            messagebox.showerror("Invalid password", error_text)
            return

        #Hash password before storing
        hashed_password = sha256(password).hex()

        try:
            
            #Insets new user into the databse with their credentials
            with sqlite3.connect(db_path) as conn:

                c = conn.cursor()
                c.execute("INSERT INTO Users (username, password_hash) VALUES (?, ?)", 
                        (username, hashed_password))
                
                conn.commit()
                messagebox.showinfo("Success", "User registered successfully!")

        #Returns an error if the username already exists
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")

        #Catches any other database error
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    #Run the login window in Tkinter
    def run(self):
        self.window.mainloop()
        return self.login_successful, self.username