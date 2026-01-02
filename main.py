from auth.login_gui import LoginWindow
from gui.main_system import MainSystemGUI

if __name__ == "__main__":
    #Show login window first
    login_window = LoginWindow()
    login_successful, username = login_window.run()

    #If login successful, show main system
    if login_successful:
        main_system = MainSystemGUI(username)
        main_system.run()