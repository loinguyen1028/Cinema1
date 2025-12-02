# main.py
import tkinter as tk
from login_window import LoginWindow
from main_menu import MainMenu

def start_login():
    root = tk.Tk()

    def on_login_success(user_id, full_name, role_name):
        root.destroy()
        start_main_menu(user_id, full_name, role_name)

    LoginWindow(root, on_login_success)
    root.mainloop()

def start_main_menu(user_id, full_name, role_name):
    root = tk.Tk()

    def on_logout():
        root.destroy()
        start_login()

    MainMenu(root, user_id, full_name, role_name, on_logout)
    root.mainloop()

if __name__ == "__main__":
    start_login()
