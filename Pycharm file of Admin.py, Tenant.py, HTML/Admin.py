import shutil
import uuid
from tkinter import *
import tkintermapview
from PIL import Image, ImageTk
import sqlite3
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from tkinter import messagebox
from tkinter import ttk
import json
import datetime
from tkcalendar import Calendar
from datetime import datetime, timedelta
from tkcalendar import DateEntry
from tkinter import font
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import customtkinter as ctk
import os
import time
import geopy.exc
import re
import tkinter as tk
from tqdm import tk
from deepface import DeepFace
import pickle

notification = None

# Set appearance mode and default color theme
ctk.set_appearance_mode("light")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
# fg='#fedebe' , bg='#fd5602'
# Initialize the main window using CTk instead of Tk
root = ctk.CTk()
root.title("Admin Dashboard")
root.geometry("1920x1080")
root.state("zoomed")
# Create and configure login/register frame with light background color
login_register_frame = ctk.CTkFrame(root)
login_register_frame.pack(fill=BOTH, expand=True)
# Update the background image section
# Load and set background image
bg_image = Image.open(r"C:/Kai Shuang/vennis.jpg")
bg_image = ctk.CTkImage(bg_image, size=bg_image.size)
bg_label = ctk.CTkLabel(login_register_frame, image=bg_image, text="")  # Empty text parameter required
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
# Connect to the SQLite database (create it if it doesn't exist)
conn = sqlite3.connect("govRental.db")
cursor = conn.cursor()


def admin_login_register():
    main_frame.pack_forget()
    head_frame.pack_forget()
    global login_frame, register_frame, admin_ic
    # Connect to the SQLite database
    def connect_db():
        conn = sqlite3.connect('govRental.db')
        return conn
    # Function to register admin
    def register_admin(existing=None):
        # Retrieve user inputs and strip whitespace
        try:
            admin_name = name_entry.get().strip()
            admin_ic = ic_entry.get().strip()
            admin_gender = gender_var.get().strip()
            admin_phone = phone_entry.get().strip()
            admin_passcode = passcode_entry.get().strip()
            admin_email = email_entry.get().strip()
        except NameError as e:
            messagebox.showerror("Error", f"An entry field is not defined: {e}")
            return
        # Validate all fields are filled
        if not all([admin_name, admin_ic, admin_gender, admin_phone, admin_passcode, admin_email]):
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        # Additional input validation
        try:
            # Validate IC Number
            if not (admin_ic.isdigit() and len(admin_ic) == 12):
                messagebox.showerror("Error", "IC Number must be exactly 12 digits.")
                return
            # Validate Phone Number
            if not (admin_phone.isdigit() and 10 <= len(admin_phone) <= 11):
                messagebox.showerror("Error", "Phone number must be 10-11 digits.")
                return
            # Validate Passcode
            if not (len(admin_passcode) == 6):
                messagebox.showerror("Error", "Passcode must be exactly 6 characters.")
                return
            # Validate Gender
            admin_gender = admin_gender.capitalize()
            if admin_gender not in ['Male', 'Female']:
                messagebox.showerror("Error", "Gender must be 'Male' or 'Female'.")
                return
            # Validate Email (basic check)
            if '@' not in admin_email or '.' not in admin_email:
                messagebox.showerror("Error", "Please enter a valid email address.")
                return
            # Database operations
            conn = connect_db()
            cursor = conn.cursor()
            # Check if IC or Email already exists
            cursor.execute(
                "SELECT Admin_IC_Number, Admin_Email_Address FROM Admin WHERE Admin_IC_Number = ? OR Admin_Email_Address = ?",
                (admin_ic, admin_email))
            cursor.fetchone()
            if existing:
                conn.close()
                messagebox.showerror("Error", "An admin with this IC number or email already exists.")
                return
            # Generate Admin_ID
            cursor.execute("SELECT Admin_ID FROM Admin ORDER BY Admin_ID DESC LIMIT 1")
            last_admin_id = cursor.fetchone()
            new_admin_id = f"AD{(int(last_admin_id[0][2:]) + 1 if last_admin_id else 1):03d}"
            # Insert new admin
            cursor.execute("""
                INSERT INTO Admin (
                    Admin_ID, Admin_Name, Admin_IC_Number, Admin_Phone_Number,
                    Admin_Passcode, Admin_Email_Address, Admin_Gender, Admin_Join_Date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, DATE('now'))
            """, (new_admin_id, admin_name, admin_ic, admin_phone, admin_passcode,
                  admin_email, admin_gender))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Admin registered successfully!\nYour Admin ID is: {new_admin_id}")
            clear_entries()
            show_login_frame()  # Automatically switch to login frame after successful registration
        except sqlite3.IntegrityError as e:
            conn.close()
            messagebox.showerror("Database Error", f"Registration failed: {str(e)}")
        except Exception as e:
            conn.close()
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    # Function to login admin
    def login_admin():
        global admin_ic, admin_passcode
        admin_ic = login_ic_num_entry.get()
        admin_passcode = login_passcode_entry.get()
        if admin_ic and admin_passcode:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Admin WHERE Admin_IC_Number = ? AND Admin_Passcode = ?",
                           (admin_ic, admin_passcode))
            admin = cursor.fetchone()
            conn.close()
            if admin:
                messagebox.showinfo("Success", f"Welcome {admin[1]}!")
                login_register_frame.pack_forget()  # Hide login register frame
                head_frame.pack(side=TOP, fill=X)
                main_frame.pack(side=RIGHT)
                live_location()
            else:
                messagebox.showerror("Error", "Invalid IC Number or passcode.")
        else:
            messagebox.showerror("Error", "Please fill in both IC Number and passcode.")
    # Function to clear form entries after registration
    def clear_entries():
        name_entry.delete(0, END)
        ic_entry.delete(0, END)
        gender_var.delete(0, END)
        phone_entry.delete(0, END)
        passcode_entry.delete(0, END)
        email_entry.delete(0, END)
    # Function to switch to the register frame
    def show_register_frame():
        main_frame.pack_forget()
        head_frame.pack_forget()
        login_frame.place_forget()  # Hide login frame
        register_frame.place(relx=0.5, rely=0.5, anchor='center')  # Show register frame
        register_frame.configure(fg_color='floral white')  # Set background color
    # Function to switch to the login frame
    def show_login_frame():
        main_frame.pack_forget()
        head_frame.pack_forget()
        register_frame.place_forget()  # Hide register frame
        login_frame.place(relx=0.5, rely=0.5, anchor='center')  # Show login frame
        login_frame.configure(fg_color='floral white')  # Set background color
    admin_id = None  # Global variable to store Admin_ID after verification
    def forgot_password():
        global admin_id  # Use the global variable to keep track of Admin_ID
        # Create a new frame for password recovery
        recovery_frame = Frame(login_register_frame, padx=20, pady=20, width=700, height=700)
        recovery_frame.pack_propagate(False)  # Prevent resizing
        recovery_frame.configure(bg='floral white')  # White background
        recovery_label = Label(recovery_frame, text="Password Recovery", font=("Times new roman", 35, 'bold'),
                               fg='#fd5602',
                               bg='white')
        recovery_label.place(relx=0.5, rely=0.1, anchor='center')
        # Label and Entry for IC Number
        Label(recovery_frame, text="Please enter your IC Number:", bg='white', font=("Arial", 14)).place(relx=0.5,
                                                                                                         rely=0.2,
                                                                                                         anchor='center')
        reset_identifier_entry = Entry(recovery_frame, font=("Arial", 14))  # Define the entry widget here
        reset_identifier_entry.place(relx=0.5, rely=0.3, anchor='center')
        # Function to reset the password
        def reset_password():
            global admin_id  # Use the global variable
            new_password = new_password_entry.get().strip()  # New password to set
            admin_identifier = reset_identifier_entry.get().strip()  # Get the IC number
            if not new_password:
                messagebox.showerror("Error", "Please enter a new password.")
                return
            # Validate new password length
            if len(new_password) != 6:
                messagebox.showerror("Error", "New password must be exactly 6 characters.")
                return
            try:
                conn = connect_db()
                cursor = conn.cursor()
                # Update the password using the admin's IC number
                cursor.execute("UPDATE Admin SET Admin_Passcode = ? WHERE Admin_IC_Number = ?",
                               (new_password, admin_identifier))
                conn.commit()
                messagebox.showinfo("Success", "Password has been reset successfully.")
                # Automatically go back to the login frame after resetting the password
                recovery_frame.destroy()  # Destroy the recovery frame
                show_login_frame()  # Show the login frame
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
            finally:
                conn.close()
        # Function to verify the identifier
        def verify_identifier():
            admin_identifier = reset_identifier_entry.get().strip()
            if not admin_identifier:
                messagebox.showerror("Error", "Please enter your IC Number or Email.")
                return
            try:
                conn = connect_db()
                cursor = conn.cursor()
                # Check if the identifier (IC or Email) exists
                cursor.execute("SELECT Admin_ID FROM Admin WHERE Admin_IC_Number = ? OR Admin_Email_Address = ?",
                               (admin_identifier, admin_identifier))
                admin = cursor.fetchone()
                if admin:
                    # Successful verification: Show password reset fields
                    show_reset_fields(admin[0])
                else:
                    messagebox.showerror("Error", "No admin found with the provided IC Number or Email.")
                conn.close()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
                conn.close()
        def show_reset_fields(admin_id):
            # Update and show the Admin ID label
            admin_id_label.config(text=f"Admin ID: {admin_id}")
            admin_id_label.place(relx=0.5, rely=0.4, anchor='center')  # Make sure it appears at the desired location
            # Show the New Password fields and Reset Button
            new_password_label.place(relx=0.5, rely=0.5, anchor='center')  # Show New Password label
            new_password_entry.place(relx=0.5, rely=0.6, anchor='center')  # Show New Password entry
            reset_button.place(relx=0.5, rely=0.7, anchor='center')  # Show Reset Button
        hyperlink_font = font.Font(family="Arial", size=10, underline=True)
        Button(recovery_frame, text="< Back to Login", command=lambda: (recovery_frame.destroy(), show_login_frame()),
               bg='white', fg="blue", font=hyperlink_font, activebackground='white', borderwidth=0).place(relx=0.1,
                                                                                                          rely=0.9,
                                                                                                          anchor='center')
        recovery_frame.place(relx=0.5, rely=0.5, anchor='center')  # Show recovery frame
        # Button to verify the identifier
        verify_button = Button(recovery_frame, text="Proceed", command=verify_identifier, font=("Arial", 14, 'bold'),
                               bg='#fd5602')
        verify_button.place(relx=0.5, rely=0.35, anchor='center')
        # Labels for Admin ID and New Password (hidden initially)
        admin_id_label = Label(recovery_frame, text="", bg='white', font=("Arial", 14), fg='#fd5602')
        admin_id_label.place_forget()  # Initially hidden
        # Assign the "New Password" label to a variable
        new_password_label = Label(recovery_frame, text="New Password:", bg='white', font=("Arial", 14))
        new_password_label.place_forget()  # Initially hidden
        new_password_entry = Entry(recovery_frame, show='*', font=("Arial", 14))
        new_password_entry.place_forget()  # Initially hidden
        reset_button = Button(recovery_frame, text="Reset Password", command=reset_password, font=("Arial", 14, 'bold'),
                              bg='#fd5602', fg='white')
        reset_button.place_forget()  # Initially hidden
    label_font = ('Arial', 14, 'bold')
    entry_font = ('Arial', 14)
    # Create the login frame with specified width and height
    login_frame = ctk.CTkFrame(login_register_frame, width=700, height=700, fg_color='floral white')
    login_frame.place(x=610, y=190)
    login_frame.pack_propagate(False)
    login_label = ctk.CTkLabel(
        login_frame,
        text="ADMIN LOGIN",
        font=("Times new roman", 45, "bold"),
        text_color='black'
    )
    login_label.place(x=190, y=60)
    # Update entry fields
    ic_label = ctk.CTkLabel(login_frame, text="IC Number:", font=("Arial", 18, "bold"))
    ic_label.place(x=220, y=180)
    login_ic_num_entry = ctk.CTkEntry(
        login_frame,
        font=("Arial", 18),
        width=250,
        height=35,
        border_width=2,
        corner_radius=10
    )
    login_ic_num_entry.place(x=220, y=220)
    pass_label = ctk.CTkLabel(login_frame, text="Passcode:", font=("Arial", 18, "bold"))
    pass_label.place(x=220, y=280)
    login_passcode_entry = ctk.CTkEntry(
        login_frame,
        font=("Arial", 18),
        width=250,
        height=35,
        border_width=2,
        corner_radius=10,
        show='*'
    )
    login_passcode_entry.place(x=220, y=320)
    # Update buttons
    login_button = ctk.CTkButton(
        login_frame,
        text="Login",
        command=login_admin,
        font=("Arial", 18, "bold"),
        fg_color='#fd5602',
        hover_color='#d14501',
        width=120,
        height=35,
        corner_radius=10
    )
    login_button.place(x=200, y=460)
    register_button = ctk.CTkButton(
        login_frame,
        text="Register",
        command=show_register_frame,
        font=("Arial", 18, "bold"),
        fg_color='#fd5602',
        hover_color='#d14501',
        width=120,
        height=35,
        corner_radius=10
    )
    register_button.place(x=350, y=460)
    hyperlink_font = font.Font(family="Arial", size=14, underline=True)
    Button(login_frame, text="Forgot Password?", command=forgot_password, fg="#fd5602", font=hyperlink_font,
           activebackground='white', borderwidth=0).place(x=255, y=540)
    # Create the registration frame with specified width and height (initially hidden)
    register_frame = ctk.CTkFrame(login_register_frame, width=700, height=700, corner_radius=10,
                                  fg_color='floral white')
    register_frame.pack_propagate(False)  # Prevent the frame from resizing
    register_label = ctk.CTkLabel(register_frame, text="ADMIN REGISTER", font=("Times new roman", 45, 'bold'),
                                  text_color='black')
    register_label.place(x=160, y=30)
    ctk.CTkLabel(register_frame, text="Name:", font=label_font).place(x=220, y=120)
    name_entry = ctk.CTkEntry(register_frame, font=entry_font, width=250, height=35, corner_radius=10)
    name_entry.place(x=220, y=150)
    ctk.CTkLabel(register_frame, text="IC Number:", font=label_font).place(x=220, y=190)
    ic_entry = ctk.CTkEntry(register_frame, font=entry_font, width=250, height=35, corner_radius=10)
    ic_entry.place(x=220, y=220)
    ctk.CTkLabel(register_frame, text="Gender:", font=label_font).place(x=220, y=260)
    gender_var = StringVar()
    ctk.CTkRadioButton(register_frame, text="Male", variable=gender_var, value="Male", font=entry_font,
                       fg_color='#fd5602').place(x=220, y=290)
    ctk.CTkRadioButton(register_frame, text="Female", variable=gender_var, value="Female", font=entry_font,
                       fg_color='#fd5602').place(x=320, y=290)
    gender_var.set("Male")  # Set default selection to the first option ("Male")
    ctk.CTkLabel(register_frame, text="Phone Number:", font=label_font).place(x=220, y=330)
    phone_entry = ctk.CTkEntry(register_frame, font=entry_font, width=250, height=35, corner_radius=10)
    phone_entry.place(x=220, y=360)
    ctk.CTkLabel(register_frame, text="Passcode:", font=label_font).place(x=220, y=400)
    passcode_entry = ctk.CTkEntry(register_frame, font=entry_font, width=250, height=35, corner_radius=10)
    passcode_entry.place(x=220, y=430)
    passcode_info_label = None  # Initialize the label variable
    def toggle_passcode_info():
        nonlocal passcode_info_label
        if passcode_info_label and passcode_info_label.winfo_exists():
            passcode_info_label.destroy()
            passcode_info_label = None
        else:
            passcode_info_label = ctk.CTkLabel(register_frame, text="[Passcode must be in 6 digits.]",
                                               text_color='blue', font=('Arial', 10, 'bold'))
            passcode_info_label.place(x=510, y=430)
    info_button = ctk.CTkButton(register_frame, text="!", width=20, height=20, command=toggle_passcode_info)
    info_button.place(x=480, y=435)
    ctk.CTkLabel(register_frame, text="Email Address:", font=label_font).place(x=220, y=470)
    email_entry = ctk.CTkEntry(register_frame, font=entry_font, width=250, height=35, corner_radius=10)
    email_entry.place(x=220, y=500)
    register_button = ctk.CTkButton(
        register_frame,
        text="Register",
        command=register_admin,
        font=("Arial", 18, "bold"),
        fg_color='#fd5602',
        hover_color='#d14501',
        width=120,
        height=35,
        corner_radius=10
    )
    register_button.place(x=200, y=610)
    # Button to switch back to login form
    back_to_login_button = ctk.CTkButton(
        register_frame,
        text="Back to Login",
        command=show_login_frame,
        font=("Arial", 18, 'bold'),
        fg_color='#fd5602',
        hover_color='#d14501',
        width=120,
        height=35,
        corner_radius=10
    )
    back_to_login_button.place(x=350, y=610)
    # Start with login frame
    login_frame.place(x=610, y=190)  # Adjust initial position for visibility


def add_marker_to_db(lat, lon, text, icon_path):
    """Insert marker details into the database."""
    cursor.execute('INSERT INTO markers (lat, lon, text, icon_path) VALUES (?, ?, ?, ?)',
                   (lat, lon, text, icon_path))
    conn.commit()


def add_initial_users():
    """Add predefined users to the database with specific locations."""
    users = [
        {"lat": 5.3521073, "lon": 100.3001165, "text": "Sarah",
         "icon_path": "C:/Kai Shuang/Green_Marker.jpeg"},  # Sarah matches Stall 1
        {"lat": 5.3130725, "lon": 100.2768388, "text": "John",
         "icon_path": "C:/Kai Shuang/Green_Marker.jpeg"},  # John matches Stall 2
        {"lat": 5.3301444, "lon": 100.2655045, "text": "Alice",
         "icon_path": "C:/Kai Shuang/Green_Marker.jpeg"},  # Alice matches Stall 3
        {"lat": 5.3376014, "lon": 100.2211739, "text": "Mike",
         "icon_path": "C:/Kai Shuang/Green_Marker.jpeg"},  # Mike matches Stall 4
        {"lat": 5.4108194, "lon": 100.3348786, "text": "Emma",
         "icon_path": "C:/Kai Shuang/Green_Marker.jpeg"},  # Emma matches Stall 5
        {"lat": 5.270447, "lon": 100.4196629, "text": "Ahmad", "icon_path": "C:/Kai Shuang/Green_Marker.jpeg"}
    ]
    # Clear existing users to prevent duplicates (optional)
    cursor.execute('DELETE FROM markers')
    conn.commit()
    for user in users:
        add_marker_to_db(user["lat"], user["lon"], user["text"], user["icon_path"])


# Define the fixed stalls
stalls = {
    "Stall 1": {"lat": 5.3521073, "lon": 100.3001165},
    "Stall 2": {"lat": 5.3130725, "lon": 100.2768388},
    "Stall 3": {"lat": 5.3301444, "lon": 100.2655045},
    "Stall 4": {"lat": 5.3376014, "lon": 100.2211739},
    "Stall 5": {"lat": 5.4108194, "lon": 100.3348786},
    "Stall 6": {"lat": 5.270447, "lon": 100.4196629}
}


def get_assigned_stall(user_name):
    """Return the assigned stall for a given user."""
    assignment = {
        "Sarah": "Stall 1",
        "John": "Stall 2",
        "Alice": "Stall 3",
        "Mike": "Stall 4",
        "Emma": "Stall 5",
        "Ahmad": "Stall 6"
    }
    return assignment.get(user_name, None)


def load_markers_from_db(user_lat, user_lon, tolerance=0.001):
    """Load markers from the database and display them on the map, matching user location with assigned stalls."""
    cursor.execute('SELECT lat, lon, text FROM markers')
    rows = cursor.fetchall()
    for lat, lon, text in rows:
        assigned_stall = get_assigned_stall(text)
        if not assigned_stall:
            # If no assigned stall found, default to red marker
            icon_path = "C:/Kai Shuang/Red_Marker.jpeg"
        else:
            stall_coords = stalls.get(assigned_stall)
            if stall_coords:
                # Calculate distance between user location and assigned stall
                lat_diff = abs(stall_coords["lat"] - lat)
                lon_diff = abs(stall_coords["lon"] - lon)
                if lat_diff <= tolerance and lon_diff <= tolerance:
                    icon_path = "C:/Kai Shuang/Green_Marker.jpeg"  # Matching location
                else:
                    icon_path = "C:/Kai Shuang/Red_Marker.jpeg"  # Not matching
            else:
                icon_path = "C:/Kai Shuang/Red_Marker.jpeg"  # Stall data missing
        # Load and resize the marker icon
        try:
            icon_image = Image.open(icon_path)
            icon_image = icon_image.resize((80, 80), Image.LANCZOS)
            custom_icon = ImageTk.PhotoImage(icon_image)
        except Exception as e:
            print(f"Error loading icon for {text}: {e}")
            continue  # Skip this marker if icon fails to load
        # Set the marker on the map with the correct icon
        marker = map_widget.set_marker(lat, lon, text=text, icon=custom_icon)
        marker.command = on_click


def on_click(marker):
    print(f"Marker clicked: {marker.position}")


def toggle_menu():
    def collapse_toggle_menu():
        toggle_menu_fm.destroy()
        toggle_btn.configure(text=' ≡ ')
        toggle_btn.configure(command=toggle_menu)

    toggle_menu_fm = ctk.CTkFrame(
        root,
        fg_color='#FFC4A4',  # Light orange background for sidebar
        width=500,
        height=1080
    )
    # Create navigation buttons with customtkinter
    nav_buttons = [
        ("Live Location Tracking", live_location),
        ("Contract Renewal Management", contract_renewal),
        ("Tenant & Stall Management", create_tenant_stall_frame),
        ("Payment Management", payment_management),
        ("Analytics & Reports", analytics_and_report),
        ("Inbox", admin_inbox),
        ("Settings", general_setting)
    ]
    for i, (text, command) in enumerate(nav_buttons):
        btn = ctk.CTkButton(
            toggle_menu_fm,
            text=text,
            command=lambda cmd=command: [cmd(), collapse_toggle_menu()] if cmd else None,
            font=("Nunito", 22, "bold"),
            fg_color='#fd5602',  # Orange background
            text_color='white',
            hover_color='#FFC4A4',  # Light orange hover color
            width=460,
            height=60,
            corner_radius=10
        )
        # Add some padding and spacing between buttons
        btn.place(x=20, y=50 + i * 80)
    toggle_menu_fm.place(x=0, y=60)  # Place behind the head frame
    toggle_btn.configure(text=' X ')
    toggle_btn.configure(command=collapse_toggle_menu)


# Add this function before the toggle_menu function
def confirm_logout():
    """Confirm before logging out"""
    if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
        root.destroy()


# Update the head_frame section
head_frame = ctk.CTkFrame(root, fg_color='#fd5602', height=120)  # Increased height
toggle_btn = ctk.CTkButton(
    head_frame,
    text=' ≡ ',
    command=toggle_menu,
    font=("Bold", 28),  # Increased font size
    fg_color='transparent',
    text_color='#fedebe',
    hover_color='#d14501',
    width=60,  # Increased width
    height=60  # Added height
)
toggle_btn.pack(side=LEFT, padx=20)  # Increased padding
title_lb = ctk.CTkLabel(
    head_frame,
    text='Government Stall Rental System - Admin Dashboard',
    font=('Arial', 28, 'bold'),  # Increased font size
    text_color='#fedebe'
)
title_lb.pack(side=LEFT, padx=30)  # Increased padding
'''
def fetch_admin_name(admin_ic_number):
    try:
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Admin_Name FROM Admin WHERE Admin_IC_Number = ?", (admin_ic_number,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        else:
            messagebox.showerror("Error", "Admin not found.")
            return "Admin"
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Error fetching admin name: {str(e)}")
        return "Admin"
admin_name = fetch_admin_name(login_ic_num_entry.get())
admin_label = ctk.CTkLabel(
    head_frame,
    text=f'Admin: {admin_name}',
    font=('Arial', 20, 'bold'),
    text_color='#fedebe'
)
admin_label.pack(side=LEFT, padx=20)  # Adjust padding as needed
'''
# Update logout button
logout_btn = ctk.CTkButton(
    head_frame,
    text='Logout',
    command=confirm_logout,
    font=('Arial', 20, "bold"),  # Increased font size
    fg_color='transparent',
    text_color='white',
    hover_color='#d14501',
    width=120,  # Increased width
    height=40,  # Added height
    corner_radius=8
)
logout_btn.pack(side=RIGHT, padx=30)  # Increased padding


def get_nearest_stall(user_lat, user_lon, tolerance=0.01):
    """Find the nearest stall to the user based on latitude and longitude within a tolerance."""
    # This function is now integrated into load_markers_from_db for each user
    pass  # Not used anymore


def live_location():
    global location_frame, location_label
    location_frame = Frame(main_frame)
    location_frame.place(relwidth=1, relheight=1)
    global map_widget
    map_widget = tkintermapview.TkinterMapView(location_frame, width=1600, height=700)
    map_widget.place(x=150, y=150)
    map_widget.set_position(5.2945, 100.2593)  # Center map on Bayan Lepas, Penang
    map_widget.set_zoom(15)

    # Create a frame for search controls
    search_frame = Frame(location_frame)
    search_frame.place(x=150, y=100)

    # Add date picker
    date_label = Label(search_frame, text="Select Date:", font=('Arial', 12))
    date_label.pack(side=LEFT, padx=5)
    date_picker = DateEntry(search_frame, width=12, background='darkblue',
                            foreground='white', borderwidth=2, font=('Arial', 12))
    date_picker.pack(side=LEFT, padx=5)

    # Add location search
    search_entry = Entry(search_frame, font=('Arial', 12), width=30)
    search_entry.pack(side=LEFT, padx=5)
    search_btn = Button(search_frame, text="Search Location", font=('Arial', 12, 'bold'),
                        command=lambda: perform_search(search_entry.get()))
    search_btn.pack(side=LEFT)

    # Add search by date button
    date_search_btn = Button(search_frame, text="Search by Date", font=('Arial', 12, 'bold'),
                             command=lambda: load_markers_from_db(5.285153, 100.456238,
                                                                  date_picker.get_date().strftime('%d-%m-%Y')))
    date_search_btn.pack(side=LEFT, padx=5)

    # Add location label next to search button
    location_label = Label(search_frame, text="", font=('Arial', 12), wraplength=1000)
    location_label.pack(side=LEFT, padx=10)

    # Add a refresh button below the map
    refresh_btn = Button(location_frame, text="Refresh ↻", font=('Arial', 12, 'bold'),
                         command=lambda: load_markers_from_db(5.285153, 100.456238,
                                                              datetime.now().strftime('%d-%m-%Y')),
                         bd=0, highlightthickness=0, relief='flat', fg='blue')
    refresh_btn.place(x=150, y=870)

    # Load initial markers with today's date
    load_markers_from_db(5.285153, 100.456238, datetime.now().strftime('%d-%m-%Y'))


def perform_search(query):
    geolocator = Nominatim(user_agent="YourAppName/1.0 (your_email@example.com)")
    try:
        location = geolocator.geocode(f"{query}, Penang, Malaysia")
        if location:
            map_widget.set_position(location.latitude, location.longitude)
            map_widget.set_zoom(15)
            location_label.config(text=f"Moved to: {location.address} at ({location.latitude}, {location.longitude})")
            print(f"Moved to: {location.address} at ({location.latitude}, {location.longitude})")
        else:
            location_label.config(text="Location not found. Please enter a valid postcode.")
    except Exception as e:
        location_label.config(text=f"Error occurred: {e}")


def load_markers_from_db(center_lat, center_lon, selected_date):
    """Load markers from the Attendance table and display them on the map."""
    conn = sqlite3.connect('govRental.db')
    cursor = conn.cursor()

    # Fetch attendance data for selected date
    cursor.execute("""
        SELECT Clock_In_latitude, Clock_In_longitude, Clock_In_status, name
        FROM Attendance
        WHERE date = ?
    """, (selected_date,))
    records = cursor.fetchall()
    conn.close()

    # Clear existing markers
    map_widget.delete_all_marker()

    # Check if there are any records for the selected date
    if not records:
        messagebox.showinfo("No Records", f"No attendance records found for {selected_date}")
        return

    # Loop through each record to add markers
    for lat, lon, status, name in records:
        if lat is not None and lon is not None:
            color_circle = "lime green" if status == "Correct" else "red"
            color_outside = "green" if status == "Correct" else "darkred"

            # Create marker with a custom callback that extracts marker text
            def create_marker_callback(marker):
                show_tenant_info(marker.text, "Correct" if marker.marker_color_circle == "lime green" else "Wrong")

            # Create marker and bind callback
            marker = map_widget.set_marker(
                lat,
                lon,
                text=name,
                marker_color_circle=color_circle,
                marker_color_outside=color_outside,
                command=create_marker_callback
            )


def show_tenant_info(name, status):
    # Create a popup window
    popup = Toplevel()
    popup.title("Tenant Information")
    popup.geometry("1000x800")
    # Connect to database
    conn = sqlite3.connect('govRental.db')
    cursor = conn.cursor()
    # Get today's attendance data for the specific tenant
    cursor.execute("""
            SELECT name, Clock_In_latitude, Clock_In_longitude, Clock_In_status, 
                   Clock_Out_latitude, Clock_Out_longitude, Clock_Out_status
            FROM Attendance 
            WHERE name = ? AND date = ?
        """, (name, datetime.now().strftime('%d-%m-%Y')))
    # Fetch the data
    attendance_data = cursor.fetchone()
    Label(popup, text="Tenant Location Information", font=("Arial", 24, "bold")).pack(pady=30)
    cor_frame = Frame(popup, bg='SkyBlue1')
    cor_frame.pack(pady=10)
    if attendance_data:
        # Create labels to display the data
        Label(cor_frame, text=f"Clock In Location: ({attendance_data[1]}, {attendance_data[2]})",
              font=("Arial", 14, 'bold'), bg='SkyBlue1').pack(pady=5)
        Label(cor_frame, text=f"Clock In Status: {attendance_data[3]}",
              font=("Arial", 14), bg='SkyBlue1').pack(pady=5)
        if attendance_data[4] and attendance_data[5]:  # If clock out data exists
            Label(cor_frame, text=f"Clock Out Location: ({attendance_data[4]}, {attendance_data[5]})",
                  font=("Arial", 14, 'bold'), bg='SkyBlue1').pack(pady=5)
            Label(cor_frame, text=f"Clock Out Status: {attendance_data[6]}",
                  font=("Arial", 14), bg='SkyBlue1').pack(pady=5)
    conn.close()
    # Display tenant information
    Label(popup, text=f"Tenant: {name}", font=("Arial", 16)).pack(pady=20)
    Label(popup, text=f"Current Status: {'Correct Location' if status == 'Correct' else 'Wrong Location'}",
          font=("Arial", 16, "bold"), fg='green' if status == 'Correct' else 'red').pack(pady=10)

    # Button(popup, text="Close", font=("Arial", 14), command=popup.destroy).pack(pady=20)
    def show_reason_fields():
        # Create reason input fields if they don't exist
        reason_label = Label(popup, text="Enter Reason to Update Status:", font=("Arial", 14, 'bold'))
        reason_text = Text(popup, height=4, width=60, font=("Arial", 14))

        def confirm_reason():
            reason = reason_text.get("1.0", "end-1c").lower()
            if "issue" in reason or "problem" in reason:
                # Update Status_Reason and Status in database
                conn = sqlite3.connect('govRental.db')
                cursor = conn.cursor()
                # Toggle status between Correct and Wrong
                new_status = 'Wrong' if status == 'Correct' else 'Correct'
                cursor.execute("""
                    UPDATE Attendance 
                    SET Status_Reason = ?, Clock_In_status = ?, Clock_Out_status = ?
                    WHERE name = ? AND date = ?
                """, (reason, new_status, new_status, name, datetime.now().strftime('%d-%m-%Y')))
                conn.commit()
                conn.close()
                # Update all markers with the toggled color
                for marker in map_widget.canvas_marker_list:
                    marker.delete()
                    # Get coordinates from attendance data
                    if attendance_data and attendance_data[1] and attendance_data[2]:
                        # Toggle colors based on new status
                        color_circle = "red" if status == "Correct" else "lime green"
                        color_outside = "darkred" if status == "Correct" else "green"
                        map_widget.set_marker(attendance_data[1], attendance_data[2],
                                              text=marker.text, marker_color_circle=color_circle,
                                              marker_color_outside=color_outside)
                messagebox.showinfo("Success", "Reason accepted and status updated")
                popup.destroy()
            else:
                messagebox.showerror("Error", "Reason must include words like 'issue' or 'problem'")

        # Create action buttons if they don't exist
        confirm_button = Button(popup, text="Confirm", font=("Arial", 14, 'bold'), command=confirm_reason)
        cancel_button = Button(popup, text="Cancel", font=("Arial", 14),
                               command=lambda: [reason_label.pack_forget(), reason_text.pack_forget(),
                                                confirm_button.pack_forget(), cancel_button.pack_forget(),
                                                update_button.pack(pady=20)])
        # Show reason input fields
        reason_label.pack(pady=20)
        reason_text.pack(pady=10)
        # Show action buttons
        confirm_button.pack(pady=10)
        cancel_button.pack(pady=10)
        # Hide update status button
        update_button.pack_forget()

    # Create and pack update button
    update_button = Button(popup, text="Update Status", font=("Arial", 14, "bold"), fg='white', bg='#1757b7',
                           activebackground='white', command=show_reason_fields)
    update_button.pack(pady=20)

    def add_stalls_info():
        """Optional: Display stall locations on the map as reference (without markers)."""
        # You can add visual indicators like circles or lines if needed
        pass


def on_treeview_select(event, treeview):
    selected_item = treeview.selection()
    if selected_item:
        item_values = treeview.item(selected_item)['values']
        # Update the entry fields with the selected row's data
        # Set the state of entry fields to normal before updating
        for entry in [request_id_entry, stall_id_entry, postcode_entry, tenant_id_entry,
                      username_entry, contact_entry, status_entry, payment_entry, stallmg_entry, violation_entry,
                      endDate_entry]:
            entry.config(state='normal')  # Enable editing
        request_id_entry.delete(0, END)
        request_id_entry.insert(0, item_values[0])
        stall_id_entry.delete(0, END)
        stall_id_entry.insert(0, item_values[1])
        postcode_entry.delete(0, END)
        postcode_entry.insert(0, item_values[2])
        tenant_id_entry.delete(0, END)
        tenant_id_entry.insert(0, item_values[3])
        username_entry.delete(0, END)
        username_entry.insert(0, item_values[4])
        contact_entry.delete(0, END)
        contact_entry.insert(0, item_values[5])
        status_entry.delete(0, END)
        status_entry.insert(0, item_values[6])
        payment_entry.delete(0, END)
        payment_entry.insert(0, item_values[7])
        stallmg_entry.delete(0, END)
        stallmg_entry.insert(0, item_values[8])
        violation_entry.delete(0, END)
        violation_entry.insert(0, item_values[9])
        endDate_entry.delete(0, END)
        endDate_entry.insert(0, item_values[10])
        # Set the state of entry fields to readonly after updating
        for entry in [request_id_entry, stall_id_entry, postcode_entry, tenant_id_entry,
                      username_entry, contact_entry, status_entry, payment_entry, stallmg_entry, violation_entry,
                      endDate_entry]:
            entry.config(state='readonly')


def approve_selected():
    selected_item = treeview.selection()
    if selected_item:
        # Update the status entry to 'Approved'
        status_entry.config(state='normal')  # Enable editing
        status_entry.delete(0, END)
        status_entry.insert(0, "Approved")
        status_entry.config(state='readonly')  # Set back to readonly
        # Get the selected item ID (Request_ID) to update the database
        request_id = treeview.item(selected_item)['values'][0]  # Assuming Request_ID is the first column
        refresh_treeview()
        # Update the database
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE PendingApprovalRequest SET Status = ? WHERE Request_ID = ?", ("Approved", request_id))
        conn.commit()
        conn.close()


def open_reject_reason_window(request_id):
    # Create a new Toplevel window
    reject_window = Toplevel()
    reject_window.title("Reason for Rejection")
    reject_window.geometry("600x350")
    # Add a label
    Label(reject_window, text="Select a reason for rejection:").pack(pady=10)
    # Create a Combobox for rejection reasons
    reasons = ["Late payment history", "Bad stall management"]
    reason_combobox = ttk.Combobox(reject_window, values=reasons, state="readonly")
    reason_combobox.pack(pady=10)
    reason_combobox.current(0)  # Set the default selection

    # Function to update status
    def update_status(request_id, new_status):
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE PendingApprovalRequest SET Status = ? WHERE Request_ID = ?", (new_status, request_id))
        conn.commit()
        conn.close()

    # Function to handle submission
    def submit_reason():
        # Get the selected item ID (Request_ID)
        selected_item = treeview.selection()
        if selected_item:
            request_id = treeview.item(selected_item)['values'][0]  # Assuming Request_ID is the first column
            # Fetch the current payment_history and stall_management for the selected request
            conn = sqlite3.connect('govRental.db')
            cursor = conn.cursor()
            cursor.execute("SELECT Payment_History, Stall_Management FROM PendingApprovalRequest WHERE Request_ID = ?",
                           (request_id,))
            payment_history, stall_management = cursor.fetchone()
            # Get the selected reason from the drop-down
            rejection_reason = reason_combobox.get()  # Use reason_combobox
            # Logic to check conditions
            if rejection_reason == "Late payment history" and payment_history != 0:
                print("Yes")
                messagebox.showinfo("Invalid Reason",
                                    "Rejection reason 'Late payment history' can only be selected when payment history is 0.")
                # Reset status to Pending
                update_status(request_id, "Pending")
                refresh_treeview()
                return
            if rejection_reason == "Bad stall management" and stall_management != 0:
                print("No")
                messagebox.showinfo("Invalid Reason",
                                    "Rejection reason 'Bad stall management' can only be selected when stall management is 0.")
                # Reset status to Pending
                update_status(request_id, "Pending")
                refresh_treeview()
                return
            # If conditions are met, proceed to update the status and reason
            cursor.execute("UPDATE PendingApprovalRequest SET Status = ?, Rejection_Reason = ? WHERE Request_ID = ?",
                           ("Rejected", rejection_reason, request_id))
            conn.commit()
            conn.close()
            # Refresh the treeview to reflect changes
            refresh_treeview()
            reject_window.destroy()  # Close the reject window after submission

    # Submit button
    submit_button = Button(reject_window, text="Submit", command=submit_reason)
    submit_button.pack(pady=20)


def reject_selected():
    selected_item = treeview.selection()
    if selected_item:
        # Get the selected item ID (Request_ID) to update the database
        request_id = treeview.item(selected_item)['values'][0]  # Assuming Request_ID is the first column
        # Open the reason input window
        open_reject_reason_window(request_id)


def pending_selected():
    selected_item = treeview.selection()
    if selected_item:
        # Update the status entry to 'Pending'
        status_entry.config(state='normal')  # Enable editing
        status_entry.delete(0, END)
        status_entry.insert(0, "Pending")
        status_entry.config(state='readonly')  # Set back to readonly
        # Get the selected item ID (Request_ID) to update the database
        request_id = treeview.item(selected_item)['values'][0]  # Assuming Request_ID is the first column
        # Update the database
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE PendingApprovalRequest SET Status = ? WHERE Request_ID = ?", ("Pending", request_id))
        conn.commit()
        conn.close()


def refresh_treeview():
    # Clear the current data in the Treeview
    for item in treeview.get_children():
        treeview.delete(item)
    # Fetch fresh tenant data
    tenant_data = fetch_tenant_data()
    for tenant in tenant_data:
        treeview.insert('', 'end', values=tenant)
    # Schedule the next refresh
    treeview.after(10000, refresh_treeview)  # Refresh every 3000 milliseconds (3 seconds)


# Function to create the tenant stall Treeview
def tenant_stall_treeview():
    global request_id_entry, stall_id_entry, postcode_entry, tenant_id_entry, username_entry, contact_entry
    global status_entry, payment_entry, stallmg_entry, violation_entry, endDate_entry, treeview  # Declare them as global
    location_frame.destroy()  # Assuming `location_frame` is a global variable created elsewhere
    for widget in contract_frame.winfo_children():
        if isinstance(widget, Frame):  # Only destroy frames, keep the navigation buttons
            widget.destroy()
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 12, 'bold'))
    style.configure("Treeview", font=("Arial", 12))
    # Create a new frame
    contract_frame2 = Frame(contract_frame, width=1350, height=800)
    contract_frame2.place(x=500, y=100)
    # Define columns for the Treeview
    columns = (
        'Request ID', 'Stall ID', 'Postcode', 'Tenant ID', 'Username', 'Contact Number', 'Status', 'Payment History',
        'Stall Management', 'Contract Violation', 'Contract End Date')
    # Create the Treeview
    treeview = ttk.Treeview(contract_frame2, columns=columns, show='headings')
    # Define column headings and widths
    for column in columns:
        treeview.heading(column, text=column, anchor='center')
        treeview.column(column, anchor='center', width=150)  # Adjust width as needed
    # Fetch data and insert into Treeview
    tenant_data = fetch_tenant_data()
    for tenant in tenant_data:
        treeview.insert('', 'end', values=tenant)  # Ensure tenant is a tuple
    # Place the Treeview widget
    treeview.place(x=10, y=0, width=1320, height=350)
    # Bind the select event to update entry fields
    treeview.bind('<<TreeviewSelect>>', lambda event: on_treeview_select(event, treeview))
    # --- Add Search Bar ---
    search_frame = Frame(contract_frame2)
    search_frame.place(x=10, y=360, width=1310, height=50)  # Position and size of search frame
    search_label = Label(search_frame, text="Search:", font=("Arial", 14))
    search_label.place(x=10, y=10)  # Position of the label within search_frame
    search_entry = Entry(search_frame, font=("Arial", 14), width=30)
    search_entry.place(x=80, y=10)  # Position of the entry within search_frame
    search_btn = Button(search_frame, text="Search", font=("Arial", 14, 'bold'),
                        command=lambda: search_treeview(treeview, search_entry.get()))
    search_btn.place(x=430, y=4)  # Position of the search button
    reset_btn = Button(search_frame, text="Reset", font=("Arial", 14, 'bold'),
                       command=lambda: reset_treeview(treeview))
    reset_btn.place(x=520, y=4)  # Position of the reset button
    # Entry fields for selected data
    request_ID_Label = Label(contract_frame2, text="Request ID:", font=('Arial', 14, 'bold'))
    request_ID_Label.place(x=10, y=450)
    request_id_entry = Entry(contract_frame2, font=("Arial", 14), width=15)
    request_id_entry.place(x=210, y=450)
    stall_ID_Label = Label(contract_frame2, text="Stall ID:", font=('Arial', 14, 'bold'))
    stall_ID_Label.place(x=10, y=480)
    stall_id_entry = Entry(contract_frame2, font=("Arial", 14), width=15)
    stall_id_entry.place(x=210, y=480)
    postcode_Label = Label(contract_frame2, text="Postcode:", font=('Arial', 14, 'bold'))
    postcode_Label.place(x=10, y=510)
    postcode_entry = Entry(contract_frame2, font=("Arial", 14), width=15)
    postcode_entry.place(x=210, y=510)
    tenant_id__Label = Label(contract_frame2, text="Tenant ID:", font=('Arial', 14, 'bold'))
    tenant_id__Label.place(x=10, y=540)
    tenant_id_entry = Entry(contract_frame2, font=("Arial", 14), width=15)
    tenant_id_entry.place(x=210, y=540)
    username_Label = Label(contract_frame2, text="Tenant Username:", font=('Arial', 14, 'bold'))
    username_Label.place(x=10, y=570)
    username_entry = Entry(contract_frame2, font=("Arial", 14), width=15)
    username_entry.place(x=210, y=570)
    contact_Label = Label(contract_frame2, text="Contact Number:", font=('Arial', 14, 'bold'))
    contact_Label.place(x=10, y=600)
    contact_entry = Entry(contract_frame2, font=("Arial", 14), width=15)
    contact_entry.place(x=210, y=600)
    status_Label = Label(contract_frame2, text="Status:", font=('Arial', 14, 'bold'))
    status_Label.place(x=10, y=630)
    status_entry = Entry(contract_frame2, font=("Arial", 14), width=15)
    status_entry.place(x=210, y=630)
    payment_Label = Label(contract_frame2, text="Payment History:", font=('Arial', 14, 'bold'))
    payment_Label.place(x=550, y=450)
    payment_entry = Entry(contract_frame2, font=("Arial", 14), width=15)
    payment_entry.place(x=800, y=450)
    stallmg_Label = Label(contract_frame2, text="Stall Management:", font=('Arial', 14, 'bold'))
    stallmg_Label.place(x=550, y=480)
    stallmg_entry = Entry(contract_frame2, font=("Arial", 14), width=15)
    stallmg_entry.place(x=800, y=480)
    violation_Label = Label(contract_frame2, text="Any contract violations:", font=('Arial', 14, 'bold'))
    violation_Label.place(x=550, y=510)
    violation_entry = Entry(contract_frame2, font=("Arial", 14), width=15)
    violation_entry.place(x=800, y=510)
    endDate_Label = Label(contract_frame2, text="Contract End Date:", font=('Arial', 14, 'bold'))
    endDate_Label.place(x=550, y=540)
    endDate_entry = Entry(contract_frame2, font=("Arial", 14), width=15)
    endDate_entry.place(x=800, y=540)
    approve_button = Button(contract_frame2, text="Approve", font=('Arial', 14, 'bold'), fg="black", bg="#fd5602",
                            width=10, command=approve_selected)
    approve_button.place(x=1200, y=650)
    reject_button = Button(contract_frame2, text="Reject", font=('Arial', 14, 'bold'), fg="white", bg="#002400",
                           width=10, command=reject_selected)
    reject_button.place(x=1200, y=700)
    pending_button = Button(contract_frame2, text="Pending", font=('Arial', 14, 'bold'), fg="white", bg="#002400",
                            width=10, command=pending_selected)
    pending_button.place(x=1200, y=750)


def search_treeview(treeview, query):
    """Search function to filter the Treeview based on the query."""
    # Remove existing rows
    for row in treeview.get_children():
        treeview.delete(row)
    # Fetch new data filtered by the query (case-insensitive search)
    tenant_data = fetch_tenant_data()  # Fetch the original data
    filtered_data = [tenant for tenant in tenant_data if query.lower() in str(tenant).lower()]
    # Insert filtered data back into the Treeview
    for tenant in filtered_data:
        treeview.insert('', 'end', values=tenant)


def reset_treeview(treeview):
    """Reset the Treeview to show all data."""
    # Clear the search entry and reload all data
    for row in treeview.get_children():
        treeview.delete(row)
    # Fetch the original data
    tenant_data = fetch_tenant_data()
    for tenant in tenant_data:
        treeview.insert('', 'end', values=tenant)
    refresh_treeview()


def contract_renewal():
    global contract_frame, label1, label2, label3, show_label1, show_label2, show_label3, renewal_frame2
    location_frame.destroy()
    contract_frame = Frame(main_frame)
    contract_frame.place(relwidth=1, relheight=1)
    for widget in contract_frame.winfo_children():
        if isinstance(widget, Frame) and widget != renewal_frame2:  # Skip nav_frame
            widget.destroy()

    def show_label1():
        hide_all_labels()  # Hide all other labels
        label1.place(x=500, y=25)  # Show label1
        line1.place(x=500, y=label1.winfo_y() + 35, relwidth=0.7)  # Place line under label1
        tenant_stall_treeview()  # Call Treeview function
        print("Yes 1")

    def show_label2():
        hide_all_labels()  # Hide all other labels
        label2.place(x=500, y=25)  # Show label2
        line2.place(x=500, y=label2.winfo_y() + 35, relwidth=0.7)  # Place line under label2
        print("Yes 2")

        def initialize_treeview(parent_frame):
            global tree  # Declare tree as global to access it in other functions
            tree = ttk.Treeview(parent_frame, columns=(
                'Stall_ID', 'Stall_Address', 'Tenant_ID', 'Tenant_Username', 'Contract_End_Date', 'Rental_Amount'),
                                show='headings')
            # Define the column headings
            tree.heading('Stall_ID', text='Stall ID')
            tree.heading('Stall_Address', text='Stall Address')
            tree.heading('Tenant_ID', text='Tenant ID')
            tree.heading('Tenant_Username', text='Tenant Username')
            tree.heading('Contract_End_Date', text='Contract End Date')
            tree.heading('Rental_Amount', text='Rental Amount')
            # Set column widths (adjust these values as needed)
            tree.column('Stall_ID', width=100, anchor='center')
            tree.column('Stall_Address', width=400)
            tree.column('Tenant_ID', width=100, anchor='center')
            tree.column('Tenant_Username', width=200, anchor='center')
            tree.column('Contract_End_Date', width=200, anchor='center')
            tree.column('Rental_Amount', width=150, anchor='center')
            # Configure styles
            style = ttk.Style()
            style.configure('Treeview.Heading', font=('Arial', 12, 'bold'))  # Heading font
            style.configure('Treeview', font=('Arial', 12))  # Record font
            # Position the Treeview and scrollbar in the window using place
            tree.place(x=0, y=0, width=1350, height=350)

        def upcoming_renewal():
            global contract_frame
            # Clear existing frames while keeping navigation buttons
            for widget in contract_frame.winfo_children():
                if isinstance(widget, Frame) and widget != contract_frame:
                    widget.destroy()
            # Create a new renewal frame for upcoming renewals
            renewal_frame2 = Frame(contract_frame, width=1350, height=800)
            renewal_frame2.place(x=500, y=100)
            # Initialize Treeview
            initialize_treeview(renewal_frame2)
            # Show upcoming renewals in the Treeview
            show_upcoming_renewals()

            def show_expired_contracts():
                expired_window = Toplevel()
                expired_window.title("Expired Contracts")
                expired_window.geometry("800x600")

                conn = sqlite3.connect('govRental.db')
                cursor = conn.cursor()
                current_date = datetime.now().date()
                cursor.execute('''SELECT Stall_ID, Stall_Address, Tenant_ID, Tenant_Username, Contract_End_Date, Rental_Amount
                                  FROM Stall 
                                  WHERE Contract_End_Date < ?''', (current_date,))
                rows = cursor.fetchall()
                conn.close()

                # Create a text widget to display the expired contracts
                expired_text = Text(expired_window, wrap=WORD, font=('Arial', 12))
                expired_text.pack(fill=BOTH, expand=True)

                # Check if there are any expired contracts
                if not rows:
                    expired_text.insert(END, "No contracts expired.\n")
                else:
                    # Insert the data into the text widget
                    for row in rows:
                        expired_text.insert(END, f"Stall ID: {row[0]}\n")
                        expired_text.insert(END, f"Stall Address: {row[1]}\n")
                        expired_text.insert(END, f"Tenant ID: {row[2]}\n")
                        expired_text.insert(END, f"Tenant Username: {row[3]}\n")
                        expired_text.insert(END, f"Contract End Date: {row[4]}\n")
                        expired_text.insert(END, f"Rental Amount: {row[5]}\n")
                        expired_text.insert(END, "-" * 50 + "\n\n")

            expired_button = Button(renewal_frame2, text='Expired Contracts', command=show_expired_contracts,
                                    font=('Arial', 12, 'underline'), fg='blue', bg='ivory2', activebackground='ivory2',
                                    bd=0, cursor="hand2")
            expired_button.place(x=0, y=380)

            upcoming_button = Button(renewal_frame2, text='Show Upcoming Renewals', command=show_upcoming_renewals,
                                     font=('Arial', 12, 'bold'), fg='#fedebe', bg='#fd5602', activebackground='white')
            upcoming_button.place(x=0, y=420)
            show_all_button = Button(renewal_frame2, text='Show All Records', command=show_all_records,
                                     font=('Arial', 12, 'bold'), fg='#fedebe', bg='#fd5602', activebackground='white')
            show_all_button.place(x=0, y=460)
            global send_reminder_button  # Declare send_reminder_button as global
            send_reminder_button = Button(renewal_frame2, text='Remind Tenant to Renew Contract',
                                          command=send_reminder_for_renewals, font=('Arial', 12, 'bold'), fg='sky blue',
                                          bg='blue2', activebackground='white')
            send_reminder_button.place(x=0, y=460)
            send_reminder_button.place_forget()  # Initially hide the button

            def on_treeview_select(event):
                selected_item = tree.selection()  # Get the selected item
                if selected_item:
                    send_reminder_button.place(x=0, y=460)  # Show the button if something is selected
                else:
                    send_reminder_button.place_forget()  # Hide the button if nothing is selected

            # Bind Treeview selection event
            tree.bind('<<TreeviewSelect>>', on_treeview_select)

        def show_upcoming_renewals():
            conn = sqlite3.connect('govRental.db')
            cursor = conn.cursor()
            # Calculate the date 30 days from now
            current_date = datetime.now().date()
            future_date = current_date + timedelta(days=30)
            # Fetch upcoming renewals
            cursor.execute('''SELECT Stall_ID, Stall_Address, Tenant_ID, Tenant_Username, Contract_End_Date, Rental_Amount
                              FROM Stall 
                              WHERE Contract_End_Date BETWEEN ? AND ?''', (current_date, future_date))
            rows = cursor.fetchall()
            conn.close()
            # Clear existing records in the Treeview
            tree.delete(*tree.get_children())
            # Insert upcoming renewal data into the Treeview
            for row in rows:
                tree.insert('', END, values=row)

        def show_all_records():
            conn = sqlite3.connect('govRental.db')
            cursor = conn.cursor()
            # Fetch all records
            cursor.execute('''SELECT Stall_ID, Stall_Address, Tenant_ID, Tenant_Username, Contract_End_Date, Rental_Amount
                              FROM Stall''')
            rows = cursor.fetchall()
            conn.close()
            # Clear existing records in the Treeview
            tree.delete(*tree.get_children())
            # Insert all records data into the Treeview
            for row in rows:
                tree.insert('', END, values=row)

        def fetch_tenant_username(tenant_id):
            conn = sqlite3.connect("govRental.db")
            cursor = conn.cursor()
            cursor.execute("SELECT Tenant_Username FROM Tenant WHERE Tenant_ID = ?", (tenant_id,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None

        def send_reminder_for_renewals():
            reminder_window = Toplevel()
            reminder_window.title("Send Reminder")
            reminder_window.geometry("800x800")
            label_font = ("Arial", 12, 'bold')
            entry_font = ("Arial", 12)
            # Tenant ID Entry
            tenant_id_label = Label(reminder_window, text="Tenant ID:")
            tenant_id_label.pack(pady=5)
            tenant_id_entry = Entry(reminder_window)
            tenant_id_entry.pack(pady=5)
            # Tenant Username Entry
            username_label = Label(reminder_window, text="Tenant Username:")
            username_label.pack(pady=5)
            username_entry = Entry(reminder_window, state='readonly', font=entry_font)
            username_entry.pack(pady=5)

            # Function to update the entry state
            def update_username_entry_state():
                if username_entry.get():  # Check if there's a value
                    username_entry.config(state='readonly')  # Set to read-only if there's a value
                else:
                    username_entry.config(state='normal')  # Set to normal state if empty

            def fetch_username():
                tenant_id = tenant_id_entry.get()
                print(f"Fetching username for Tenant ID: {tenant_id}")  # Debugging line
                tenant_username = fetch_tenant_username(tenant_id)
                if tenant_username:
                    username_entry.delete(0, END)
                    username_entry.insert(0, tenant_username)
                    print(f"Found username: {tenant_username}")  # Debugging line
                    update_username_entry_state()  # Update entry state after setting value
                else:
                    messagebox.showwarning("Input Error", "Tenant ID not found.")
                    print("Tenant ID not found.")  # Debugging line
                    username_entry.delete(0, END)  # Clear the entry if not found
                    update_username_entry_state()  # Update entry state

            # Button to fetch Tenant Username
            fetch_button = Button(reminder_window, text="Fetch Username", command=fetch_username)
            fetch_button.pack(pady=5)
            # Date Calendar
            cal = Calendar(reminder_window, selectmode='day', year=datetime.now().year, month=datetime.now().month,
                           day=datetime.now().day)
            cal.pack(pady=10)
            # Reminder Message Entry with default message
            default_message = "Dear Tenant, your rental contract is due soon. If you want to renew your contract, please send us a request."
            message_label = Label(reminder_window, text="Reminder Message:", font=label_font)
            message_label.pack(pady=5)
            message_entry = Text(reminder_window, width=100, height=5, font=entry_font, wrap=WORD)
            message_entry.insert(END, default_message)
            message_entry.pack(pady=5)

            def save_reminder(tenant_id, tenant_username, datetime_str, message, date):
                print(
                    f"Inserting into Reminders: Tenant_ID={tenant_id}, Tenant_Username={tenant_username}, Date_Time={datetime_str}, Message={message}")  # Debugging print
                conn = sqlite3.connect("govRental.db")
                try:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO Reminders (Tenant_ID, Tenant_Username, Date_Time, Message, read)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (tenant_id, tenant_username, datetime_str, message, 0))  # Ensure this order is correct
                    conn.commit()
                    # Fetch the last entry to verify
                    cursor.execute("SELECT * FROM Reminders ORDER BY rowid DESC LIMIT 1")
                    last_entry = cursor.fetchone()
                    print("Last Entry:", last_entry)  # Debugging print
                    # Prepare reminder for JSON
                    reminder = {
                        "message": message,
                        "datetime": f"{date} {datetime_str.split(' ')[1]}"  # Combine date and time correctly
                    }
                    # Save reminder to JSON file
                    with open("reminder.json", "w") as f:
                        json.dump(reminder, f)
                    # Show success message
                    messagebox.showinfo("Success", f"Reminder set for {date} at {datetime_str.split(' ')[1]}.")
                except sqlite3.Error as e:
                    print("Database error:", e)
                    messagebox.showerror("Error", "Failed to save reminder.")
                except Exception as e:
                    print("General error:", e)
                    messagebox.showerror("Error", "An error occurred while saving the reminder.")
                finally:
                    conn.close()  # Ensure the connection is closed

            def set_reminder():
                tenant_id = tenant_id_entry.get()
                tenant_username = fetch_tenant_username(tenant_id)
                if tenant_username is None:
                    messagebox.showwarning("Input Error", "Tenant ID not found.")
                    return
                # Get selected date and time
                selected_date = cal.get_date()
                formatted_date = datetime.strptime(selected_date, "%m/%d/%y").strftime("%Y-%m-%d")
                message = message_entry.get("1.0", END).strip()  # Retrieve the message from the entry

                # Call save_reminder with all required parameters
                current_time_str = datetime.now().strftime("%H:%M")
                save_reminder(tenant_id, tenant_username, f"{formatted_date} {current_time_str}", message,
                              formatted_date)

            def view_reminders():
                # Load reminders from the JSON file
                try:
                    with open("reminders.json", "r") as f:
                        reminders = json.load(f)
                    # Filter reminders from the last 30 days
                    current_time = datetime.now()
                    reminders_list = []
                    for reminder in reminders:
                        reminder_time = datetime.strptime(reminder["datetime"], "%Y-%m-%d %H:%M")
                        if (current_time - reminder_time).days <= 30:
                            reminders_list.append(
                                f"Reminder: {reminder['message']}\nScheduled for: {reminder['datetime']}")
                    if reminders_list:
                        messagebox.showinfo("Reminders in the Last 30 Days", "\n\n".join(reminders_list))
                    else:
                        messagebox.showinfo("No Recent Reminders", "No reminders found in the last 30 days.")
                except FileNotFoundError:
                    messagebox.showwarning("No Reminders Found", "No reminders have been set yet.")

            # Set Reminder Button
            send_button = Button(reminder_window, text="Send Reminder", command=set_reminder, font=label_font,
                                 background='#fd5602', activebackground='#fedebe')
            send_button.pack(pady=20)
            # View Reminders Button
            # view_button = Button(reminder_window, text="View Recently Sent Reminders", command=view_reminders, font=label_font, background='#002400', activebackground='#d4edda', fg='white')
            # view_button.pack(pady=10)
            # Ensure the entry starts in the correct state
            update_username_entry_state()

        upcoming_renewal()

    def show_label3():
        hide_all_labels()  # Hide all other labels
        label3.place(x=500, y=25)  # Show label3
        line3.place(x=500, y=label3.winfo_y() + 35, relwidth=0.7)  # Place line under label3
        renewal_agreement()  # Ensure this function is called
        print("Yes 3")

    def hide_all_labels():
        label1.place_forget()
        label2.place_forget()
        label3.place_forget()
        line1.place_forget()
        line2.place_forget()
        line3.place_forget()

    # Buttons for contract management
    request_button = Button(contract_frame, text="Pending Approval Request", font=("Arial", 16, 'bold'),
                            fg="#BBCF8D", bg='#002400', activebackground="white", width=30,
                            command=show_label1)
    request_button.place(x=25, y=25)
    upcoming_button = Button(contract_frame, text="Upcoming Renewals", font=("Arial", 16, 'bold'),
                             fg="#BBCF8D", bg='#002400', activebackground="white", width=30, command=show_label2)
    upcoming_button.place(x=25, y=75)

    renewal_agreement_button = Button(contract_frame, text="Renewal Agreement", font=("Arial", 16, 'bold'),
                                      fg="#BBCF8D", bg='#002400', activebackground="white", width=30,
                                      command=show_label3)
    renewal_agreement_button.place(x=25, y=125)
    # Labels for each section
    label1 = Label(contract_frame, text="Pending Approval Request", font=("Arial", 20, 'bold'), fg='black')
    label2 = Label(contract_frame, text="Upcoming Renewals", font=("Arial", 20, 'bold'), fg='black')
    label3 = Label(contract_frame, text="Renewal Agreement", font=("Arial", 20, 'bold'), fg='black')
    # Create lines under each label
    line1 = Canvas(contract_frame, height=2, bg='black')
    line2 = Canvas(contract_frame, height=2, bg='black')
    line3 = Canvas(contract_frame, height=2, bg='black')
    # Initially hide all labels and lines
    hide_all_labels()


def renewal_agreement():
    for widget in contract_frame.winfo_children():
        if isinstance(widget, Frame) and widget != contract_frame:
            widget.destroy()
        else:
            pass

    label_font = ("Arial", 12, 'bold')
    entry_font = ("Arial", 12)

    def fetch_tenant_username(event=None):
        tenant_id = tenant_id_entry.get()
        if not tenant_id:
            return
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Tenant_Username FROM Tenant WHERE Tenant_ID = ?", (tenant_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            tenant_username_entry.configure(state='normal')
            tenant_username_entry.delete(0, END)
            tenant_username_entry.insert(0, result[0])
            tenant_username_entry.configure(state='readonly')
        else:
            tenant_username_entry.configure(state='normal')
            tenant_username_entry.delete(0, END)
            tenant_username_entry.configure(state='readonly')

    renewal_agreement_frame2 = Frame(contract_frame, width=1350, height=800)
    renewal_agreement_frame2.place(x=500, y=100)

    # Agreement
    tenant_info_frame = Frame(renewal_agreement_frame2, bg='ivory2', width=600, height=800)
    tenant_info_frame.place(x=0, y=0)

    # Left side - Tenant ID
    Label(tenant_info_frame, text="Tenant ID:", font=label_font, anchor='w', bg='ivory2').grid(row=0, column=0, padx=5,
                                                                                               pady=5, sticky=W)
    tenant_id_entry = Entry(tenant_info_frame, width=15, font=entry_font)
    tenant_id_entry.grid(row=0, column=1, padx=5, pady=5)
    tenant_id_entry.bind("<FocusOut>", lambda event: (fetch_tenant_username(event), fetch_stall_id(event)))

    # Right side - Username
    Label(tenant_info_frame, text="Tenant Username:", font=label_font, anchor='w', bg='ivory2').grid(row=1, column=0,
                                                                                                     padx=5, pady=5,
                                                                                                     sticky=W)
    tenant_username_entry = Entry(tenant_info_frame, width=15, font=entry_font, state='readonly')
    tenant_username_entry.grid(row=1, column=1, padx=5, pady=5)

    def fetch_stall_id(event=None):
        tenant_id = tenant_id_entry.get()
        if not tenant_id:
            return
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Stall_ID FROM Tenant WHERE Tenant_ID = ?", (tenant_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            stall_id_entry.configure(state='normal')
            stall_id_entry.delete(0, END)
            stall_id_entry.insert(0, result[0])
            stall_id_entry.configure(state='readonly')
            fetch_rental_amounts(result[0])
        else:
            stall_id_entry.configure(state='normal')
            stall_id_entry.delete(0, END)
            stall_id_entry.configure(state='readonly')

    def fetch_rental_amounts(stall_id):
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Rental_Amount, Deposit_Amount, Total_Amount FROM Stall WHERE Stall_ID = ?", (stall_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            rental_amount, deposit_amount, total_amount = map(float, result)
            update_all_amounts(rental_amount, deposit_amount, total_amount)
        else:
            rental_amount_entry.configure(state='normal')
            rental_amount_entry.delete(0, END)
            rental_amount_entry.configure(state='readonly')
            deposit_entry.configure(state='normal')
            deposit_entry.delete(0, END)
            deposit_entry.configure(state='readonly')
            total_entry.configure(state='normal')
            total_entry.delete(0, END)
            total_entry.configure(state='readonly')

    # Stall ID
    Label(tenant_info_frame, text="Stall ID:", font=label_font, anchor='w', bg='ivory2').grid(row=2, column=0, padx=5,
                                                                                              pady=5, sticky=W)
    stall_id_entry = Entry(tenant_info_frame, width=15, font=entry_font, state='readonly')
    stall_id_entry.grid(row=2, column=1, padx=5, pady=5)

    # Add button to switch stall id

    # Rental period frame
    Label(tenant_info_frame, text="Rental Period:", font=label_font, anchor='w', bg='ivory2').grid(row=3, column=0,
                                                                                                   padx=5, pady=5,
                                                                                                   sticky=W)
    rental_period_combobox = ttk.Combobox(tenant_info_frame, values=["6 months", "1 year", "2 years"], width=30,
                                          font=entry_font)
    rental_period_combobox.grid(row=3, column=1, padx=5, pady=5)

    def update_contract_dates(event=None):
        from dateutil.relativedelta import relativedelta
        rental_period = rental_period_combobox.get()
        if rental_period:
            start_date = contract_start_entry.get_date()
            # Calculate months to add based on rental period
            if rental_period == "6 months":
                months = 6
            elif rental_period == "1 year":
                months = 12
            else:  # 2 years
                months = 24
            # Calculate end date by adding months to start date
            end_date = start_date + relativedelta(months=months)
            contract_end_entry.set_date(end_date)

    # Update end date when rental period changes
    rental_period_combobox.bind("<<ComboboxSelected>>", update_contract_dates)

    # Contract start date
    Label(tenant_info_frame, text="Contract Start Date:", font=label_font, anchor='w', bg='ivory2').grid(row=4,
                                                                                                         column=0,
                                                                                                         padx=5, pady=5,
                                                                                                         sticky=W)
    contract_start_entry = DateEntry(tenant_info_frame, width=27, background='navy', foreground='white', borderwidth=2,
                                     font=entry_font, date_pattern='yy-mm-dd')
    contract_start_entry.grid(row=4, column=1, padx=5, pady=5)

    # Update end date whenever start date or rental period changes
    def auto_update_dates(*args):
        if not rental_period_combobox.get():
            return
        from dateutil.relativedelta import relativedelta
        start_date = contract_start_entry.get_date()
        # Calculate months based on rental period
        rental_period = rental_period_combobox.get()
        if rental_period == "6 months":
            months = 6
        elif rental_period == "1 year":
            months = 12
        else:  # 2 years
            months = 24
        # Calculate and set end date
        end_date = start_date + relativedelta(months=months)
        contract_end_entry.set_date(end_date)

    # Bind auto update to both start date and rental period changes
    contract_start_entry.bind("<<DateEntrySelected>>", auto_update_dates)
    contract_start_entry.bind("<KeyRelease>", auto_update_dates)
    contract_start_entry.bind("<FocusOut>", auto_update_dates)
    rental_period_combobox.bind("<<ComboboxSelected>>", auto_update_dates)

    # Contract end date
    Label(tenant_info_frame, text="Contract End Date:", font=label_font, anchor='w', bg='ivory2').grid(row=5, column=0,
                                                                                                       padx=5, pady=5,
                                                                                                       sticky=W)
    contract_end_entry = DateEntry(tenant_info_frame, width=27, background='navy', foreground='white', borderwidth=2,
                                   font=entry_font, state='readonly', date_pattern='yy-mm-dd')  # Made end date readonly
    contract_end_entry.grid(row=5, column=1, padx=5, pady=5)

    # Rental amount
    Label(tenant_info_frame, text="Rental Amount (RM):", font=label_font, anchor='w', bg='ivory2').grid(row=6, column=0,
                                                                                                        padx=5, pady=5,
                                                                                                        sticky=W)
    rental_amount_entry = Entry(tenant_info_frame, width=30, font=entry_font, state='readonly')
    rental_amount_entry.grid(row=6, column=1, padx=5, pady=5)

    def update_rental():
        if update_rental_button["text"] == "Update Rental":
            rental_amount_entry.config(state='normal')
            update_rental_button.config(text="Save Changes")
        else:
            try:
                new_amount = float(rental_amount_entry.get())
                tenant_id = tenant_id_entry.get()
                if tenant_id:
                    conn = sqlite3.connect('govRental.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT Stall_ID FROM Tenant WHERE Tenant_ID = ?", (tenant_id,))
                    result = cursor.fetchone()
                    if result:
                        stall_id = result[0]
                        cursor.execute("UPDATE Stall SET Rental_Amount = ? WHERE Stall_ID = ?", (new_amount, stall_id))
                        conn.commit()
                        messagebox.showinfo("Success", "Rental amount updated successfully!")
                        rental_amount_entry.config(state='readonly')
                        update_rental_button.config(text="Update Rental")
                        # Update deposit and total amounts
                        update_all_amounts(new_amount)
                    conn.close()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number for rental amount")
                rental_amount_entry.delete(0, END)
                rental_amount_entry.focus()

    update_rental_button = Button(tenant_info_frame, text="Update Rental", font=('Arial', 10, 'bold'),
                                  activebackground='#fd5602', command=update_rental)
    update_rental_button.grid(row=6, column=2, padx=5, pady=5)

    def update_all_amounts(rental_amount, deposit_amount=None, total_amount=None):
        def update_entry(entry, value):
            entry.config(state='normal')
            entry.delete(0, END)
            entry.insert(0, str(value))
            entry.config(state='readonly')

        # Update rental amount
        update_entry(rental_amount_entry, rental_amount)

        # Update deposit amount (1.5 times rental if not provided)
        if deposit_amount is None:
            deposit_amount = rental_amount * 1.5
        update_entry(deposit_entry, deposit_amount)

        # Update total amount (rental + deposit if not provided)
        if total_amount is None:
            total_amount = rental_amount + deposit_amount
        update_entry(total_entry, total_amount)

        # Save total amount to database
        tenant_id = tenant_id_entry.get()
        if tenant_id:
            with sqlite3.connect('govRental.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Stall_ID FROM Tenant WHERE Tenant_ID = ?", (tenant_id,))
                result = cursor.fetchone()
                if result:
                    stall_id = result[0]
                    cursor.execute("UPDATE Stall SET Total_Amount = ? WHERE Stall_ID = ?", (total_amount, stall_id))
                    conn.commit()

    # Fetch rental amount when stall is selected
    def update_rental_amount(event=None):
        tenant_id = tenant_id_entry.get()
        if tenant_id:
            with sqlite3.connect('govRental.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Stall_ID FROM Tenant WHERE Tenant_ID = ?", (tenant_id,))
                result = cursor.fetchone()
                if result:
                    stall_id = result[0]
                    cursor.execute("SELECT Rental_Amount, Deposit_Amount, Total_Amount FROM Stall WHERE Stall_ID = ?",
                                   (stall_id,))
                    result = cursor.fetchone()
                    if result:
                        rental_amount, deposit_amount, total_amount = map(float, result)
                        update_all_amounts(rental_amount, deposit_amount, total_amount)

    # Deposit amount
    Label(tenant_info_frame, text="Deposit Amount (RM):", font=label_font, anchor='w', bg='ivory2').grid(row=7,
                                                                                                         column=0,
                                                                                                         padx=5, pady=5,
                                                                                                         sticky=W)
    deposit_entry = Entry(tenant_info_frame, width=30, font=entry_font, state='readonly')
    deposit_entry.grid(row=7, column=1, padx=5, pady=5)

    # Total amount
    Label(tenant_info_frame, text="Total Amount (RM):", font=label_font, anchor='w', bg='ivory2').grid(row=8, column=0,
                                                                                                       padx=5, pady=5,
                                                                                                       sticky=W)
    total_entry = Entry(tenant_info_frame, width=30, font=entry_font, state='readonly')
    total_entry.grid(row=8, column=1, padx=5, pady=5)

    # Payment date frame
    payment_date_frame = Frame(tenant_info_frame, bg='ivory2')
    payment_date_frame.grid(row=9, column=0, columnspan=2, pady=20)

    # Payment by date
    payment_date_inner_frame = Frame(payment_date_frame, bg='ivory2')
    payment_date_inner_frame.pack(fill=X)

    # Payment due date
    Label(payment_date_inner_frame, text="Payment due by:", font=label_font, anchor='w', bg='ivory2').pack(side=LEFT,
                                                                                                           padx=5)
    last_payment_entry = DateEntry(payment_date_inner_frame, width=27, background='darkblue', foreground='white',
                                   borderwidth=2, font=entry_font, calendar_position='above', mindate=datetime.now(),
                                   date_pattern='yy-mm-dd')
    last_payment_entry.pack(side=LEFT)

    # Reminder date
    Label(payment_date_inner_frame, text="Send reminder on:", font=label_font, anchor='w', bg='ivory2').pack(side=LEFT,
                                                                                                             padx=5)
    reminder_entry = DateEntry(payment_date_inner_frame, width=27, background='darkblue', foreground='white',
                               borderwidth=2, font=entry_font, calendar_position='above', mindate=datetime.now(),
                               date_pattern='yy-mm-dd')  # Set date format to yyyy-mm-dd
    reminder_entry.pack(side=LEFT)

    # Update payment due date when contract start date changes
    def update_payment_due_date(*args):
        start_date = contract_start_entry.get_date()
        # Set payment due date to 7 days after the start date
        payment_due_date = start_date + timedelta(days=7)
        # Update the last payment entry with the calculated payment due date
        last_payment_entry.set_date(payment_due_date)
        # Update reminder date whenever payment due date changes
        reminder_date = payment_due_date - timedelta(days=3)
        reminder_entry.set_date(reminder_date)
        reminder_entry.config(state='readonly')

    contract_start_entry.bind('<<DateEntrySelected>>', update_payment_due_date)

    # Update reminder date when payment due date changes
    def update_reminder_date(*args):
        payment_due = last_payment_entry.get_date()
        reminder_date = payment_due - timedelta(days=3)
        reminder_entry.set_date(reminder_date)
        reminder_entry.config(state='readonly')

    # Bind to both DateEntrySelected and when payment due date is updated
    last_payment_entry.bind('<<DateEntrySelected>>', update_reminder_date)

    # Initial updates
    update_payment_due_date()  # This will also update the reminder date

    # Button to open the preview agreement window
    separator_label = Label(tenant_info_frame,
                            text="----------------------------------------------------------------------------------------------------------------------------------------------"
                                 "----------------------------------------------------------------------------------------------------",
                            font=label_font, bg='ivory2')
    separator_label.grid(row=11, column=0, columnspan=2, pady=10)

    def generate_agreement():
        if not all([stall_id_entry.get(), tenant_id_entry.get(), tenant_username_entry.get(),
                    rental_period_combobox.get(), rental_amount_entry.get(), deposit_entry.get()]):
            messagebox.showerror("Error", "Please fill in all required fields before generating agreement")
            return
        stall_id = stall_id_entry.get()
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Stall_Address FROM Stall WHERE Stall_ID = ?", (stall_id,))
        stall_address = cursor.fetchone()[0]
        conn.close()
        tenant_id = tenant_id_entry.get()
        tenant_username = tenant_username_entry.get()
        rental_period = rental_period_combobox.get()
        start_date = contract_start_entry.get_date()
        end_date = contract_end_entry.get_date()
        rental_amount = rental_amount_entry.get()
        deposit = deposit_entry.get()
        preview_window = Toplevel()
        preview_window.title("Agreement Preview")
        preview_window.geometry("600x800")
        preview_frame = Frame(preview_window)
        preview_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        preview_text = Text(preview_frame, wrap=WORD, font=("Helvetica", 12))
        preview_text.pack(fill=BOTH, expand=True)
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Tenant_IC_Number FROM Tenant WHERE Tenant_Username = ?", (tenant_username,))
        tenant_ic = cursor.fetchone()[0]
        conn.close()
        preview_text.insert(END, "RENTAL AGREEMENT\n\n", "title")
        preview_text.insert(END, f"Tenant Name: {tenant_username}\n")
        preview_text.insert(END, f"Tenant IC: {tenant_ic}\n")
        preview_text.insert(END, f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n")
        preview_text.insert(END, f"Stall ID: {stall_id}\n")
        preview_text.insert(END, f"Stall Address: {stall_address}\n")
        preview_text.insert(END, f"Tenant ID: {tenant_id}\n")
        preview_text.insert(END, f"Tenant Name: {tenant_username}\n")
        preview_text.insert(END, f"Rental Period: {rental_period}\n")
        preview_text.insert(END, f"Contract Start Date: {start_date}\n")
        preview_text.insert(END, f"Contract End Date: {end_date}\n")
        preview_text.insert(END, f"Monthly Rental Amount: RM {rental_amount}\n")
        preview_text.insert(END, f"Security Deposit: RM {deposit}\n")
        preview_text.insert(END, f"Total Amount: RM {total_entry.get()}\n")
        preview_text.tag_configure("bold_red", font=("Helvetica", 12, "bold"), foreground="red")
        preview_text.insert(END, f"\n\nPlease paid by: {last_payment_entry.get_date()}\n\n", "bold_red")
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Admin_ID, Admin_Name FROM Admin WHERE Admin_IC_Number = ?", (admin_ic,))
        admin = cursor.fetchone()
        conn.close()
        if admin:
            preview_text.insert(END, f"Admin ID: {admin[0]} | Admin Name: {admin[1]} \n")
        else:
            preview_text.insert(END, "Admin information not found\n")
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Business_Name, Licence_No, Business_Hours, Location, Contact_No, Email_Address FROM Business_Information")
        business_info = cursor.fetchone()
        conn.close()
        if business_info:
            preview_text.insert(END, f"{business_info[0]}\n")
            preview_text.insert(END, f"License No: {business_info[1]}\n")
            preview_text.insert(END, f"{business_info[2]}\n")
            preview_text.insert(END, f"{business_info[3]}\n")
            preview_text.insert(END, f"Contact No: {business_info[4]}, Email: {business_info[5]}\n")
        preview_text.tag_configure("title", font=("Helvetica", 16, "bold"))
        preview_text.config(state=DISABLED)

    preview_button = Button(tenant_info_frame, text="Preview Agreement", font=label_font, fg='misty rose', bg='#fd5602',
                            command=generate_agreement)
    preview_button.grid(row=12, column=0, columnspan=2, pady=10)


# Fetch tenant data from the SQLite database
def fetch_tenant_data():
    conn = sqlite3.connect('govRental.db')
    cursor = conn.cursor()
    # Ensure the SQL query selects the correct columns in the correct order
    cursor.execute("""
        SELECT 
            Request_ID, 
            Stall_ID, 
            Postcode, 
            Tenant_ID, 
            Tenant_Username, 
            Tenant_Phone_Number, 
            Status, 
            Payment_History, 
            Stall_Management, 
            Contract_Violation, 
            Contract_End_Date 
        FROM PendingApprovalRequest
    """)
    data = cursor.fetchall()
    conn.close()
    return data


def create_tenant_stall_frame():
    # Create a new frame to hold the tenant and stall management UI
    tenant_and_stall_frame = Frame(main_frame)
    tenant_and_stall_frame.place(relwidth=1, relheight=1)
    # Call the function to add tenant and stall management UI to the frame
    add_stall_and_assign_stall(tenant_and_stall_frame)


def add_stall_and_assign_stall(tenant_and_stall):
    global contract_start_date, contract_end_date

    def fetch_tenant_username(event=None):
        tenant_id = tenant_id_entry.get()
        if not tenant_id:
            return
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Tenant_Username FROM Tenant WHERE Tenant_ID = ?", (tenant_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            tk.tenant_username_entry.configure(state='normal')
            tk.tenant_username_entry.delete(0, END)
            tk.tenant_username_entry.insert(0, result[0])
            tk.tenant_username_entry.configure(state='readonly')
        else:
            tk.tenant_username_entry.configure(state='normal')
            tk.tenant_username_entry.delete(0, END)
            tk.tenant_username_entry.configure(state='readonly')

    def add_stall():
        stall_address = tk.address_entry.get("1.0", "end-1c")
        postcode = postcode_entry.get()
        rental_amount = tk.stall_rental_entry.get()
        if not stall_address or not postcode or not rental_amount:
            messagebox.showerror("Error", "All fields are required!")
            return
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Stall (Stall_Address, Postcode, Stall_Status, Rental_Amount) VALUES (?, ?, 0, ?)",
            (stall_address, postcode, rental_amount))
        stall_id = cursor.lastrowid
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Stall added successfully! Stall ID: {stall_id}")
        tk.address_entry.delete("1.0", "end-1c")
        postcode_entry.delete(0, END)
        tk.stall_rental_entry.delete(0, END)

    def search_stalls_by_postcode():
        postcode = tk.search_postcode_entry.get()
        if not postcode:
            print(postcode)
            messagebox.showerror("Error", "Please enter a postcode to search!")
            return
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Stall_ID, Stall_Address FROM Stall WHERE Postcode = ? AND Status = 0",
                       (postcode,))
        stalls = cursor.fetchall()
        conn.close()
        tk.stall_combobox['values'] = []
        if stalls:
            tk.stall_combobox['values'] = [f"ID: {stall[0]}, Address: {stall[1]}" for stall in stalls]
            messagebox.showinfo("Updates", "Available stalls already shown in the dropbox.")
        else:
            messagebox.showinfo("No Results", "No available stalls found for the given postcode.")

    from datetime import timedelta
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta
    def assign_stall():
        selected_stall = tk.stall_combobox.get()
        if not selected_stall:
            messagebox.showerror("Error", "Please select a stall to assign.")
            return
        stall_id = selected_stall.split(",")[0].split(":")[1].strip()
        stall_address = selected_stall.split(",")[1].split(":")[1].strip()
        # Get all form values
        tenant_id = tenant_id_entry.get()
        tenant_username = tk.tenant_username_entry.get()
        rental_period = tk.rental_period_combobox.get()
        rental_amount = tk.rental_amount_entry.get()
        deposit_amount = tk.deposit_entry.get()
        # Convert date string to proper format (YY-MM-DD)
        try:
            payment_date = datetime.strptime(tk.last_payment_entry.get(), '%y-%m-%d')
            last_payment_date = payment_date.strftime('%y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YY-MM-DD format")
            return
        # Parse rental period correctly
        rental_period = tk.rental_period_combobox.get()
        if rental_period == "6 months":
            rental_months = 6
        elif rental_period == "1 year":
            rental_months = 12
        elif rental_period == "2 years":
            rental_months = 24
        else:
            messagebox.showerror("Error", "Invalid rental period selected")
            return
        # Contract start and end dates
        contract_start_date = tk.contract_start_entry.get_date()
        # Calculate contract end date based on rental period
        contract_end_date = contract_start_date + relativedelta(months=rental_months)
        contract_end_date_str = contract_end_date.strftime('%Y-%m-%d')
        tk.contract_end_entry.delete(0, 'end')  # Clear any previous value
        tk.contract_end_entry.insert(0, contract_end_date_str)  # Insert the calculated end date
        tk.contract_end_entry.configure(state='readonly')  # Set to read-only after insertion
        # Reminder date
        reminder_date = tk.reminder_entry.get_date().strftime('%Y-%m-%d')
        tk.reminder_entry.delete(0, 'end')  # Clear any previous value
        tk.reminder_entry.insert(0, reminder_date)  # Insert the reminder date
        tk.reminder_entry.configure(state='readonly')  # Set to read-only after insertion
        # Payment due date (example: set as the contract start date here)
        payment_due_date_str = contract_start_date.strftime('%Y-%m-%d')
        try:
            tk.last_payment_entry.configure(state='normal')  # Set to normal before modification
            tk.last_payment_entry.delete(0, 'end')  # Clear any previous value
            tk.last_payment_entry.insert(0, payment_due_date_str)  # Insert the payment due date
            tk.last_payment_entry.configure(state='readonly')  # Set back to readonly
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set payment due date: {str(e)}")
            return
        # Validate required fields
        if not all([tenant_id, tenant_username, rental_period, rental_amount, deposit_amount, last_payment_date]):
            messagebox.showerror("Error", "All fields are required!")
            return
        # Validate numeric inputs
        try:
            rental_amount_float = float(rental_amount)
            deposit_amount_float = float(deposit_amount)
        except ValueError:
            messagebox.showerror("Error", "Rental amount and deposit amount must be valid numbers.")
            return
        try:
            conn = sqlite3.connect('govRental.db')
            cursor = conn.cursor()
            # Get full stall address from Stall table first
            cursor.execute('''SELECT Stall_Address FROM Stall WHERE Stall_ID = ?''', (stall_id,))
            stall_address = cursor.fetchone()[0]
            # Update Stall table
            cursor.execute('''UPDATE Stall 
                            SET Stall_Status = ?,
                                Tenant_ID = ?,
                                Tenant_Username = ?, 
                                Rental_Period = ?,
                                Contract_Start_Date = ?,
                                Contract_End_Date = ?,
                                Rental_Amount = ?,
                                Deposit_Amount = ?,
                                Payment_Due = ?,
                                Contract_Status = ?,
                                Renewal_Status = ?,
                                Reminder_Date = ?
                            WHERE Stall_ID = ?''',
                           (1, tenant_id, tenant_username, rental_period,
                            contract_start_date.strftime('%Y-%m-%d'),
                            contract_end_date_str,
                            rental_amount_float, deposit_amount_float,
                            last_payment_date, 'Active', 0,
                            reminder_date, stall_id))
            if cursor.rowcount == 0:
                raise Exception("No rows were updated in the database.")
            cursor.execute("SELECT Postcode FROM Stall WHERE Stall_ID = ?", (stall_id,))
            postcode = cursor.fetchone()[0]
            # Get the last payment ID
            cursor.execute("SELECT MAX(CAST(SUBSTR(Payment_ID, 4) AS INTEGER)) FROM Payment_Manage")
            last_id = cursor.fetchone()[0]
            next_id = 1 if last_id is None else last_id + 1
            # Insert payment records for each month of the rental period
            for month in range(rental_months):  # This will now correctly iterate for all months
                payment_id = f"PMT{str(next_id).zfill(5)}"
                # Calculate payment due date for each month
                payment_due_date = contract_start_date + relativedelta(months=month, day=8)
                reminder_date_for_month = payment_due_date - relativedelta(days=7)
                try:
                    # Calculate the rental amount for each month
                    monthly_rental_amount = rental_amount_float
                    cursor.execute('''INSERT INTO Payment_Manage (
                        Payment_ID, Payment_Due, Tenant_ID, Tenant_Username, Stall_ID, 
                        Postcode, Rental_Amount, Status, Due_Date, Overdue_Status,
                        Overdue_Amount, Total_Amount, Reminder_Date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                   (payment_id,
                                    payment_due_date.strftime('%Y-%m-%d'),
                                    tenant_id,
                                    tenant_username,
                                    stall_id,
                                    postcode,
                                    monthly_rental_amount,
                                    'Pending',
                                    payment_due_date.strftime('%Y-%m-%d'),
                                    'No',
                                    0,
                                    monthly_rental_amount,
                                    reminder_date_for_month.strftime('%Y-%m-%d')))
                    next_id += 1  # Increment next_id after successful insert
                except sqlite3.IntegrityError as e:
                    if "UNIQUE constraint failed: Payment_Manage.Payment_ID" in str(e):
                        print(f"Duplicate payment_id found: {payment_id}. Incrementing ID and retrying.")
                        next_id += 1  # Increment next_id and retry
                    else:
                        raise
            # Update Tenant table with Stall_ID and Stall_Address
            cursor.execute('''UPDATE Tenant 
                            SET Stall_ID = ?, 
                                Stall_Address = ?
                            WHERE Tenant_ID = ?''',
                           (stall_id, stall_address, tenant_id))
            conn.commit()
            messagebox.showinfo("Success", "Stall assigned to tenant successfully!")
            clear_form()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to assign stall: {str(e)}")
        finally:
            conn.close()

    def update_deposit_amount(event=None):
        try:
            rental_amount = float(tk.rental_amount_entry.get())
            deposit_amount = rental_amount * 1.5  # ori is 2
            tk.deposit_entry.delete(0, END)
            tk.deposit_entry.insert(0, f"{deposit_amount:.2f}")
            tk.deposit_entry.configure(state='readonly')
        except ValueError:
            tk.deposit_entry.delete(0, END)

    def clear_form():
        tenant_id_entry.delete(0, END)
        tk.tenant_username_entry.configure(state='normal')
        tk.tenant_username_entry.delete(0, END)
        tk.tenant_username_entry.configure(state='readonly')
        tk.rental_period_combobox.set("")
        tk.rental_amount_entry.configure(state='normal')
        tk.rental_amount_entry.delete(0, END)
        tk.rental_amount_entry.configure(state='readonly')
        tk.deposit_entry.configure(state='normal')
        tk.deposit_entry.delete(0, END)
        tk.deposit_entry.configure(state='readonly')
        tk.reminder_entry.configure(state='normal')
        tk.reminder_entry.delete(0, END)
        tk.reminder_entry.configure(state='readonly')
        tk.last_payment_entry.set_date(datetime.now().date())
        tk.stall_combobox.set("")

    def add_tenant():
        # Get values from entries
        tenant_ic = tk.tenant_ic_entry.get().strip()
        tenant_username = tk.tenant_username_entry.get().strip()
        temp_password = tk.pass_entry.get()
        # Validate inputs
        if not tenant_ic or not tenant_username:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        try:
            # Connect to database
            conn = sqlite3.connect('govRental.db')
            cursor = conn.cursor()
            # Check if IC already exists
            cursor.execute("SELECT * FROM Tenant WHERE Tenant_IC_Number=?", (tenant_ic,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Tenant with this IC already exists")
                tk.tenant_ic_entry.delete(0, END)
                tk.tenant_username_entry.delete(0, END)
                return
            # Generate username from IC number (last 6 digits)
            username = tenant_username
            # Insert new tenant
            cursor.execute("""
                INSERT INTO Tenant (
                    Tenant_IC_Number,
                    Tenant_Username, 
                    Tenant_Password
                ) VALUES (?, ?, ?)
            """, (tenant_ic, tenant_username, temp_password))
            conn.commit()
            messagebox.showinfo("Success", f"Tenant added successfully!\nUsername: {username}")
            tk.tenant_ic_entry.delete(0, END)
            tk.tenant_username_entry.delete(0, END)
            # Clear entries
            tk.tenant_ic_entry.delete(0, END)
            tk.tenant_username_entry.delete(0, END)
            tk.pass_entry.configure(state='normal')
            tk.pass_entry.delete(0, END)
            tk.pass_entry.insert(0, "Pass1234")
            tk.pass_entry.configure(state='readonly')
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
        finally:
            conn.close()
        label_font = ('Arial', 14, 'bold')
        entry_font = ('Arial', 14)
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Arial', 15, 'bold'), padding=[20, 10], width=200)
        style.configure('TNotebook', tabposition='n')
        style.map('TNotebook.Tab', foreground=[("selected", "#fd5602")])
        # Notebook widget
        notebook = ttk.Notebook(tenant_and_stall)
        notebook.pack(fill='both', expand=True)  # Use pack instead of place to properly expand
        # Frame for Add Stall tab
        add_stall_frame = Frame(notebook, width=1200, height=1000, bg='mint cream')
        add_stall_frame.pack(fill='both', expand=True)
        add_stall_frame.pack_propagate(False)
        # Frame for Assign Stall tab
        assign_stall_frame = Frame(notebook, width=1200, height=1000, bg='LavenderBlush2')
        assign_stall_frame.pack(fill='both', expand=True)
        assign_stall_frame.pack_propagate(False)
        tenant_register_frame = Frame(notebook, width=1200, height=1000, bg='ivory2')
        tenant_register_frame.pack(fill='both', expand=True)
        tenant_register_frame.pack_propagate(False)
        notebook.add(add_stall_frame, text="  Add New Stall  ")
        notebook.add(assign_stall_frame, text="  Assign Stall to Tenant  ")
        notebook.add(tenant_register_frame, text="  Register a New Tenant  ")
        # Add Stall Tab
        # Center all elements using a main container frame
        container_frame = Frame(add_stall_frame, width=1200, height=1000, bg='mint cream')
        container_frame.pack(fill='both', expand=True)
        container_frame.pack_propagate(False)
        # Add Stall Tab
        stall_frame = Frame(container_frame, bg='mint cream')
        stall_frame.pack(pady=(80, 0))
        Label(stall_frame, text="Stall Address:", font=label_font, anchor='w', bg='mint cream').pack(side=LEFT, padx=5)
        address_entry = ctk.CTkTextbox(stall_frame, width=400, height=100, font=entry_font, wrap=WORD, border_width=2,
                                       border_color='black')
        address_entry.pack(side=LEFT)
        postcode_frame = Frame(container_frame, bg='mint cream')
        postcode_frame.pack(pady=20)
        Label(postcode_frame, text="Postcode:", font=label_font, anchor='w', bg='mint cream').pack(side=LEFT, padx=5)
        postcode_entry = ctk.CTkEntry(postcode_frame, width=200, font=entry_font)
        postcode_entry.pack(side=LEFT)
        coordinates_frame = Frame(container_frame, bg='mint cream')
        coordinates_frame.pack(pady=20)
        Label(coordinates_frame, text="Latitude:", font=label_font, anchor='w', bg='mint cream').pack(side=LEFT, padx=5)
        latitude_entry = ctk.CTkEntry(coordinates_frame, width=150, font=entry_font)
        latitude_entry.pack(side=LEFT, padx=(0, 20))
        Label(coordinates_frame, text="Longitude:", font=label_font, anchor='w', bg='mint cream').pack(side=LEFT,
                                                                                                       padx=5)
        longitude_entry = ctk.CTkEntry(coordinates_frame, width=150, font=entry_font)
        longitude_entry.pack(side=LEFT)
        # Image upload frame
        image_frame = Frame(container_frame, bg='mint cream')
        image_frame.pack(pady=20)
        Label(image_frame, text="Stall Image:", font=label_font, anchor='w', bg='mint cream').pack(padx=5)

        def upload_image():
            from tkinter import filedialog
            # Get image file
            file_path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
            )
            if (file_path):
                try:
                    # Open and resize image
                    image = Image.open(file_path)
                    image = image.resize((300, 300), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    # Update image label
                    image_label.config(image=photo)
                    image_label.image = photo  # Keep a reference
                    # Store file path
                    image_frame.file_path = file_path
                    # Change button text
                    upload_button.config(text="Reupload Image")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to upload image: {str(e)}")

        upload_button = ctk.CTkButton(image_frame, text="Upload Image", command=upload_image,
                                      font=('Arial', 10, 'bold'),
                                      fg_color='#fd5602', hover_color='white')
        upload_button.pack(padx=5, pady=10)
        # Create vertical container for image label
        image_container = Frame(image_frame, bg='mint cream')
        image_container.pack(padx=10, pady=10)
        # Label to display the image
        image_label = Label(image_container, bg='mint cream')
        image_label.pack()
        stall_rental_frame = Frame(container_frame, bg='mint cream')
        stall_rental_frame.pack(pady=20)
        Label(stall_rental_frame, text="Stall Rental (RM):", font=label_font, anchor='w', bg='mint cream').pack(
            side=LEFT,
            padx=5)
        stall_rental_entry = ctk.CTkEntry(stall_rental_frame, width=200, font=entry_font)
        stall_rental_entry.pack(side=LEFT)

        def add_stall():
            # Get values from entry fields
            stall_address = address_entry.get("1.0", "end-1c")  # For Text widget
            stall_postcode = postcode_entry.get().strip()
            # Validate postcode format
            if not stall_postcode.isdigit() or len(stall_postcode) != 5:
                messagebox.showerror("Error", "Postcode must be exactly 5 digits")
                return
            # Check if postcode appears in address
            if stall_postcode not in stall_address:
                messagebox.showerror("Error", "Postcode must match the one in stall address")
                return
            stall_rental = stall_rental_entry.get()
            stall_latitude = latitude_entry.get()
            stall_longitude = longitude_entry.get()
            # Validate all fields are filled
            if not all([stall_address, stall_postcode, stall_rental, stall_latitude, stall_longitude]):
                messagebox.showerror("Error", "Please fill in all fields")
                return
            # Validate if image was uploaded
            if not hasattr(image_frame, 'file_path'):
                messagebox.showerror("Error", "Please upload an image")
                return
            try:
                # Connect to database
                conn = sqlite3.connect('govRental.db')
                cursor = conn.cursor()
                # Insert new stall record with all details including latitude and longitude
                cursor.execute("""
                    INSERT INTO Stall (Stall_Address, Postcode, Address_Image, Rental_Amount, Latitude, Longitude, Stall_Status)
                    VALUES (?, ?, ?, ?, ?, ?, 0)
                """, (
                stall_address, stall_postcode, image_frame.file_path, stall_rental, stall_latitude, stall_longitude))
                conn.commit()
                cursor.execute("SELECT last_insert_rowid()")
                stall_id = cursor.fetchone()[0]
                messagebox.showinfo("Success", f"Stall details saved successfully! Stall ID: {stall_id}")
                # Clear entry fields
                address_entry.delete("1.0", "end-1c")  # For Text widget
                postcode_entry.delete(0, END)
                stall_rental_entry.delete(0, END)
                latitude_entry.delete(0, END)
                longitude_entry.delete(0, END)
                image_label.config(image='')
                upload_button.config(text="Upload Image")
                delattr(image_frame, 'file_path')
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to save stall details: {str(e)}")
            finally:
                conn.close()

        add_button = Button(container_frame, text="Add Stall", command=add_stall, font=('Arial', 12, 'bold'),
                            fg='white',
                            bg='#fd5602', activebackground='white', width=20)
        add_button.pack(pady=20)
        # Assign Stall Tab - Center elements
        assign_container = Frame(assign_stall_frame, width=1200, height=1000, bg='LavenderBlush2')
        assign_container.pack(fill='both', expand=True)
        assign_container.pack_propagate(False)
        search_frame = Frame(assign_container, bg='LavenderBlush2')
        search_frame.pack(pady=(50, 0))
        Label(search_frame, text="Search by Postcode:", font=label_font, anchor='w', bg='LavenderBlush2').pack(
            side=LEFT,
            padx=5)
        search_postcode_entry = Entry(search_frame, width=30, font=entry_font)
        search_postcode_entry.pack(side=LEFT)
        search_button = Button(search_frame, text="Search", command=search_stalls_by_postcode,
                               activebackground='#fd5602',
                               font=('Arial', 10, 'bold'))
        search_button.pack(side=LEFT, padx=5)
        stall_frame = Frame(assign_container, bg='LavenderBlush2')
        stall_frame.pack(pady=20)
        Label(stall_frame, text="Available Stalls:", font=label_font, anchor='w', bg='LavenderBlush2').pack(side=LEFT,
                                                                                                            padx=5)
        stall_combobox = ttk.Combobox(stall_frame, width=40, font=entry_font)
        stall_combobox.pack(side=LEFT)

        def view_stall_image():
            selected_stall = stall_combobox.get()
            if not selected_stall:
                messagebox.showerror("Error", "Please select a stall first.")
                return
            stall_id = selected_stall.split(",")[0].split(":")[1].strip()
            conn = sqlite3.connect('govRental.db')
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT Address_Image FROM Stall WHERE Stall_ID = ?", (stall_id,))
                result = cursor.fetchone()
                if result and result[0]:
                    image_path = result[0]
                    try:
                        img = Image.open(image_path)
                        img.show()
                    except FileNotFoundError:
                        messagebox.showerror("Error", "Image file not found.")
                else:
                    messagebox.showinfo("No Image", "No image available for this stall.")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to retrieve image: {str(e)}")
            finally:
                conn.close()

        view_image_btn = Button(stall_frame, text="View Stall Image",
                                command=view_stall_image,
                                font=('Arial', 10, 'bold'), bg='#fd5602', fg='white')
        view_image_btn.pack(side=LEFT, padx=5)

        def enable_view_button(*args):
            if stall_combobox.get():
                view_image_btn.config(state='normal')
            else:
                view_image_btn.config(state='disabled')

        stall_combobox.bind('<<ComboboxSelected>>', enable_view_button)
        stall_combobox.bind('<KeyRelease>', enable_view_button)
        # Create a container frame for tenant ID and username
        tenant_info_frame = Frame(assign_container, bg='LavenderBlush2')
        tenant_info_frame.pack(pady=20)
        # Left side - Tenant ID
        tenant_id_frame = Frame(tenant_info_frame, bg='LavenderBlush2')
        tenant_id_frame.pack(side=LEFT, padx=20)
        Label(tenant_id_frame, text="Tenant ID:", font=label_font, anchor='w', bg='LavenderBlush2').pack(side=LEFT,
                                                                                                         padx=5)
        tenant_id_entry = Entry(tenant_id_frame, width=15, font=entry_font)
        tenant_id_entry.pack(side=LEFT)
        tenant_id_entry.bind("<FocusOut>", fetch_tenant_username)
        # Right side - Username
        username_frame = Frame(tenant_info_frame, bg='LavenderBlush2')
        username_frame.pack(side=LEFT, padx=20)
        Label(username_frame, text="Tenant Username:", font=label_font, anchor='w', bg='LavenderBlush2').pack(side=LEFT,
                                                                                                              padx=5)
        tenant_username_entry = Entry(username_frame, width=15, font=entry_font, state='readonly')
        tenant_username_entry.pack(side=LEFT)
        # Rental period frame
        rental_period_frame = Frame(assign_container, bg='LavenderBlush2')
        rental_period_frame.pack(pady=20)
        Label(rental_period_frame, text="Rental Period:", font=label_font, anchor='w', bg='LavenderBlush2').pack(
            side=LEFT,
            padx=5)
        rental_period_combobox = ttk.Combobox(rental_period_frame, values=["6 months", "1 year", "2 years"],
                                              width=30, font=entry_font)
        rental_period_combobox.pack(side=LEFT)

        def update_contract_dates(event=None):
            from dateutil.relativedelta import relativedelta
            rental_period = rental_period_combobox.get()
            if rental_period:
                start_date = contract_start_entry.get_date()
                # Calculate months to add based on rental period
                if rental_period == "6 months":
                    months = 6
                elif rental_period == "1 year":
                    months = 12
                else:  # 2 years
                    months = 24
                # Calculate end date by adding months to start date
                end_date = start_date + relativedelta(months=months)
                contract_end_entry.set_date(end_date)

        # Update end date when rental period changes
        rental_period_combobox.bind("<<ComboboxSelected>>", update_contract_dates)
        start_date_frame = Frame(assign_container, bg='LavenderBlush2')
        start_date_frame.pack(pady=20)
        Label(start_date_frame, text="Contract Start Date:", font=label_font, anchor='w', bg='LavenderBlush2').pack(
            side=LEFT, padx=5)
        contract_start_entry = DateEntry(start_date_frame, width=27, background='navy', foreground='white',
                                         borderwidth=2,
                                         font=entry_font, date_pattern='yy-mm-dd')
        contract_start_entry.pack(side=LEFT)

        # Update end date whenever start date or rental period changes
        def auto_update_dates(*args):
            if not rental_period_combobox.get():
                return
            from dateutil.relativedelta import relativedelta
            start_date = contract_start_entry.get_date()
            # Calculate months based on rental period
            rental_period = rental_period_combobox.get()
            if rental_period == "6 months":
                months = 6
            elif rental_period == "1 year":
                months = 12
            else:  # 2 years
                months = 24
            # Calculate and set end date
            end_date = start_date + relativedelta(months=months)
            contract_end_entry.set_date(end_date)

        # Bind auto update to both start date and rental period changes
        contract_start_entry.bind("<<DateEntrySelected>>", auto_update_dates)
        contract_start_entry.bind("<KeyRelease>", auto_update_dates)
        contract_start_entry.bind("<FocusOut>", auto_update_dates)
        rental_period_combobox.bind("<<ComboboxSelected>>", auto_update_dates)
        end_date_frame = Frame(assign_container, bg='LavenderBlush2')
        end_date_frame.pack(pady=20)
        Label(end_date_frame, text="Contract End Date:", font=label_font, anchor='w', bg='LavenderBlush2').pack(
            side=LEFT,
            padx=5)
        contract_end_entry = DateEntry(end_date_frame, width=27, background='navy', foreground='white', borderwidth=2,
                                       font=entry_font, state='readonly',
                                       date_pattern='yy-mm-dd')  # Made end date readonly
        contract_end_entry.pack(side=LEFT)
        rental_amount_frame = Frame(assign_container, bg='LavenderBlush2')
        rental_amount_frame.pack(pady=20)
        Label(rental_amount_frame, text="Rental Amount (RM):", font=label_font, anchor='w', bg='LavenderBlush2').pack(
            side=LEFT, padx=5)
        rental_amount_entry = Entry(rental_amount_frame, width=30, font=entry_font, state='readonly')
        rental_amount_entry.pack(side=LEFT)

        def update_rental():
            if update_rental_button["text"] == "Update Rental":
                rental_amount_entry.config(state='normal')
                update_rental_button.config(text="Save Changes")
            else:
                try:
                    new_amount = float(rental_amount_entry.get())
                    selected_stall = stall_combobox.get()
                    if selected_stall:
                        stall_id = selected_stall.split(",")[0].split(":")[1].strip()
                        conn = sqlite3.connect('govRental.db')
                        cursor = conn.cursor()
                        cursor.execute("UPDATE Stall SET Rental_Amount = ? WHERE Stall_ID = ?", (new_amount, stall_id))
                        conn.commit()
                        conn.close()
                        messagebox.showinfo("Success", "Rental amount updated successfully!")
                        rental_amount_entry.config(state='readonly')
                        update_rental_button.config(text="Update Rental")
                        # Update deposit and total amounts
                        update_all_amounts(new_amount)
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid number for rental amount")
                    rental_amount_entry.delete(0, END)
                    rental_amount_entry.focus()

        update_rental_button = Button(rental_amount_frame, text="Update Rental", font=('Arial', 10, 'bold'),
                                      activebackground='#fd5602', command=update_rental)
        update_rental_button.pack(side=LEFT, padx=5)

        def update_all_amounts(rental_amount):
            # Update rental amount
            rental_amount_entry.config(state='normal')
            rental_amount_entry.delete(0, END)
            rental_amount_entry.insert(0, str(rental_amount))
            rental_amount_entry.config(state='readonly')
            # Update deposit amount (1.5 times rental)
            deposit = rental_amount * 1.5
            deposit_entry.config(state='normal')
            deposit_entry.delete(0, END)
            deposit_entry.insert(0, str(deposit))
            deposit_entry.config(state='readonly')
            # Update total amount
            total = rental_amount + deposit
            total_entry.config(state='normal')
            total_entry.delete(0, END)
            total_entry.insert(0, str(total))
            total_entry.config(state='readonly')
            # Save total amount to database
            selected_stall = stall_combobox.get()
            if selected_stall:
                stall_id = selected_stall.split(",")[0].split(":")[1].strip()
                conn = sqlite3.connect('govRental.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE Stall SET Total_Amount = ? WHERE Stall_ID = ?", (total, stall_id))
                conn.commit()
                conn.close()

        # Fetch rental amount when stall is selected
        def update_rental_amount(event=None):
            selected_stall = stall_combobox.get()
            if selected_stall:
                stall_id = selected_stall.split(",")[0].split(":")[1].strip()
                conn = sqlite3.connect('govRental.db')
                cursor = conn.cursor()
                cursor.execute("SELECT Rental_Amount FROM Stall WHERE Stall_ID = ?", (stall_id,))
                result = cursor.fetchone()
                conn.close()
                if result:
                    rental_amount = float(result[0])
                    update_all_amounts(rental_amount)

        stall_combobox.bind('<<ComboboxSelected>>', update_rental_amount)
        deposit_frame = Frame(assign_container, bg='LavenderBlush2')
        deposit_frame.pack(pady=20)
        Label(deposit_frame, text="Deposit Amount (RM):", font=label_font, anchor='w', bg='LavenderBlush2').pack(
            side=LEFT,
            padx=5)
        deposit_entry = Entry(deposit_frame, width=30, font=entry_font, state='readonly')
        deposit_entry.pack(side=LEFT)
        total_frame = Frame(assign_container, bg='LavenderBlush2')
        total_frame.pack(pady=20)
        Label(total_frame, text="Total Amount (RM):", font=label_font, anchor='w', bg='LavenderBlush2').pack(side=LEFT,
                                                                                                             padx=5)
        total_entry = Entry(total_frame, width=30, font=entry_font, state='readonly')
        total_entry.pack(side=LEFT)
        payment_date_frame = Frame(assign_container, bg='LavenderBlush2')
        payment_date_frame.pack(pady=20)
        # Payment by date
        payment_date_inner_frame = Frame(payment_date_frame, bg='LavenderBlush2')
        payment_date_inner_frame.pack(fill=X)
        # Payment due date
        Label(payment_date_inner_frame, text="Payment due by:", font=label_font, anchor='w', bg='LavenderBlush2').pack(
            side=LEFT, padx=5)
        last_payment_entry = DateEntry(payment_date_inner_frame, width=27, background='darkblue', foreground='white',
                                       borderwidth=2, font=entry_font, calendar_position='above',
                                       mindate=datetime.now(),
                                       date_pattern='yy-mm-dd')
        last_payment_entry.pack(side=LEFT)

        # Update payment due date when contract start date changes
        def update_payment_due_date(*args):
            start_date = contract_start_entry.get_date()
            # Set payment due date to 7 days after the start date
            payment_due_date = start_date + timedelta(days=7)
            # Update the last payment entry with the calculated payment due date
            last_payment_entry.set_date(payment_due_date)
            # Update reminder date whenever payment due date changes
            reminder_date = payment_due_date - timedelta(days=3)
            reminder_entry.set_date(reminder_date)
            reminder_entry.config(state='readonly')

        contract_start_entry.bind('<<DateEntrySelected>>', update_payment_due_date)
        # Reminder date
        Label(payment_date_inner_frame, text="Send reminder on:", font=label_font, anchor='w',
              bg='LavenderBlush2').pack(
            side=LEFT, padx=5)
        reminder_entry = DateEntry(payment_date_inner_frame, width=27, background='darkblue', foreground='white',
                                   borderwidth=2, font=entry_font, calendar_position='above', mindate=datetime.now(),
                                   date_pattern='yy-mm-dd')  # Set date format to yyyy-mm-dd
        reminder_entry.pack(side=LEFT)

        # Update reminder date when payment due date changes
        def update_reminder_date(*args):
            payment_due = last_payment_entry.get_date()
            reminder_date = payment_due - timedelta(days=3)
            reminder_entry.set_date(reminder_date)
            reminder_entry.config(state='readonly')

        # Bind to both DateEntrySelected and when payment due date is updated
        last_payment_entry.bind('<<DateEntrySelected>>', update_reminder_date)
        # Initial updates
        update_payment_due_date()  # This will also update the reminder date
        agreement_frame = Frame(assign_container, bg='LavenderBlush2')
        agreement_frame.pack(pady=20)
        Label(agreement_frame, text="Contract Agreement:", font=label_font, anchor='w', bg='LavenderBlush2').pack(
            side=LEFT,
            padx=5)

        def generate_agreement():
            # Verify all fields are filled
            if not all([stall_combobox.get(), tenant_id_entry.get(), tenant_username_entry.get(),
                        rental_period_combobox.get(), rental_amount_entry.get(), deposit_entry.get()]):
                messagebox.showerror("Error", "Please fill in all required fields before generating agreement")
                return
            # Get all the entered details
            stall_details = stall_combobox.get().split(",")
            stall_id = stall_details[0].split(":")[1].strip()
            # Get full stall address by taking everything after first colon
            stall_address = stall_combobox.get().split(":", 2)[2].strip()
            tenant_id = tenant_id_entry.get()
            tenant_username = tenant_username_entry.get()
            rental_period = rental_period_combobox.get()
            start_date = contract_start_entry.get_date()
            end_date = contract_end_entry.get_date()
            rental_amount = rental_amount_entry.get()
            deposit = deposit_entry.get()
            # Create preview window
            preview_window = Toplevel()
            preview_window.title("Agreement Preview")
            preview_window.geometry("600x800")
            # Create scrollable text widget for preview
            preview_frame = Frame(preview_window)
            preview_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
            preview_text = Text(preview_frame, wrap=WORD, font=("Helvetica", 12))
            preview_text.pack(fill=BOTH, expand=True)
            # Insert agreement content
            # Fetch tenant IC from database
            conn = sqlite3.connect('govRental.db')
            cursor = conn.cursor()
            cursor.execute("SELECT Tenant_IC_Number FROM Tenant WHERE Tenant_Username = ?", (tenant_username,))
            tenant_ic = cursor.fetchone()[0]
            conn.close()
            preview_text.insert(END, "RENTAL AGREEMENT\n\n", "title")
            preview_text.insert(END, f"Tenant Name: {tenant_username}\n")
            preview_text.insert(END, f"Tenant IC: {tenant_ic}\n")
            preview_text.insert(END, f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n")
            preview_text.insert(END, f"Stall ID: {stall_id}\n")
            preview_text.insert(END, f"Stall Address: {stall_address}\n")
            preview_text.insert(END, f"Tenant ID: {tenant_id}\n")
            preview_text.insert(END, f"Tenant Name: {tenant_username}\n")
            preview_text.insert(END, f"Rental Period: {rental_period}\n")
            preview_text.insert(END, f"Contract Start Date: {start_date}\n")
            preview_text.insert(END, f"Contract End Date: {end_date}\n")
            preview_text.insert(END, f"Monthly Rental Amount: RM {rental_amount}\n")
            preview_text.insert(END, f"Security Deposit: RM {deposit}\n")
            preview_text.insert(END, f"Total Amount: RM {total_entry.get()}\n")
            ''''
            # Set contract status as active
            contract_status = "Active"
            preview_text.insert(END, f"Contract Status: {contract_status}\n\n")
            '''
            # Configure bold red text style
            preview_text.tag_configure("bold_red", font=("Helvetica", 12, "bold"), foreground="red")
            # Insert payment due date in bold red
            preview_text.insert(END, f"\n\nPlease paid by: {last_payment_entry.get_date()}\n\n", "bold_red")
            # Get current logged in admin info from login details
            conn = sqlite3.connect('govRental.db')
            cursor = conn.cursor()
            cursor.execute("SELECT Admin_ID, Admin_Name FROM Admin WHERE Admin_IC_Number = ?", (admin_ic,))
            admin = cursor.fetchone()
            conn.close()
            if admin:
                preview_text.insert(END, f"Admin ID: {admin[0]} | Admin Name: {admin[1]} \n")
            else:
                preview_text.insert(END, "Admin information not found\n")
            # Fetch business information
            conn = sqlite3.connect('govRental.db')
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Business_Name, Licence_No, Business_Hours, Location, Contact_No, Email_Address FROM Business_Information")
            business_info = cursor.fetchone()
            conn.close()
            if business_info:
                preview_text.insert(END, f"{business_info[0]}\n")
                preview_text.insert(END, f"License No: {business_info[1]}\n")
                preview_text.insert(END, f"{business_info[2]}\n")
                preview_text.insert(END, f"{business_info[3]}\n")
                preview_text.insert(END, f"Contact No: {business_info[4]}, Email: {business_info[5]}\n")
            preview_text.tag_configure("title", font=("Helvetica", 16, "bold"))
            preview_text.config(state=DISABLED)  # Make text read-only

            def confirm_and_generate():
                global notification
                try:
                    from reportlab.pdfgen import canvas
                    from reportlab.lib.pagesizes import letter
                    # Create PDF
                    c = canvas.Canvas(f"{tenant_username}_{tenant_id}_{start_date}.pdf", pagesize=letter)
                    # Add content
                    # First page
                    c.setFont("Helvetica-Bold", 16)
                    c.drawString(50, 750, "RENTAL AGREEMENT")
                    # Add tenant details right after title
                    c.setFont("Helvetica", 12)
                    c.drawString(50, 720, f"Tenant Name: {tenant_username}")
                    c.drawString(50, 700, f"Tenant IC: {tenant_ic}")
                    c.drawString(50, 680, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
                    # Main content
                    c.drawString(50, 640, f"Stall ID: {stall_id}")
                    c.drawString(50, 620, f"Stall Address: {stall_address}")
                    c.drawString(50, 600, f"Tenant ID: {tenant_id}")
                    c.drawString(50, 580, f"Rental Period: {rental_period}")
                    c.drawString(50, 560, f"Contract Start Date: {start_date}")
                    c.drawString(50, 540, f"Contract End Date: {end_date}")
                    # Financial details
                    y_pos = 520
                    for text in [
                        f"Monthly Rental Amount: RM {rental_amount}",
                        f"Security Deposit: RM {deposit}",
                        f"Total Amount: RM {total_entry.get()}",
                        f"Contract Status: Active",
                        f"Please paid by: {last_payment_entry.get_date()}"  # Added payment due date
                    ]:
                        c.drawString(50, y_pos, text)
                        y_pos -= 20
                    # Signature section
                    y_pos = y_pos - 20
                    # Get admin info from database
                    conn = sqlite3.connect('govRental.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT Admin_ID, Admin_Name FROM Admin WHERE Admin_IC_Number = ?", (admin_ic,))
                    admin = cursor.fetchone()
                    conn.close()
                    if admin:  # Only add admin info if found
                        for text in [
                            f"Admin ID: {admin[0]}, Admin Name: {admin[1]}",
                            f"Date: {datetime.now().strftime('%Y-%m-%d')}"
                        ]:
                            c.drawString(50, y_pos, text)
                            y_pos -= 20
                    # Add business information
                    conn = sqlite3.connect('govRental.db')
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT Business_Name, Licence_No, Business_Hours, Location, Contact_No, Email_Address FROM Business_Information")
                    business_info = cursor.fetchone()
                    conn.close()
                    if business_info:
                        y_pos = y_pos - 40
                        for text in [
                            f"{business_info[0]}",
                            f"License No: {business_info[1]}",
                            f"{business_info[2]}",
                            f"{business_info[3]}",
                            f"Contact No: {business_info[4]}, Email: {business_info[5]}"
                        ]:
                            c.drawString(50, y_pos, text)
                            y_pos -= 20
                    # Second page
                    c.showPage()
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(50, 750, "Terms & Conditions")
                    c.setFont("Helvetica", 12)
                    y = 700
                    line_height = 20
                    penalty = float(rental_amount) * 0.3
                    terms = [
                        f"Monthly rental of RM{rental_amount} is due at the 8th of each month.",
                        f"Late payments will incur a 30% penalty, amounting to RM{penalty:.2f}.",
                        f"The rental period begins on {start_date} and ends on {end_date} for an initial term of {rental_period}.",
                        "The Tenant cannot assign, transfer, or sublet the stall to others.",
                        "The Tenant is responsible for maintaining cleanliness and repairing any damages caused.",
                        "The Landlord may inspect the stall with prior notice to ensure compliance.",
                        "Upon termination or expiration, the Tenant must return the stall in its original condition, considering normal wear and tear.",
                        "Cleaning or repair costs will be deducted from the security deposit.",
                        "Breaching any terms, including subletting or unauthorized activities, may result in immediate termination of the Agreement.",
                        "Following termination for breach, the Tenant will be banned from renting government stalls in the future.",
                        "This Agreement supersedes any prior agreements and can only be amended in writing and signed by both parties."
                    ]
                    # Add image after terms
                    try:
                        from reportlab.lib.utils import ImageReader
                        import os
                        current_dir = os.path.dirname(os.path.abspath(__file__))
                        image_path = os.path.join(current_dir, "images", "Gov_Agreement_Stamp.png")
                        if os.path.exists(image_path):
                            img = ImageReader(image_path)
                            img_width = 200
                            img_height = 200
                            x = (letter[0] - img_width) / 2
                            c.drawImage(img, x, y - 20, width=img_width, height=img_height)
                        else:
                            print(f"Image file not found at: {image_path}")
                    except Exception as e:
                        print(f"Could not add image: {str(e)}")
                    for term in terms:
                        words = term.split()
                        line = ''
                        for word in words:
                            test_line = line + word + ' '
                            if len(test_line) * 6 > 500:
                                c.drawString(50, y, line)
                                y -= line_height
                                line = word + ' '
                            else:
                                line = test_line
                        c.drawString(50, y, line)
                        y -= line_height * 1.5
                    c.save()
                    root.update()
                    messagebox.showinfo("Success", "Agreement generated successfully!")
                    conn.close()
                    preview_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to generate agreement: {str(e)}")

            def cancel_generation():
                preview_window.destroy()

            # Add buttons frame
            button_frame = Frame(preview_window)
            button_frame.pack(pady=20)
            confirm_button = Button(button_frame, text="Confirm & Generate PDF",
                                    command=confirm_and_generate,
                                    font=("Arial", 10, "bold"),
                                    bg="#4CAF50", fg="white")
            confirm_button.pack(side=LEFT, padx=10)
            cancel_button = Button(button_frame, text="Make Changes",
                                   command=cancel_generation,
                                   font=("Arial", 10, "bold"),
                                   bg="#f44336", fg="white")
            cancel_button.pack(side=LEFT, padx=10)

        agreement_button = Button(agreement_frame, text="Generate Agreement", font=entry_font,
                                  command=generate_agreement)
        agreement_button.pack(side=LEFT)
        assign_button = Button(assign_container, text="Assign Stall", command=assign_stall, fg='white', bg='#fd5602',
                               activebackground='white', font=label_font)
        assign_button.pack(pady=20)
        # Tenant Register Tab - Center elements
        register_container = Frame(tenant_register_frame, width=1200, height=1000, bg='ivory2')
        register_container.pack(fill='both', expand=True)
        register_container.pack_propagate(False)
        # Create frames with explicit dimensions and background colors
        add_tenant_frame1 = Frame(register_container, width=400, height=1000, bg='ivory2')
        add_tenant_frame1.pack(side=LEFT, fill='both', expand=True)
        add_tenant_frame1.pack_propagate(False)
        add_tenant_frame2 = Frame(register_container, width=800, height=1000, bg='floral white')
        add_tenant_frame2.pack(side=RIGHT, fill='both', expand=True)
        add_tenant_frame2.pack_propagate(False)
        # Add authentication image
        auth_image = Image.open(r"C:/Kai_Shuang/vennis2.jpg")
        auth_image = auth_image.resize((250, 250), Image.Resampling.LANCZOS)  # Resize image
        auth_photo = ImageTk.PhotoImage(auth_image)
        auth_label = Label(add_tenant_frame1, image=auth_photo, bg='ivory2')
        auth_label.image = auth_photo  # Keep a reference to prevent garbage collection
        auth_label.pack(pady=(50, 0))
        # Add form elements to right frame
        form_frame = Frame(add_tenant_frame2, bg='floral white')
        form_frame.pack(pady=50)
        ic_frame = Frame(form_frame, bg='floral white')
        ic_frame.pack(pady=20)
        Label(ic_frame, text="Tenant IC Number: ", font=label_font, bg='floral white').pack(side=LEFT)
        tenant_ic_entry = ctk.CTkEntry(ic_frame, width=300, font=entry_font)
        tenant_ic_entry.pack(side=LEFT)
        name_frame = Frame(form_frame, bg='floral white')
        name_frame.pack(pady=20)
        Label(name_frame, text="Tenant Name:", font=label_font, bg='floral white').pack(side=LEFT)
        tenant_username_entry = ctk.CTkEntry(name_frame, width=300, font=entry_font)
        tenant_username_entry.pack(side=LEFT)
        shining_label = Label(form_frame,
                              text="* * * Temporary Password for every tenant is set refer to their IC Number. * * *",
                              font=('Arial', 12, 'italic', 'bold'), fg='blue', bg='floral white')
        shining_label.pack(pady=20)

        def shine():
            colors = ['blue', 'navy']
            current_color = shining_label.cget('fg')
            next_color = colors[(colors.index(current_color) + 1) % len(colors)]
            shining_label.config(fg=next_color)
            register_container.after(300, shine)

        shine()
        pass_frame = Frame(form_frame, bg='floral white')
        pass_frame.pack(pady=20)
        Label(pass_frame, text="Temporary Password :", font=label_font, bg='floral white').pack(side=LEFT)
        pass_entry = ctk.CTkEntry(pass_frame, width=300, font=entry_font, state='normal')
        pass_entry.pack(side=LEFT)

        def update_password(*args):
            ic = tenant_ic_entry.get()
            pass_entry.configure(state='normal')
            pass_entry.delete(0, 'end')
            pass_entry.insert(0, ic)
            pass_entry.configure(state='readonly')

        tenant_ic_entry.bind('<KeyRelease>', update_password)
        add_button = ctk.CTkButton(form_frame, text="Register New Tenant", command=add_tenant,
                                   font=('Arial', 12, 'bold'), fg_color='#fd5602',
                                   hover_color='#db4a02', width=200)
        add_button.pack(pady=20)
        # change Tenant database to Null for others except Tenant_IC_Number, Tenant_Username, Password

    def payment_management():
        payment_manage_frame = Frame(main_frame)
        payment_manage_frame.place(relwidth=1, relheight=1)

        def search_payments():
            start_date = start_date_entry.get()
            end_date = end_date_entry.get()
            # Clear existing items in treeview
            for item in transaction_tree.get_children():
                transaction_tree.delete(item)
            try:
                # Query payments within date range with calculated fields
                cursor.execute("""
                SELECT Payment_ID, Tenant_ID, Tenant_Name, Transaction_Date, 
                       Rental_Amount, Status, Overdue_Status, Overdue_Amount, Total_Amount
                FROM Payment_Manage
                WHERE Transaction_Date BETWEEN ? AND ?
                """, (start_date, end_date))
                payments = cursor.fetchall()
                # Insert payments into treeview
                for payment in payments:
                    transaction_tree.insert('', 'end', values=payment)
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

        def load_all_payments():
            # Clear existing items in treeview
            for item in transaction_tree.get_children():
                transaction_tree.delete(item)
            try:
                # Query all payments with calculated fields
                cursor.execute("""
                SELECT Payment_ID, Tenant_ID, Tenant_Name, Transaction_Date, 
                       Rental_Amount, Status, Overdue_Status, Overdue_Amount, Total_Amount
                FROM Payment_Manage
            """)
                payments = cursor.fetchall()
                # Insert payments into treeview
                for payment in payments:
                    transaction_tree.insert('', 'end', values=payment)
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

        def view_monthly_payments():
            # Clear existing items in treeview
            for item in transaction_tree.get_children():
                transaction_tree.delete(item)
            try:
                # Query payments grouped by month with calculated fields
                cursor.execute("""
                SELECT Payment_ID, Tenant_ID, Tenant_Name, Transaction_Date, 
                       Rental_Amount, Status, Overdue_Status, Overdue_Amount, Total_Amount
                FROM Payment_Manage
                ORDER BY strftime('%Y-%m', Transaction_Date)
                """)
                payments = cursor.fetchall()
                # Insert payments into treeview
                for payment in payments:
                    transaction_tree.insert('', 'end', values=payment)
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

        Label(payment_manage_frame, text="Admin- Payment Management", fg='black', font=("Arial", 35, "bold")).place(
            x=650,
            y=30)
        # Define font for labels
        font = ("Arial", 14, "bold")
        notebook = ttk.Notebook(payment_manage_frame)
        notebook.place(x=0, y=100, width=1920, height=930)
        # Create Transaction History tab
        transaction_frame = Frame(notebook, bg='mint cream')
        notebook.add(transaction_frame, text='  Payment Management', padding=10)
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Arial', 16, 'bold'))
        # Configure notebook tab width and selected color
        style.configure('TNotebook', tabposition='n', width=1920)
        style.configure('TNotebook.Tab', width=960)  # Split width evenly between 2 tabs
        style.map('TNotebook.Tab', foreground=[('selected', '#fd5602')])
        # Create Overdue Payments tab
        overdue_frame = Frame(notebook, bg='mint cream')
        notebook.add(overdue_frame, text='  Overdue Management', padding=10)
        # Add date selection and search to Transaction History tab
        date_frame = Frame(transaction_frame, bg='mint cream')
        date_frame.pack(pady=10, fill=X)  # Added fill=X to make frame expand horizontally
        # Label for Start Date
        start_date_label = Label(date_frame, text="Start Date:", font=("Arial", 14, "bold"), bg='mint cream')
        start_date_label.pack(side=LEFT, padx=15)  # Changed to pack layout
        # Date Entry for Start Date
        start_date_entry = DateEntry(date_frame, font=font, width=12, background='darkblue', foreground='white',
                                     date_pattern='yyyy-mm-dd')
        start_date_entry.pack(side=LEFT, padx=15)  # Changed to pack layout
        # Label for End Date
        end_date_label = Label(date_frame, text="End Date:", font=("Arial", 14, "bold"), bg='mint cream')
        end_date_label.pack(side=LEFT, padx=15)  # Changed to pack layout
        # Date Entry for End Date
        end_date_entry = DateEntry(date_frame, font=font, width=12, background='darkblue', foreground='white',
                                   date_pattern='yyyy-mm-dd')
        end_date_entry.pack(side=LEFT, padx=15)  # Changed to pack layout
        # Search Button
        search_button = ttk.Button(date_frame, text="Search",
                                   command=lambda: search_payments(start_date_entry.get(), end_date_entry.get()),
                                   style="TButton")
        style = ttk.Style()
        style.configure("TButton", font=font)
        search_button.pack(side=LEFT, padx=15)  # Changed to pack layout

        # Function to search payments between dates
        def search_payments(start_date, end_date):
            # Clear existing items in treeview
            for item in transaction_tree.get_children():
                transaction_tree.delete(item)
            try:
                # Query payments between selected dates
                cursor.execute("""
                SELECT Payment_ID, Tenant_ID, Tenant_Name, Transaction_Date, 
                       Rental_Amount, Status, Overdue_Status, Overdue_Amount, Total_Amount
                FROM Payment_Manage
                    WHERE DATE(Transaction_Date) BETWEEN ? AND ?
                """, (start_date, end_date))
                payments = cursor.fetchall()
                # Insert filtered payments into treeview
                for payment in payments:
                    transaction_tree.insert('', 'end', values=payment)
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

        # Create Treeview for Transaction History
        transaction_tree = ttk.Treeview(transaction_frame, columns=(
            "Payment ID", "Tenant ID", "Tenant Name", "Date", "Amount", "Status", "Overdue Status", "Overdue Amount",
            "Total Amount"), show="headings", height=20)
        # Configure Transaction History columns with center alignment
        # Configure column headings
        transaction_tree.heading("Payment ID", text="Payment ID", anchor=CENTER)
        transaction_tree.heading("Tenant ID", text="Tenant ID", anchor=CENTER)
        transaction_tree.heading("Tenant Name", text="Tenant Name", anchor=CENTER)
        transaction_tree.heading("Date", text="Date", anchor=CENTER)
        transaction_tree.heading("Amount", text="Amount", anchor=CENTER)
        transaction_tree.heading("Status", text="Status", anchor=CENTER)
        transaction_tree.heading("Overdue Status", text="Overdue", anchor=CENTER)
        transaction_tree.heading("Overdue Amount", text="Penalty", anchor=CENTER)
        transaction_tree.heading("Total Amount", text="Total", anchor=CENTER)
        # Configure column widths and center alignment
        transaction_tree.column("Payment ID", width=120, anchor=CENTER)
        transaction_tree.column("Tenant ID", width=120, anchor=CENTER)
        transaction_tree.column("Tenant Name", width=150, anchor=CENTER)
        transaction_tree.column("Date", width=150, anchor=CENTER)
        transaction_tree.column("Amount", width=120, anchor=CENTER)
        transaction_tree.column("Status", width=120, anchor=CENTER)
        transaction_tree.column("Overdue Status", width=120, anchor=CENTER)
        transaction_tree.column("Overdue Amount", width=120, anchor=CENTER)
        transaction_tree.column("Total Amount", width=120, anchor=CENTER)
        # Fetch and display data
        for item in transaction_tree.get_children():
            transaction_tree.delete(item)
        try:
            cursor.execute("""
                SELECT Payment_ID, Tenant_ID, Tenant_Name, Transaction_Date, 
                       Rental_Amount, Status, Overdue_Status, Overdue_Amount, Total_Amount
                FROM Payment_Manage
            """)
            payments = cursor.fetchall()
            for payment in payments:
                transaction_tree.insert('', 'end', values=payment)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
        # Configure fonts
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))
        style.configure("Treeview", font=("Arial", 12))
        # Add scrollbar for Transaction History
        # transaction_scrollbar = ttk.Scrollbar(transaction_frame, orient=VERTICAL, command=transaction_tree.yview)
        # transaction_tree.configure(yscrollcommand=transaction_scrollbar.set)
        # Place Transaction History treeview and scrollbar
        # transaction_scrollbar.pack(side=RIGHT, fill=Y)
        transaction_tree.place(x=15, y=80)
        # Load initial data into transaction tree
        load_all_payments()

        def view_payment_details():
            selected_item = transaction_tree.selection()
            if not selected_item:
                messagebox.showwarning("Selection Required", "Please select a payment to view details")
                return
            payment_id = transaction_tree.item(selected_item)['values'][0]
            try:
                # Clear previous details in side frame first, except the details_label
                for widget in side_frame.winfo_children():
                    if widget != details_label:
                        widget.destroy()
                # Get payment details
                cursor.execute("""
                    SELECT * FROM Payment_Manage 
                    WHERE Payment_ID = ?
                """, (payment_id,))
                payment_details = cursor.fetchone()
                if payment_details:
                    # Create treeview to display details
                    details_tree = ttk.Treeview(side_frame, columns=("Field", "Value"), show="headings", height=16)
                    details_tree.heading("Field", text="Field")
                    details_tree.heading("Value", text="Value")
                    details_tree.column("Field", width=200)
                    details_tree.column("Value", width=300)
                    # Insert payment details into treeview
                    details = [
                        ("Payment ID", payment_details[0]),
                        ("Tenant ID", payment_details[1]),
                        ("Tenant Name", payment_details[2]),
                        ("Stall ID", payment_details[3]),
                        ("Postcode", payment_details[4]),
                        ("Rental Amount", payment_details[5]),
                        ("Transaction Date", payment_details[6]),
                        ("Remarks", payment_details[7]),
                        ("Bank Slip", payment_details[8]),
                        ("Status", payment_details[9]),
                        ("Gov Receipts", payment_details[10]),
                        ("Due Date", payment_details[11]),
                        ("Overdue Status", payment_details[12]),
                        ("Overdue Amount", payment_details[13]),
                        ("Total Amount", payment_details[14])
                    ]
                    for field, value in details:
                        details_tree.insert("", "end", values=(field, value))
                    details_tree.pack(padx=10, pady=(0, 10))
                    # Create a frame for buttons
                    button_frame = Frame(side_frame, bg='white')
                    button_frame.pack(pady=10)

                    def view_bank_slip(bank_slip_path):
                        if bank_slip_path and os.path.exists(bank_slip_path):
                            try:
                                os.startfile(bank_slip_path)  # For Windows
                            except:
                                try:
                                    subprocess.run(['xdg-open', bank_slip_path])  # For Linux
                                except:
                                    try:
                                        subprocess.run(['open', bank_slip_path])  # For macOS
                                    except:
                                        messagebox.showerror("Error", "Could not open bank slip file")
                        else:
                            messagebox.showerror("Error", "Bank slip file not found")

                    def view_gov_receipt(receipt_path):
                        if receipt_path and os.path.exists(receipt_path):
                            try:
                                os.startfile(receipt_path)  # For Windows
                            except:
                                try:
                                    subprocess.run(['xdg-open', receipt_path])  # For Linux
                                except:
                                    try:
                                        subprocess.run(['open', receipt_path])  # For macOS
                                    except:
                                        messagebox.showerror("Error", "Could not open government receipt file")
                        else:
                            messagebox.showerror("Error", "Government receipt file not found")

                    # Add buttons to the button frame
                    Button(button_frame, text='View Bank Slip', fg='black', bg='ivory2', activebackground='#fd5602',
                           font=('Times new roman', 14), width=15,
                           command=lambda: view_bank_slip(payment_details[8])).pack(
                        side=LEFT, padx=10)
                    Button(button_frame, text='View Gov Receipt', fg='black', bg='ivory2', activebackground='#fd5602',
                           font=('Times new roman', 14), width=15,
                           command=lambda: view_gov_receipt(payment_details[10])).pack(
                        side=LEFT, padx=10)

                    def show_status_options():
                        # Create frame for radio buttons below button frame
                        status_frame = Frame(side_frame, bg='white')
                        status_frame.pack(pady=10)
                        # Create StringVar to store selected status
                        status_var = StringVar()
                        status_var.set('Completed')  # Default selection
                        # Create radio buttons
                        Radiobutton(status_frame, text='Completed', variable=status_var, value='Completed', bg='white',
                                    font=('Arial', 12, 'bold')).pack(side=LEFT, padx=10)
                        Radiobutton(status_frame, text='Pending', variable=status_var, value='Pending', bg='white',
                                    font=('Arial', 12, 'bold')).pack(side=LEFT, padx=10)
                        # Add save button below radio buttons
                        save_btn = Button(status_frame, text='Save Changes', fg='white', bg='blue',
                                          activebackground='white',
                                          font=('Times new roman', 12), width=12,
                                          command=lambda: save_status_changes(payment_details[0], status_var.get(),
                                                                              status_frame, update_status_btn))
                        save_btn.pack(pady=10)
                        # Disable the update status button while editing
                        update_status_btn.config(state='disabled')

                    def save_status_changes(payment_id, new_status, status_frame, update_btn):
                        try:
                            # Update status in database
                            cursor.execute("""
                                UPDATE Payment_Manage 
                                SET Status = ? 
                                WHERE Payment_ID = ?
                            """, (new_status, payment_id))
                            conn.commit()
                            messagebox.showinfo("Status Update",
                                                f"Payment ID {payment_id}: Status updated to {new_status}.")
                            # Refresh the transaction tree view
                            show_all_data()
                            # Forget (remove) the status frame containing radio buttons and save button
                            status_frame.pack_forget()
                            # Re-enable the update status button
                            update_btn.config(state='normal')
                        except sqlite3.Error as e:
                            messagebox.showerror("Database Error", f"Failed to update status: {str(e)}")

                    update_status_btn = Button(button_frame, text='Update Status', fg='black', bg='#fd5602',
                                               activebackground='ivory2', font=('Times new roman', 14), width=15,
                                               command=show_status_options)
                    update_status_btn.pack(side=LEFT, padx=10)
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

        def show_all_data():
            # Clear existing items in treeview
            for item in transaction_tree.get_children():
                transaction_tree.delete(item)
            try:
                # Query all payment details from database
                cursor.execute("""
                        SELECT Payment_ID, Tenant_ID, Tenant_Name, Transaction_Date, 
                               Rental_Amount, Status, Overdue_Status, Overdue_Amount, Total_Amount
                        FROM Payment_Manage
                    """)
                payments = cursor.fetchall()
                # Insert all payments into treeview
                for payment in payments:
                    transaction_tree.insert('', 'end', values=payment)
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

        show_all_button = Button(transaction_frame, text='Show All', font=('Arial', 12, 'bold'), bg='#fd5602',
                                 activebackground='white', command=show_all_data, width=12)
        show_all_button.place(x=350, y=550)

    view_details_button = Button(transaction_frame, text='View Details', font=('Arial', 12, 'bold'), bg='#fd5602',
                                 activebackground='white', command=view_payment_details, width=12)
    view_details_button.place(x=600, y=550)
    # Create frame beside transaction treeview
    side_frame = Frame(transaction_frame, bg='white', width=650, height=600, relief="solid", borderwidth=1)
    side_frame.place(x=1200, y=80)
    side_frame.pack_propagate(False)  # Prevent the frame from shrinking
    # Create details label at the top of side frame
    details_label = Label(side_frame, text='Details:', font=("Times new roman", 20), bg='white', fg='black')
    details_label.pack(padx=10, pady=10, anchor='nw')
    # Create Treeview for Overdue Payments
    # Create label to show current time
    Label(overdue_frame, text="Current Date & Time: ", font=("Times new roman", 20), fg="blue", bg='mint cream').place(
        x=25, y=20)
    current_time_label = Label(overdue_frame, text="", font=("Times new roman", 20), fg="blue", bg='mint cream')
    current_time_label.place(x=280, y=20)

    def update_time():
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_time_label.config(text=current_time)
        current_time_label.after(1000, update_time)  # Update every 1 second

    update_time()  # Start the time update
    '''
    # Add a checkbox at the right top on the same line as current_time
    show_time_var = IntVar()
    show_time_checkbox = Checkbutton(overdue_frame, text="Show Time", variable=show_time_var, font=("Times new roman", 14), bg='mint cream')
    show_time_checkbox.place(x=600, y=20)
    '''
    # Create frames for checkboxes and labels
    checkbox_frame = Frame(overdue_frame, bg='mint cream')
    checkbox_frame.place(x=1570, y=20)
    label_frame = Frame(overdue_frame, bg='mint cream')
    label_frame.place(x=1570, y=50)
    # Create the monthly label
    monthly_label = Label(label_frame, text="", font=("Times new roman", 14), bg='mint cream')
    monthly_label.pack(anchor='w')
    # Initialize variables
    show_monthly_var = IntVar()
    show_all_var = IntVar()
    # Create both checkboxes at initialization
    show_monthly_checkbox = Checkbutton(
        checkbox_frame,
        text="Show Current Month Records",
        variable=show_monthly_var,
        font=("Times new roman", 14),
        bg='mint cream',
        command=lambda: filter_monthly_records()
    )
    show_all_checkbox = Checkbutton(
        checkbox_frame,
        text="Show All Records",
        variable=show_all_var,
        font=("Times new roman", 14),
        bg='mint cream',
        command=lambda: show_all_records()
    )
    # Initially show only the monthly checkbox
    show_monthly_checkbox.pack(anchor='w')

    def show_all_records():
        # Clear existing items in the treeview
        for item in overdue_tree.get_children():
            overdue_tree.delete(item)
        # Update label
        monthly_label.config(text="All Records Shown", fg='green')
        # Reset checkboxes
        show_monthly_var.set(0)
        show_all_var.set(1)
        # Show monthly checkbox, hide all records checkbox
        show_all_checkbox.pack_forget()
        show_monthly_checkbox.pack(anchor='w')
        # Query and display all records
        try:
            cursor.execute("""
            SELECT Payment_ID, Tenant_ID, Tenant_Name, Rental_Amount, Payment_Due, 
                   Overdue_Status, Overdue_Amount, Total_Amount, Reminder_Date
            FROM Payment_Manage
            """)
            payments = cursor.fetchall()
            for payment in payments:
                overdue_tree.insert('', 'end', values=payment)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    def filter_monthly_records():
        # Clear existing items in the treeview
        for item in overdue_tree.get_children():
            overdue_tree.delete(item)
        # Update label and show all records checkbox
        monthly_label.config(text="Current Month Records Shown", fg='red')
        show_monthly_checkbox.pack_forget()
        show_all_checkbox.pack(anchor='w')
        # Get current month and year
        current_month = datetime.now().month
        current_year = datetime.now().year
        # Query and filter records
        try:
            cursor.execute("""
            SELECT Payment_ID, Tenant_ID, Tenant_Name, Rental_Amount, Payment_Due, 
                   Overdue_Status, Overdue_Amount, Total_Amount, Reminder_Date
            FROM Payment_Manage
            """)
            payments = cursor.fetchall()
            for payment in payments:
                if payment[4] is None:
                    continue
                try:
                    payment_due_date = datetime.strptime(payment[4], "%Y-%m-%d")
                    if payment_due_date.month == current_month and payment_due_date.year == current_year:
                        overdue_tree.insert('', 'end', values=payment)
                except ValueError:
                    continue
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    overdue_tree = ttk.Treeview(overdue_frame, columns=(
        "Payment ID", "Tenant ID", "Tenant Name", "Rental Amount", "Due Date", "Overdue Status", "Overdue Amount",
        "Total Amount", "Reminder Date"), show="headings", height=12)
    # Configure Overdue Payments columns with center alignment
    overdue_tree.heading("Payment ID", text="Payment ID", anchor=CENTER)
    overdue_tree.heading("Tenant ID", text="Tenant ID", anchor=CENTER)
    overdue_tree.heading("Tenant Name", text="Tenant Name", anchor=CENTER)
    overdue_tree.heading("Rental Amount", text="Rental Amount", anchor=CENTER)
    overdue_tree.heading("Due Date", text="Due Date", anchor=CENTER)
    overdue_tree.heading("Overdue Status", text="Overdue Status", anchor=CENTER)
    overdue_tree.heading("Overdue Amount", text="Overdue Amount", anchor=CENTER)
    overdue_tree.heading("Total Amount", text="Total Amount", anchor=CENTER)
    overdue_tree.heading("Reminder Date", text="Reminder Date", anchor=CENTER)
    # Configure column widths and center alignment
    overdue_tree.column("Payment ID", width=180, anchor=CENTER)
    overdue_tree.column("Tenant ID", width=180, anchor=CENTER)
    overdue_tree.column("Tenant Name", width=260, anchor=CENTER)
    overdue_tree.column("Rental Amount", width=220, anchor=CENTER)
    overdue_tree.column("Due Date", width=180, anchor=CENTER)
    overdue_tree.column("Overdue Status", width=200, anchor=CENTER)
    overdue_tree.column("Overdue Amount", width=200, anchor=CENTER)
    overdue_tree.column("Total Amount", width=200, anchor=CENTER)
    overdue_tree.column("Reminder Date", width=220, anchor=CENTER)
    # Configure fonts
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 14, "bold"))
    style.configure("Treeview", font=("Arial", 12))
    # Add scrollbar for Overdue Payments
    # overdue_scrollbar = ttk.Scrollbar(overdue_frame, orient=VERTICAL, command=overdue_tree.yview)
    # overdue_tree.configure(yscrollcommand=overdue_scrollbar.set)
    # Place Overdue Payments treeview and scrollbar
    overdue_tree.place(x=25, y=90)

    # Function to load overdue payments
    def load_overdue_payments():
        # Clear existing items
        for item in overdue_tree.get_children():
            overdue_tree.delete(item)
        try:
            conn = sqlite3.connect('govRental.db')
            cursor = conn.cursor()
            # Get overdue payments with all required fields
            cursor.execute("""
                SELECT 
                    Payment_ID,
                    Tenant_ID,
                    Tenant_Name,
                    Rental_Amount,
                    Payment_Due,
                    Overdue_Status,
                    Overdue_Amount,
                    Total_Amount,
                    Reminder_Date
                FROM Payment_Manage
                WHERE Transaction_Date IS NULL
                AND Status = 'Pending'
            """)
            overdue_payments = cursor.fetchall()
            # Insert payments into treeview
            for payment in overdue_payments:
                payment_id = payment[0]
                tenant_id = payment[1]
                tenant_name = payment[2]
                rental_amount = payment[3]
                payment_due = payment[4] if payment[4] is not None else "N/A"
                overdue_status = payment[5]
                overdue_amount = payment[6]
                total_amount = payment[7] if payment[7] is not None else 0.0  # Handle NoneType for total_amount
                reminder_date = payment[8]
                overdue_tree.insert('', 'end', values=(
                    payment_id,
                    tenant_id,
                    tenant_name,
                    f'RM {rental_amount:.2f}',
                    payment_due,
                    overdue_status,
                    f'RM {overdue_amount:.2f}',
                    f'RM {total_amount:.2f}',
                    reminder_date
                ))
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    # Load overdue payments initially
    load_overdue_payments()
    # Add a label below overdue_tree
    reminder_label = Label(overdue_frame, text="Reminder Message", font=("Arial", 16, "bold"), fg='blue',
                           bg='mint cream')
    reminder_label.place(x=25, y=400)
    '''
    # Add a new Treeview below the label
    reminder_tree = ttk.Treeview(overdue_frame, columns=("Reminder ID", "Message"), show="headings", height=5)
    # Configure Reminder Treeview columns
    reminder_tree.heading("Reminder ID", text="Reminder ID", anchor=CENTER)
    reminder_tree.heading("Message", text="Message", anchor=CENTER)
    # Configure column widths and center alignment
    reminder_tree.column("Reminder ID", width=180, anchor=CENTER)
    reminder_tree.column("Message", width=400, anchor=CENTER)
    # Place Reminder Treeview
    reminder_tree.place(x=25, y=450)
    '''

    def check_and_send_reminders():
        # Get the current date in YYYY-MM-DD format
        current_date = datetime.now().strftime("%Y-%m-%d")
        # Query to find tenants with reminders set for today in Payment_Manage
        cursor.execute("""
        SELECT pm.Stall_ID, pm.Tenant_ID, pm.Tenant_Name, pm.Reminder_Date
        FROM Payment_Manage pm
        WHERE pm.Reminder_Date = ?
        """, (current_date,))
        results = cursor.fetchall()
        for row in results:
            stall_id, tenant_id, tenant_username, reminder_date = row
            reminder_message = "This is a reminder for your upcoming payment due."
            # Insert a new reminder entry into the Reminder table
            cursor.execute("""
            INSERT INTO Reminders (Tenant_ID, Tenant_Username, Date_Time, Message, read, Tenant_Email_Address)
            VALUES (?, ?, '', ?, ?, ?)
            """, (tenant_id, tenant_username, stall_id, reminder_message, current_date))  #
        # Commit the changes
        conn.commit()

    def display_reminders():
        # Query to fetch reminder details for the Treeview display
        cursor.execute("""
        SELECT Tenant_ID, Tenant_Username, Date_Time, Message, read, Tenant_Email_Address FROM Reminders
        """)
        reminders = cursor.fetchall()
        # Configure Treeview
        reminder_tree = ttk.Treeview(overdue_frame, columns=(
            "Reminder_ID", "Tenant_ID", "Tenant_Username", "Date_Time", "Message"),
                                     show="headings")
        reminder_tree.heading("Reminder_ID", text="Reminder ID")
        reminder_tree.heading("Tenant_ID", text="Tenant ID")
        reminder_tree.heading("Tenant_Username", text="Tenant Username")
        reminder_tree.heading("Date_Time", text="Sent Date")
        reminder_tree.heading("Reminder_Message", text="Message")
        # Insert data into Treeview
        for reminder in reminders:
            reminder_tree.insert("", "end", values=reminder)
        reminder_tree.place(x=25, y=450)

    check_and_send_reminders()
    display_reminders()


def analytics_and_report():
    report_frame = Frame(main_frame)
    report_frame.place(relwidth=1, relheight=1)
    radio_button_frame = Frame(report_frame, width=350, height=1080)
    radio_button_frame.place(x=0, y=0)
    chart_frame = Frame(report_frame, width=1500, height=800, bg='white')
    chart_frame.place(x=350, y=100)

    def show_selection():
        selection = var.get()
        print(f"Selected option: {selection}")

    def attendance_report():
        # Clear existing widgets in chart frame
        for widget in chart_frame.winfo_children():
            widget.destroy()
        # Create date picker frame
        date_frame = Frame(chart_frame, width=1500, height=800, bg='white')
        date_frame.place(x=0, y=0)
        # Add date picker
        Label(date_frame, text="Select Date:", bg='white', font=('Arial', 14, 'bold')).place(x=20, y=25)
        date_picker = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2,
                                font=('Arial', 14))
        date_picker.place(x=140, y=25)
        # Create container frame for canvas and scrollbar
        container = Frame(date_frame, width=1450, height=650, bg='white')
        container.place(x=10, y=60)
        container.pack_propagate(False)
        # Create canvas and scrollbar
        canvas = Canvas(container, bg='white')
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg='white')
        # Configure the canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        # Pack canvas and scrollbar
        scrollbar.pack(side=RIGHT, fill=Y)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        # Create text widget inside scrollable frame
        attendance_text = Text(scrollable_frame, width=165, height=35, bg='white', font=('Arial', 14))
        attendance_text.pack(padx=5, pady=5)

        def update_report():
            selected_date = date_picker.get_date()
            date_str = selected_date.strftime('%Y-%m-%d')  # Ensure date format matches the database
            # Clear previous text
            attendance_text.delete('1.0', END)
            # Query to get all tenants
            cursor.execute("SELECT Tenant_ID, Tenant_IC_Number, Tenant_Username FROM Tenant")
            all_tenants = cursor.fetchall()
            # Query to get attendance for selected date
            cursor.execute("""
                SELECT Tenant_IC_Number, Clock_In_Time, Clock_Out_Time,
                       Clock_In_Status, Clock_Out_Status
                FROM Attendance 
                WHERE Date = ?
            """, (date_str,))
            attendance_records = cursor.fetchall()
            # Convert attendance records to a dictionary for easy lookup
            attendance_dict = {record[0]: record for record in attendance_records}
            # Debugging outputs (optional, for troubleshooting)
            print("Selected date:", date_str)
            print("Attendance records:", attendance_records)
            print("Attendance dictionary:", attendance_dict)
            # Display header
            attendance_text.insert(END, f"Attendance Report for {selected_date.strftime('%d/%m/%Y')}\n")
            attendance_text.insert(END, "=" * 70 + "\n\n")
            # Configure tag for red text
            attendance_text.tag_configure("red_text", foreground="red")
            # Display attendance status for each tenant
            for tenant in all_tenants:
                tenant_id, tenant_ic, tenant_username = tenant
                attendance_text.insert(END, f"Tenant: {tenant_username} (ID: {tenant_id})\n")
                if tenant_ic in attendance_dict:
                    record = attendance_dict[tenant_ic]
                    clock_in_time = record[1] or "N/A"
                    clock_out_time = record[2] or "N/A"
                    clock_in_status = record[3] or "N/A"
                    clock_out_status = record[4] or "N/A"
                    attendance_text.insert(END, f"Clock In Time: {clock_in_time} - Status: {clock_in_status}\n")
                    attendance_text.insert(END, f"Clock Out Time: {clock_out_time} - Status: {clock_out_status}\n")
                else:
                    # No attendance record for this date
                    attendance_text.insert(END, "No attendance record for this date\n", "red_text")
                attendance_text.insert(END, "-" * 100 + "\n")
            # Reset scroll position to top
            attendance_text.see("1.0")

        # Add search button
        ctk.CTkButton(date_frame, text="Search", command=update_report, fg_color='#4CAF50', text_color='white',
                      font=('Arial', 14, 'bold'), hover_color='black').place(x=300, y=25)

    def yearly_income_report():
        # Clear existing widgets in chart frame
        for widget in chart_frame.winfo_children():
            widget.destroy()
        # Create a new frame for yearly income report with full width/height
        income_frame = Frame(chart_frame, width=1500, height=800, bg='white')
        income_frame.place(x=0, y=0)
        income_frame.pack_propagate(False)  # Prevent frame from shrinking

        def get_yearly_income():
            connection = sqlite3.connect('govRental.db')
            cursor = connection.cursor()
            try:
                # Query to get total rental amount for each month from Payment_Manage table
                cursor.execute("""
                    SELECT strftime('%Y-%m', Transaction_Date) AS year_month, 
                           COALESCE(SUM(Rental_Amount), 0) as total_rental
                    FROM Payment_Manage
                    WHERE Transaction_Date IS NOT NULL
                    AND Status = 'Completed'
                    GROUP BY year_month
                    ORDER BY year_month
                """)
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=['year_month', 'rental'])
                df['rental'] = pd.to_numeric(df['rental'])
                if len(data) > 0:
                    df['year_month'] = pd.to_datetime(df['year_month'], format='%Y-%m')
                    min_date = df['year_month'].min()
                    max_date = df['year_month'].max()
                    date_range = pd.date_range(start=min_date, end=max_date, freq='MS')
                    all_months_df = pd.DataFrame({'year_month': date_range})
                    df = pd.merge(all_months_df, df, on='year_month', how='left')
                    df['rental'] = df['rental'].fillna(0)
                    months = [date.strftime('%B %Y') for date in df['year_month']]
                    rental_values = df['rental'].tolist()
                else:
                    months = []
                    rental_values = []
            except Exception as e:
                messagebox.showerror("Database Error", f"An error occurred: {e}")
                print(e)
                return [], [], None
            finally:
                connection.close()
            return months, rental_values, df

        def save_to_excel():
            file_name = "Monthly_Rental_Report.xlsx"
            try:
                df.to_excel(file_name, index=False)
                messagebox.showinfo("Excel Export", f"Data exported successfully to {file_name}")
            except Exception as e:
                messagebox.showerror("Excel Export Error", f"An error occurred while exporting data: {e}")
                print(e)

        def show_details():
            details_window = Toplevel()
            details_window.title("Rental Amount Details")
            details_window.geometry("600x400")
            details_window.configure(bg='white')
            details_frame = Frame(details_window, bg='white')
            details_frame.pack(padx=20, pady=20, fill=BOTH, expand=True)
            title_label = Label(details_frame,
                                text=f"Monthly Rental Breakdown for {year}",
                                font=('Arial', 14, 'bold'),
                                bg='white')
            title_label.pack(pady=(0, 20))
            headers_frame = Frame(details_frame, bg='white')
            headers_frame.pack(fill=X, padx=10)
            Label(headers_frame, text="Month", font=('Arial', 12, 'bold'),
                  width=20, bg='white').pack(side=LEFT)
            Label(headers_frame, text="Rental Amount (RM)", font=('Arial', 12, 'bold'),
                  width=20, bg='white').pack(side=LEFT)
            canvas = Canvas(details_frame, bg='white')
            scrollbar = Scrollbar(details_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = Frame(canvas, bg='white')
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            for month, rental in zip(months, rental_values):
                row_frame = Frame(scrollable_frame, bg='white')
                row_frame.pack(fill=X, padx=10, pady=2)
                Label(row_frame, text=month, font=('Arial', 11),
                      width=20, bg='white').pack(side=LEFT)
                Label(row_frame, text=f"{rental:,.2f}", font=('Arial', 11),
                      width=20, bg='white').pack(side=LEFT)
            canvas.pack(side="left", fill="both", expand=True, padx=10, pady=(10, 0))
            scrollbar.pack(side="right", fill="y", pady=(10, 0))

        # Get data first before creating widgets
        months, rental_values, df = get_yearly_income()
        if not months or not rental_values:
            # Show message if no data
            no_data_label = Label(
                income_frame,
                text="No rental data available",
                font=('Arial', 14, 'bold'),
                bg='white'
            )
            no_data_label.pack(pady=20)
            return
        # Calculate total rental amount
        total_rental = sum(rental_values)
        year = months[0].split()[-1] if months else ""
        # Create figure and canvas
        fig = plt.Figure(figsize=(12, 6))
        fig.patch.set_facecolor('none')
        canvas = FigureCanvasTkAgg(fig, master=income_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=BOTH, expand=True)
        # Add total label
        total_label = Label(
            income_frame,
            text=f"Total Rental Amount for Year {year}: RM {total_rental:,.2f}",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#002400'
        )
        total_label.pack(pady=10)
        # Add details button
        details_button = Label(
            income_frame,
            text="Details",
            font=('Arial', 10, 'underline'),
            bg='white',
            fg='blue',
            cursor='hand2'
        )
        details_button.pack(pady=5)
        details_button.bind('<Button-1>', lambda e: show_details())
        details_button.bind('<Enter>', lambda e: details_button.configure(fg='purple'))
        details_button.bind('<Leave>', lambda e: details_button.configure(fg='blue'))
        # Create bar chart
        ax = fig.add_subplot(111)
        ax.set_facecolor('none')
        bars = ax.bar(months, rental_values, color='#002400', alpha=0.7)
        ax.set_title("Yearly Rental Amount", pad=20, fontsize=20, fontweight='bold', color='black')
        ax.set_xlabel("Month", labelpad=10, fontsize=12, color='black')
        ax.set_ylabel("Rental Amount (RM)", labelpad=10, fontsize=12, color='black')
        ax.tick_params(colors='black')
        ax.set_xticks(range(len(months)))
        ax.set_xticklabels(months, rotation=45, ha='right', fontsize=9, color='black')
        ax.grid(True, axis='y', linestyle='--', alpha=0.3, color='black')
        fig.subplots_adjust(left=0.1, right=0.95, bottom=0.2, top=0.9)
        canvas_widget.configure(bg='white')
        canvas.draw()
        # Add export button
        excel_button = Button(
            income_frame,
            text="Export Rental Report",
            font=('Arial', 12, 'bold'),
            bg='green',
            fg='white',
            command=save_to_excel
        )
        excel_button.pack(pady=10)

    def get_overdue_payments():
        connection = sqlite3.connect('govRental.db')
        cursor = connection.cursor()
        try:
            # Modified query to get overdue payments from Payment_Manage table
            cursor.execute("""
                SELECT 
                    pm.Payment_ID,
                    pm.Tenant_ID,
                    pm.Tenant_Name,
                    strftime('%d-%m-%Y', pm.Due_Date) as formatted_date,
                    strftime('%m-%Y', pm.Due_Date) as month_year,
                    pm.Total_Amount,
                    pm.Overdue_Amount,
                    pm.Overdue_Status
                FROM Payment_Manage pm
                WHERE pm.Overdue_Status = 'Yes'
                ORDER BY pm.Due_Date DESC
            """)
            data = cursor.fetchall()
            # Convert to DataFrame with new columns
            df = pd.DataFrame(data, columns=['Payment ID', 'Tenant ID', 'Tenant Username',
                                             'Payment Date', 'Month Year', 'Total Amount',
                                             'Overdue Amount', 'Overdue Status'])
            # Format the amounts
            df['Total Amount'] = df['Total Amount'].apply(lambda x: f"RM {x:,.2f}")
            df['Overdue Amount'] = df['Overdue Amount'].apply(lambda x: f"RM {x:,.2f}")
            # Sort Month Year in descending order and then group
            df['Sort Key'] = pd.to_datetime(df['Month Year'], format='%m-%Y')
            df = df.sort_values('Sort Key', ascending=False)
            df = df.drop(['Sort Key', 'Overdue Status'], axis=1)
            # Group by Month Year
            grouped_df = df.groupby('Month Year', sort=False)
            return grouped_df
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            print(e)
            return None
        finally:
            connection.close()

    def overdue_payments_report():
        # Clear existing widgets in chart frame
        for widget in chart_frame.winfo_children():
            widget.destroy()
        # Create a new frame for overdue payments with full width/height
        overdue_frame = Frame(chart_frame, width=1500, height=800, bg='white')
        overdue_frame.place(x=0, y=0)
        overdue_frame.pack_propagate(False)  # Prevent frame from shrinking
        # Get the grouped overdue payments data
        grouped_df = get_overdue_payments()
        if grouped_df is None or len(grouped_df) == 0:
            message_label = Label(
                overdue_frame,
                text="No overdue payments found.",
                font=('Arial', 14, 'bold'),
                bg='white',
                fg='black'
            )
            message_label.pack(expand=True)
            return
        # Create main title
        title_label = Label(
            overdue_frame,
            text="Overdue Payments Report",
            font=('Arial', 20, 'bold'),
            bg='white',
            fg='black'
        )
        title_label.pack(pady=20)
        # Create container frame for canvas and scrollbar
        container = Frame(overdue_frame, bg='white')
        container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        # Create canvas and scrollbar
        canvas = Canvas(container, bg='white')
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg='white')
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        # Create window inside canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        # Pack canvas and scrollbar
        scrollbar.pack(side=RIGHT, fill=Y)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        # Column widths
        widths = [12, 12, 20, 15, 15, 15]  # Adjusted widths for each column
        headers = ['Payment ID', 'Tenant ID', 'Tenant Username', 'Payment Date', 'Total Amount', 'Overdue Amount']
        # Create tables for each month
        total_overdue = 0
        for month_year, group in grouped_df:
            # Month header
            month_label = Label(
                scrollable_frame,
                text=f"Month: {month_year}",
                font=('Arial', 12, 'bold'),
                bg='white',
                fg='#002400'
            )
            month_label.pack(pady=(20, 10))
            # Create frame for this month's table
            table_frame = Frame(scrollable_frame, bg='white')
            table_frame.pack(fill=X, padx=10)
            # Create headers
            for col, (header, width) in enumerate(zip(headers, widths)):
                Label(
                    table_frame,
                    text=header,
                    font=('Arial', 11, 'bold'),
                    bg='white',
                    width=width
                ).grid(row=0, column=col, padx=5, pady=5)
            # Add data rows
            for row_idx, (_, row) in enumerate(group.iterrows(), 1):
                for col_idx, (value, width) in enumerate(zip(row[headers], widths)):
                    Label(
                        table_frame,
                        text=str(value),
                        font=('Arial', 10),
                        bg='white',
                        width=width
                    ).grid(row=row_idx, column=col_idx, padx=5, pady=2)
            # Add separator
            separator = Frame(scrollable_frame, height=2, bg='grey')
            separator.pack(fill=X, padx=20, pady=10)
            total_overdue += len(group)
        # Add total count label
        total_label = Label(
            overdue_frame,
            text=f"Total Overdue Payments: {total_overdue}",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='black'
        )
        total_label.pack(pady=10)

    def generate_report():
        selection = var.get()
        for widget in chart_frame.winfo_children():
            widget.destroy()
        if selection == "Attendance":
            attendance_report()
        elif selection == "Yearly Income":
            yearly_income_report()
        elif selection == "Overdue Payments":
            overdue_payments_report()

    var = StringVar(value="Attendance")
    report_label = Label(chart_frame, text="Please select and click on generate to view analytic and report.",
                         bg='white',
                         fg='black', font=('Arial', 20, 'bold'))
    report_label.place(relx=0.5, rely=0.5, anchor='center')
    radio_button_font = ('Arial', 15, 'bold')
    radio_attendance = Radiobutton(radio_button_frame, text="Attendance", variable=var, value="Attendance",
                                   font=radio_button_font, command=show_selection)
    radio_yearly_income = Radiobutton(radio_button_frame, text="Yearly Income", variable=var, value="Yearly Income",
                                      font=radio_button_font, command=show_selection)
    radio_overdue_payments = Radiobutton(radio_button_frame, text="Overdue Payments", variable=var,
                                         value="Overdue Payments", font=radio_button_font, command=show_selection)
    generate_button = Button(radio_button_frame, text="Generate", font=radio_button_font, fg="#BBCF8D",
                             bg="#002400",
                             activebackground="white", width=18, command=generate_report)
    generate_button.place(x=50, y=300)
    radio_attendance.place(x=50, y=100)
    radio_yearly_income.place(x=50, y=150)
    radio_overdue_payments.place(x=50, y=200)


def create_tenant_stall_frame():
    # Create a new frame to hold the tenant and stall management UI
    tenant_and_stall_frame = Frame(main_frame)
    tenant_and_stall_frame.place(relwidth=1, relheight=1)
    # Call the function to add tenant and stall management UI to the frame
    add_stall_and_assign_stall(tenant_and_stall_frame)


def add_stall_and_assign_stall(tenant_and_stall):
    global contract_start_date, contract_end_date

    def fetch_tenant_username(event=None):
        tenant_id = tenant_id_entry.get()
        if not tenant_id:
            return
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Tenant_Username FROM Tenant WHERE Tenant_ID = ?", (tenant_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            tenant_username_entry.configure(state='normal')
            tenant_username_entry.delete(0, END)
            tenant_username_entry.insert(0, result[0])
            tenant_username_entry.configure(state='readonly')
        else:
            tenant_username_entry.configure(state='normal')
            tenant_username_entry.delete(0, END)
            tenant_username_entry.configure(state='readonly')

    def search_stalls_by_postcode():
        postcode = search_postcode_entry.get()
        if not postcode:
            print(postcode)
            messagebox.showerror("Error", "Please enter a postcode to search!")
            return
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Stall_ID, Stall_Address FROM Stall WHERE Postcode = ? AND Stall_Status = 0",
                       (postcode,))
        stalls = cursor.fetchall()
        conn.close()
        stall_combobox['values'] = []
        if stalls:
            stall_combobox['values'] = [f"ID: {stall[0]}, Address: {stall[1]}" for stall in stalls]
            messagebox.showinfo("Updates", "Available stalls already shown in the dropbox.")
        else:
            messagebox.showinfo("No Results", "No available stalls found for the given postcode.")

    from datetime import timedelta
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta
    def assign_stall():
        import sys
        if not hasattr(sys.modules[__name__], 'current_agreement_path'):
            messagebox.showerror("Error", "Please generate agreement first")
            return
        selected_stall = stall_combobox.get()
        if not selected_stall:
            messagebox.showerror("Error", "Please select a stall to assign.")
            return
        stall_id = selected_stall.split(",")[0].split(":")[1].strip()
        stall_address = selected_stall.split(",")[1].split(":")[1].strip()
        # Get all form values
        tenant_id = tenant_id_entry.get()
        tenant_username = tenant_username_entry.get()
        rental_period = rental_period_combobox.get()
        rental_amount = rental_amount_entry.get()
        deposit_amount = deposit_entry.get()
        # Convert date string to proper format (YY-MM-DD)
        try:
            payment_date = datetime.strptime(last_payment_entry.get(), '%y-%m-%d')
            last_payment_date = payment_date.strftime('%y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YY-MM-DD format")
            return
        # Parse rental period correctly
        rental_period = rental_period_combobox.get()
        if rental_period == "6 months":
            rental_months = 6
        elif rental_period == "1 year":
            rental_months = 12
        elif rental_period == "2 years":
            rental_months = 24
        else:
            messagebox.showerror("Error", "Invalid rental period selected")
            return
        # Contract start and end dates
        contract_start_date = contract_start_entry.get_date()
        # Calculate contract end date based on rental period
        contract_end_date = contract_start_date + relativedelta(months=rental_months)
        contract_end_date_str = contract_end_date.strftime('%Y-%m-%d')
        contract_end_entry.delete(0, 'end')  # Clear any previous value
        contract_end_entry.insert(0, contract_end_date_str)  # Insert the calculated end date
        contract_end_entry.configure(state='readonly')  # Set to read-only after insertion
        # Reminder date
        reminder_date = reminder_entry.get_date().strftime('%Y-%m-%d')
        reminder_entry.delete(0, 'end')  # Clear any previous value
        reminder_entry.insert(0, reminder_date)  # Insert the reminder date
        reminder_entry.configure(state='readonly')  # Set to read-only after insertion
        # Payment due date (example: set as the contract start date here)
        payment_due_date_str = contract_start_date.strftime('%Y-%m-%d')
        try:
            last_payment_entry.configure(state='normal')  # Set to normal before modification
            last_payment_entry.delete(0, 'end')  # Clear any previous value
            last_payment_entry.insert(0, payment_due_date_str)  # Insert the payment due date
            last_payment_entry.configure(state='readonly')  # Set back to readonly
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set payment due date: {str(e)}")
            return
        # Validate required fields
        if not all([tenant_id, tenant_username, rental_period, rental_amount, deposit_amount, last_payment_date]):
            messagebox.showerror("Error", "All fields are required!")
            return
        # Validate numeric inputs
        try:
            rental_amount_float = float(rental_amount)
            deposit_amount_float = float(deposit_amount)
        except ValueError:
            messagebox.showerror("Error", "Rental amount and deposit amount must be valid numbers.")
            return
        try:
            conn = sqlite3.connect('govRental.db')
            cursor = conn.cursor()
            # Update Stall table
            cursor.execute('''UPDATE Stall 
                            SET Stall_Status = ?,
                                Tenant_ID = ?,
                                Tenant_Username = ?, 
                                Rental_Period = ?,
                                Contract_Start_Date = ?,
                                Contract_End_Date = ?,
                                Rental_Amount = ?,
                                Deposit_Amount = ?,
                                Payment_Due = ?,
                                Contract_Status = ?,
                                Renewal_Status = ?,
                                Reminder_Date = ?
                            WHERE Stall_ID = ?''',
                           (1, tenant_id, tenant_username, rental_period,
                            contract_start_date.strftime('%Y-%m-%d'),
                            contract_end_date_str,
                            rental_amount_float, deposit_amount_float,
                            last_payment_date, 'Active', 0,
                            reminder_date, stall_id))
            if cursor.rowcount == 0:
                raise Exception("No rows were updated in the database.")
            cursor.execute("SELECT Postcode FROM Stall WHERE Stall_ID = ?", (stall_id,))
            postcode = cursor.fetchone()[0]
            # Get the last payment ID
            cursor.execute("SELECT MAX(CAST(SUBSTR(Payment_ID, 4) AS INTEGER)) FROM Payment_Manage")
            last_id = cursor.fetchone()[0]
            next_id = 1 if last_id is None else last_id + 1
            # Insert payment records for each month of the rental period
            for month in range(rental_months):  # This will now correctly iterate for all months
                payment_id = f"PMT{str(next_id).zfill(5)}"
                # Calculate payment due date for each month
                payment_due_date = contract_start_date + relativedelta(months=month, day=8)
                reminder_date_for_month = payment_due_date - relativedelta(days=7)
                try:
                    # Calculate the rental amount for each month
                    monthly_rental_amount = rental_amount_float
                    cursor.execute('''INSERT INTO Payment_Manage (
                        Payment_ID, Payment_Due, Tenant_ID, Tenant_Name, Stall_ID, 
                        Postcode, Rental_Amount, Status, Due_Date, Overdue_Status,
                        Overdue_Amount, Total_Amount, Reminder_Date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                   (payment_id,
                                    payment_due_date.strftime('%Y-%m-%d'),
                                    tenant_id,
                                    tenant_username,
                                    stall_id,
                                    postcode,
                                    monthly_rental_amount,
                                    'Pending',
                                    payment_due_date.strftime('%Y-%m-%d'),
                                    'No',
                                    0,
                                    monthly_rental_amount,
                                    reminder_date_for_month.strftime('%Y-%m-%d')))
                    next_id += 1  # Increment next_id after successful insert
                except sqlite3.IntegrityError as e:
                    if "UNIQUE constraint failed: Payment_Manage.Payment_ID" in str(e):
                        print(f"Duplicate payment_id found: {payment_id}. Incrementing ID and retrying.")
                        next_id += 1  # Increment next_id and retry
                    else:
                        raise
            # Update Tenant table with Stall_ID and Stall_Address
            cursor.execute('''UPDATE Tenant 
                            SET Stall_ID = ?, 
                                Stall_Address = ?
                            WHERE Tenant_ID = ?''',
                           (stall_id, stall_address, tenant_id))
            conn.commit()
            messagebox.showinfo("Success", "Stall assigned to tenant successfully!")
            clear_form()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to assign stall: {str(e)}")
        finally:
            conn.close()

    def update_deposit_amount(event=None):
        try:
            rental_amount = float(rental_amount_entry.get())
            deposit_amount = rental_amount * 1.5  # ori is 2
            deposit_entry.delete(0, END)
            deposit_entry.insert(0, f"{deposit_amount:.2f}")
            deposit_entry.configure(state='readonly')
        except ValueError:
            deposit_entry.delete(0, END)

    def clear_form():
        tenant_id_entry.delete(0, END)
        tenant_username_entry.configure(state='normal')
        tenant_username_entry.delete(0, END)
        tenant_username_entry.configure(state='readonly')
        rental_period_combobox.set("")
        rental_amount_entry.configure(state='normal')
        rental_amount_entry.delete(0, END)
        rental_amount_entry.configure(state='readonly')
        deposit_entry.configure(state='normal')
        deposit_entry.delete(0, END)
        deposit_entry.configure(state='readonly')
        reminder_entry.configure(state='normal')
        reminder_entry.delete(0, END)
        reminder_entry.configure(state='readonly')
        last_payment_entry.set_date(datetime.now().date())
        stall_combobox.set("")

    def add_tenant():
        # Get values from entries
        tenant_ic = tenant_ic_entry.get().strip()
        tenant_username = tenant_username_entry.get().strip()
        temp_password = tenant_ic_entry.get()  # Use IC number as password
        # Validate inputs
        if not tenant_ic or not tenant_username:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        # Check if IC is 12 digits
        if not tenant_ic.isdigit() or len(tenant_ic) != 12:
            messagebox.showerror("Error", "IC number must be exactly 12 digits")
            tenant_ic_entry.delete(0, END)
            return
        try:
            # Connect to database
            conn = sqlite3.connect('govRental.db')
            cursor = conn.cursor()
            # Check if IC already exists
            cursor.execute("SELECT * FROM Tenant WHERE Tenant_IC_Number=?", (tenant_ic,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Tenant with this IC already exists")
                tenant_ic_entry.delete(0, END)
                tenant_username_entry.delete(0, END)
                return
            # Generate username from IC number (last 6 digits)
            username = tenant_username
            # Insert new tenant
            cursor.execute("""
                INSERT INTO Tenant (
                    Tenant_IC_Number,
                    Tenant_Username, 
                    Tenant_Password
                ) VALUES (?, ?, ?)
            """, (tenant_ic, tenant_username, temp_password))
            conn.commit()
            messagebox.showinfo("Success", f"Tenant added successfully!\nUsername: {username}")
            # Clear all entries after successful save
            tenant_ic_entry.delete(0, END)
            tenant_username_entry.delete(0, END)
            pass_entry.configure(state='normal')
            pass_entry.delete(0, END)
            pass_entry.configure(state='readonly')
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
        finally:
            conn.close()

    label_font = ('Arial', 18, 'bold')
    entry_font = ('Arial', 18)
    style = ttk.Style()
    style.configure('TNotebook.Tab', font=('Arial', 18, 'bold'), padding=[20, 10], width=200)
    style.configure('TNotebook', tabposition='n')
    style.map('TNotebook.Tab', foreground=[("selected", "#fd5602")])
    # Notebook widget
    notebook = ttk.Notebook(tenant_and_stall)
    notebook.pack(fill='both', expand=True)  # Use pack instead of place to properly expand
    # Frame for Add Stall tab
    add_stall_frame = Frame(notebook, width=1200, height=1000, bg='mint cream')
    add_stall_frame.pack(fill='both', expand=True)
    add_stall_frame.pack_propagate(False)
    # Frame for Assign Stall tab
    assign_stall_frame = Frame(notebook, width=1200, height=1000, bg='LavenderBlush2')
    assign_stall_frame.pack(fill='both', expand=True)
    assign_stall_frame.pack_propagate(False)
    tenant_register_frame = Frame(notebook, width=1200, height=1000, bg='ivory2')
    tenant_register_frame.pack(fill='both', expand=True)
    notebook.add(add_stall_frame, text="  Add New Stall  ")
    notebook.add(assign_stall_frame, text="  Assign Stall to Tenant  ")
    notebook.add(tenant_register_frame, text="  Register a New Tenant  ")
    # Add Stall Tab
    container_frame = Frame(add_stall_frame, width=1200, height=1000, bg='mint cream')
    container_frame.pack(fill='both', expand=True)
    container_frame.pack_propagate(False)
    add_stall_label1 = Frame(container_frame, bg='mint cream', width=900, height=1080)
    add_stall_label1.place(x=0, y=0)
    add_stall_label2 = Frame(container_frame, bg='mint cream', width=1020, height=1080)
    add_stall_label2.place(x=900, y=0)
    # Add a small tkintermapview here
    map_widget = tkintermapview.TkinterMapView(add_stall_label1, width=800, height=300, corner_radius=0)
    map_widget.set_position(5.4164, 100.3327)  # Set initial position to Penang, Malaysia
    map_widget.set_zoom(10)  # Set initial zoom level
    map_widget.place(x=200, y=50)  # Adjust the x-axis and y-axis
    # Initialize current_marker as None
    current_marker = None

    def set_marker_and_fill_entries(coords):
        nonlocal current_marker  # Use nonlocal to access the outer function's variable
        # coords is a tuple of (latitude, longitude)
        latitude = coords[0]  # Get latitude from tuple
        longitude = coords[1]  # Get longitude from tuple
        # Get address using reverse geocoding
        geolocator = Nominatim(
            user_agent="GovRentalSystem/1.0",
            timeout=10
        )
        try:
            # Add delay to respect rate limits
            time.sleep(1)
            # Get location information
            location = geolocator.reverse((latitude, longitude))
            address = location.address if location else "Address not found"
            # Extract postcode from address using regex
            postcode_match = re.search(r'\b\d{5}\b', address)
            postcode = postcode_match.group(0) if postcode_match else ""
            # Update the entry fields
            latitude_entry.delete(0, END)
            latitude_entry.insert(0, latitude)
            longitude_entry.delete(0, END)
            longitude_entry.insert(0, longitude)
            address_entry.delete("1.0", END)
            address_entry.insert("1.0", address)
            if postcode:
                postcode_entry.delete(0, END)
                postcode_entry.insert(0, postcode)
            # Remove existing marker from the map
            if current_marker:
                try:
                    current_marker.delete()
                except Exception as e:
                    print(f"Error deleting marker: {e}")
            # Add new marker
            current_marker = map_widget.set_marker(
                latitude,
                longitude,
                text=address
            )
        except geopy.exc.GeocoderTimedOut:
            messagebox.showerror("Error", "Geocoding service timed out. Please try again.")
        except geopy.exc.GeocoderUnavailable:
            messagebox.showerror("Error", "Geocoding service unavailable. Please try again later.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    # Add left click command to map
    map_widget.add_left_click_map_command(set_marker_and_fill_entries)
    # Correct the method for adding a right-click command
    map_widget.add_right_click_menu_command(label="Set Marker", command=set_marker_and_fill_entries, pass_coords=True)
    Label(add_stall_label1, text="Stall Address:", font=label_font, bg='mint cream').place(x=200, y=425)
    address_entry = ctk.CTkTextbox(add_stall_label1, width=600, height=100, font=entry_font, wrap=WORD, border_width=1,
                                   border_color='grey')
    address_entry.place(x=200, y=465)  # Add 50 (y-axis)
    Label(add_stall_label1, text="Postcode:", font=label_font, bg='mint cream').place(x=200, y=380)
    postcode_entry = ctk.CTkEntry(add_stall_label1, width=200, font=entry_font)
    postcode_entry.place(x=550, y=380)
    Label(add_stall_label1, text="Latitude:", font=label_font, bg='mint cream').place(x=200, y=600)
    latitude_entry = ctk.CTkEntry(add_stall_label1, width=200, font=entry_font)
    latitude_entry.place(x=550, y=600)
    Label(add_stall_label1, text="Longitude:", font=label_font, bg='mint cream').place(x=200, y=650)
    longitude_entry = ctk.CTkEntry(add_stall_label1, width=200, font=entry_font)
    longitude_entry.place(x=550, y=650)

    def fetch_coordinates():
        address = address_entry.get("1.0", "end-1c").strip()
        if not address:
            messagebox.showerror("Error", "Please enter a valid address.")
            return
        geolocator = Nominatim(user_agent="geoapiExercises")
        try:
            location = geolocator.geocode(address)
            if location:
                latitude_entry.delete(0, END)
                latitude_entry.insert(0, location.latitude)
                longitude_entry.delete(0, END)
                longitude_entry.insert(0, location.longitude)
                # Update marker on map
                set_marker_and_fill_entries((location.latitude, location.longitude))
            else:
                messagebox.showerror("Error", "Unable to fetch coordinates for the given address.")
        except geopy.exc.GeocoderInsufficientPrivileges:
            messagebox.showerror("Error", "Insufficient privileges to access geocoding service.")
        except geopy.exc.GeocoderServiceError as e:
            messagebox.showerror("Error", f"Geocoding service error: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    address_entry.bind("<FocusOut>", lambda event: fetch_coordinates())

    def search_postcode(postcode):
        if not postcode:
            messagebox.showerror("Error", "Please enter a postcode to search!")
            return
        # Create a properly configured Nominatim geocoder
        geolocator = Nominatim(
            user_agent="GovRentalSystem/1.0 (admin@example.com)",  # Unique user agent
            timeout=10
        )
        try:
            # Add delay to respect rate limits
            time.sleep(1)
            # Add more context to the search query
            search_query = f"{postcode}, Penang, Malaysia"
            location = geolocator.geocode(search_query)
            if location:
                # Update map position and marker
                map_widget.set_position(location.latitude, location.longitude)
                map_widget.set_zoom(15)
                set_marker_and_fill_entries((location.latitude, location.longitude))
                # Show success message
                messagebox.showinfo("Success",
                                    f"Location found!\nLatitude: {location.latitude}\nLongitude: {location.longitude}")
            else:
                messagebox.showerror("Error",
                                     "Could not find location for this postcode.\n"
                                     "Please verify the postcode and try again.")
        except geopy.exc.GeocoderTimedOut:
            messagebox.showerror("Error",
                                 "The request timed out.\n"
                                 "Please check your internet connection and try again.")
        except geopy.exc.GeocoderUnavailable:
            messagebox.showerror("Error",
                                 "Geocoding service is currently unavailable.\n"
                                 "Please try again later.")
        except geopy.exc.GeocoderServiceError as e:
            messagebox.showerror("Error",
                                 f"Geocoding service error: {str(e)}\n"
                                 "Please try again later.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    Label(add_stall_label2, text="Stall Image:", font=label_font, bg='mint cream').place(x=250, y=100)

    def upload_image():
        from tkinter import filedialog
        # Get image file
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if (file_path):
            try:
                # Open and resize image
                image = Image.open(file_path)
                image = image.resize((300, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                # Update image label
                image_label.configure(image=photo)
                image_label.image = photo  # Keep a reference
                # Store file path
                upload_image.file_path = file_path  # Store on function instead of frame
                # Change button text
                upload_button.configure(text="Reupload Image")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload image: {str(e)}")

    upload_button = ctk.CTkButton(add_stall_label2, text="Upload Image", command=upload_image,
                                  font=('Arial', 12, 'bold'),
                                  fg_color='#fd5602', hover_color='white')
    # Create vertical container for image label
    image_container = Frame(add_stall_label2, bg='mint cream')
    image_container.place(x=250, y=150)
    upload_button.place(x=400, y=100)
    # Label to display the image
    image_label = Label(image_container, bg='mint cream')
    image_label.pack()
    Label(add_stall_label1, text="Stall Rental (RM):", font=label_font, bg='mint cream').place(x=200, y=700)
    stall_rental_entry = ctk.CTkEntry(add_stall_label1, width=200, font=entry_font)
    stall_rental_entry.place(x=550, y=700)

    def add_stall():
        # Get values from entry fields
        stall_address = address_entry.get("1.0", "end-1c")  # For Text widget
        stall_postcode = postcode_entry.get().strip()
        # Validate postcode format
        if not stall_postcode.isdigit() or len(stall_postcode) != 5:
            messagebox.showerror("Error", "Postcode must be exactly 5 digits")
            return
        # Check if postcode appears in address
        if stall_postcode not in stall_address:
            messagebox.showerror("Error", "Postcode must match the one in stall address")
            return
        stall_rental = stall_rental_entry.get()
        stall_latitude = latitude_entry.get()
        stall_longitude = longitude_entry.get()
        # Validate all fields are filled
        if not all([stall_address, stall_postcode, stall_rental, stall_latitude, stall_longitude]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        # Validate if image was uploaded
        if not hasattr(upload_image, 'file_path'):  # Check function attribute instead of frame
            messagebox.showerror("Error", "Please upload an image")
            return
        try:
            # Connect to database
            conn = sqlite3.connect('govRental.db')
            cursor = conn.cursor()
            # Insert new stall record with all details including latitude and longitude
            cursor.execute("""
                INSERT INTO Stall (Stall_Address, Postcode, Address_Image, Rental_Amount, Latitude, Longitude, Stall_Status)
                VALUES (?, ?, ?, ?, ?, ?, 0)
            """, (stall_address, stall_postcode, upload_image.file_path, stall_rental, stall_latitude, stall_longitude))
            conn.commit()
            cursor.execute("SELECT last_insert_rowid()")
            stall_id = cursor.fetchone()[0]
            messagebox.showinfo("Success", f"Stall details saved successfully! Stall ID: {stall_id}")
            # Clear entry fields
            address_entry.delete("1.0", "end-1c")  # For Text widget
            postcode_entry.delete(0, END)
            stall_rental_entry.delete(0, END)
            latitude_entry.delete(0, END)
            longitude_entry.delete(0, END)
            image_label.configure(image='')
            upload_button.configure(text="Upload Image")
            delattr(upload_image, 'file_path')
            # Clear marker from map
            if current_marker:
                current_marker.delete()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save stall details: {str(e)}")
        finally:
            conn.close()

    add_button = Button(add_stall_label2, text="Add Stall", command=add_stall, font=('Arial', 12, 'bold'), fg='white',
                        bg='#fd5602', activebackground='white', width=20)
    add_button.place(x=250, y=600)
    # Assign Stall Tab - Center elements
    assign_container = Frame(assign_stall_frame, width=1200, height=1000, bg='LavenderBlush2')
    assign_container.pack(fill='both', expand=True)
    assign_container.pack_propagate(False)
    assign_label1 = Frame(assign_container, bg='LavenderBlush2', width=1020, height=1080)
    assign_label1.pack(side=LEFT, fill='both', expand=True)
    assign_label2 = Frame(assign_container, bg='LavenderBlush2', width=900, height=1080)
    assign_label2.pack(side=RIGHT, fill='both', expand=True)
    ctk.CTkLabel(assign_label1, text="Search by Postcode:", font=label_font, bg_color='LavenderBlush2').place(x=250,
                                                                                                              y=50)
    search_postcode_entry = ctk.CTkEntry(assign_label1, width=200, font=entry_font)
    search_postcode_entry.place(x=250, y=85)
    search_postcode_entry.bind('<Return>', lambda event: search_stalls_by_postcode())
    search_icon = "🔍"
    search_button = Button(assign_label1, text=search_icon, command=search_stalls_by_postcode, borderwidth=0,
                           bg='LavenderBlush2', font=('Arial', 16))
    search_button.place(x=460, y=80)

    def show_all_available_stores():
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Stall_ID, Stall_Address FROM Stall WHERE Stall_Status = 0")
        stalls = cursor.fetchall()
        conn.close()
        stall_combobox['values'] = []
        if stalls:
            stall_combobox['values'] = [f"ID: {stall[0]}, Address: {stall[1]}" for stall in stalls]
            messagebox.showinfo("Updates", "All available stalls are shown in the dropbox.")
        else:
            messagebox.showinfo("No Results", "No available stalls found.")

    search_all_button = ctk.CTkButton(assign_label1, text='Show All Available Stalls',
                                      command=show_all_available_stores,
                                      font=('Arial', 14, 'bold'))
    search_all_button.place(x=500, y=85)
    # Define function before using it in button command
    # Create combobox first before defining the function that uses it
    ctk.CTkLabel(assign_label1, text="Available Stalls:", font=label_font, bg_color='LavenderBlush2').place(x=250,
                                                                                                            y=120)
    stall_combobox = ttk.Combobox(assign_label1, width=50, font=entry_font)  # Add readonly state
    stall_combobox.place(x=250, y=160)
    stall_combobox['values'] = []  # Initialize empty values list

    def view_stall_image():
        selected_stall = stall_combobox.get()
        if not selected_stall:
            messagebox.showerror("Error", "Please select a stall first.")
            return
        stall_id = selected_stall.split(",")[0].split(":")[1].strip()
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT Address_Image FROM Stall WHERE Stall_ID = ?", (stall_id,))
            result = cursor.fetchone()
            if result and result[0]:
                image_path = result[0]
                try:
                    img = Image.open(image_path)
                    img.show()
                except FileNotFoundError:
                    messagebox.showerror("Error", "Image file not found.")
            else:
                messagebox.showinfo("No Image", "No image available for this stall.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to retrieve image: {str(e)}")
        finally:
            conn.close()

    view_image_btn = ctk.CTkButton(assign_label1, text="View Stall Image", command=view_stall_image,
                                   font=('Arial', 10, 'bold'))
    view_image_btn.place(x=250, y=210)

    def enable_view_button(*args):
        if stall_combobox.get():
            view_image_btn.configure(state='normal')
        else:
            view_image_btn.configure(state='disabled')

    stall_combobox.bind('<<ComboboxSelected>>', enable_view_button)
    stall_combobox.bind('<KeyRelease>', enable_view_button)
    ctk.CTkLabel(assign_label1, text="Tenant ID:", font=label_font, bg_color='LavenderBlush2').place(x=250, y=250)
    tenant_id_entry = ctk.CTkEntry(assign_label1, width=150, font=entry_font)
    tenant_id_entry.place(x=550, y=250)
    tenant_id_entry.bind("<FocusOut>", fetch_tenant_username)
    ctk.CTkLabel(assign_label1, text="Tenant Username:", font=label_font, bg_color='LavenderBlush2').place(x=250, y=300)
    tenant_username_entry = ctk.CTkEntry(assign_label1, width=150, font=entry_font, state='readonly')
    tenant_username_entry.place(x=550, y=300)
    ctk.CTkLabel(assign_label1, text="Rental Period:", font=label_font, bg_color='LavenderBlush2').place(x=250, y=350)
    rental_period_combobox = ttk.Combobox(assign_label1, values=["6 months", "1 year", "2 years"], width=30,
                                          font=entry_font)
    rental_period_combobox.place(x=550, y=350)

    def update_contract_dates(event=None):
        from dateutil.relativedelta import relativedelta
        rental_period = rental_period_combobox.get()
        if rental_period:
            start_date = contract_start_entry.get_date()
            # Calculate months to add based on rental period
            if rental_period == "6 months":
                months = 6
            elif rental_period == "1 year":
                months = 12
            else:  # 2 years
                months = 24
            # Calculate end date by adding months to start date
            end_date = start_date + relativedelta(months=months)
            contract_end_entry.set_date(end_date)

    # Update end date when rental period changes
    rental_period_combobox.bind("<<ComboboxSelected>>", update_contract_dates)
    ctk.CTkLabel(assign_label1, text="Contract Start Date:", font=label_font, bg_color='LavenderBlush2').place(x=250,
                                                                                                               y=400)
    contract_start_entry = DateEntry(assign_label1, width=27, background='navy', foreground='white', borderwidth=2,
                                     font=entry_font, date_pattern='yy-mm-dd')
    contract_start_entry.place(x=550, y=400)

    # Update end date whenever start date or rental period changes
    def auto_update_dates(*args):
        if not rental_period_combobox.get():
            return
        from dateutil.relativedelta import relativedelta
        start_date = contract_start_entry.get_date()
        # Calculate months based on rental period
        rental_period = rental_period_combobox.get()
        if rental_period == "6 months":
            months = 6
        elif rental_period == "1 year":
            months = 12
        else:  # 2 years
            months = 24
        # Calculate and set end date
        end_date = start_date + relativedelta(months=months)
        contract_end_entry.set_date(end_date)

    # Bind auto update to both start date and rental period changes
    contract_start_entry.bind("<<DateEntrySelected>>", auto_update_dates)
    contract_start_entry.bind("<KeyRelease>", auto_update_dates)
    contract_start_entry.bind("<FocusOut>", auto_update_dates)
    rental_period_combobox.bind("<<ComboboxSelected>>", auto_update_dates)
    ctk.CTkLabel(assign_label1, text="Contract End Date:", font=label_font, bg_color='LavenderBlush2').place(x=250,
                                                                                                             y=450)
    contract_end_entry = DateEntry(assign_label1, width=27, background='navy', foreground='white', borderwidth=2,
                                   font=entry_font, state='readonly', date_pattern='yy-mm-dd')  # Made end date readonly
    contract_end_entry.place(x=550, y=450)
    ctk.CTkLabel(assign_label1, text="Rental Amount (RM):", font=label_font, bg_color='LavenderBlush2').place(x=250,
                                                                                                              y=500)
    rental_amount_entry = ctk.CTkEntry(assign_label1, width=300, font=entry_font, state='readonly')
    rental_amount_entry.place(x=550, y=500)

    def update_rental():
        if update_rental_button.cget("text") == "Update Rental":
            rental_amount_entry.configure(state='normal')
            update_rental_button.configure(text="Save Changes")
        else:
            try:
                new_amount = float(rental_amount_entry.get())
                selected_stall = stall_combobox.get()
                if selected_stall:
                    stall_id = selected_stall.split(",")[0].split(":")[1].strip()
                    conn = sqlite3.connect('govRental.db')
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Stall SET Rental_Amount = ? WHERE Stall_ID = ?", (new_amount, stall_id))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", "Rental amount updated successfully!")
                    rental_amount_entry.configure(state='readonly')
                    update_rental_button.configure(text="Update Rental")
                    # Update deposit and total amounts
                    update_all_amounts(new_amount)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number for rental amount")
                rental_amount_entry.delete(0, END)
                rental_amount_entry.focus()

    update_rental_button = Button(assign_label1, text="Update Rental", font=('Arial', 10, 'bold'),
                                  activebackground='#fd5602', command=update_rental)
    update_rental_button.place(x=140, y=500)

    def update_all_amounts(rental_amount):
        # Update rental amount
        rental_amount_entry.configure(state='normal')
        rental_amount_entry.delete(0, END)
        rental_amount_entry.insert(0, str(rental_amount))
        rental_amount_entry.configure(state='readonly')
        # Update deposit amount (1.5 times rental)
        deposit = rental_amount * 1.5
        deposit_entry.configure(state='normal')
        deposit_entry.delete(0, END)
        deposit_entry.insert(0, str(deposit))
        deposit_entry.configure(state='readonly')
        # Update total amount
        total = rental_amount + deposit
        total_entry.configure(state='normal')
        total_entry.delete(0, END)
        total_entry.insert(0, str(total))
        total_entry.configure(state='readonly')
        # Save total amount to database
        selected_stall = stall_combobox.get()
        if selected_stall:
            stall_id = selected_stall.split(",")[0].split(":")[1].strip()
            conn = sqlite3.connect('govRental.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE Stall SET Total_Amount = ? WHERE Stall_ID = ?", (total, stall_id))
            conn.commit()
            conn.close()

    # Fetch rental amount when stall is selected
    def update_rental_amount(event=None):
        selected_stall = stall_combobox.get()
        if selected_stall:
            stall_id = selected_stall.split(",")[0].split(":")[1].strip()
            conn = sqlite3.connect('govRental.db')
            cursor = conn.cursor()
            cursor.execute("SELECT Rental_Amount FROM Stall WHERE Stall_ID = ?", (stall_id,))
            result = cursor.fetchone()
            conn.close()
            if result:
                rental_amount = float(result[0])
                update_all_amounts(rental_amount)

    stall_combobox.bind('<<ComboboxSelected>>', update_rental_amount)
    ctk.CTkLabel(assign_label1, text="Deposit Amount (RM):", font=label_font, bg_color='LavenderBlush2').place(x=250,
                                                                                                               y=550)
    deposit_entry = ctk.CTkEntry(assign_label1, width=300, font=entry_font, state='readonly')
    deposit_entry.place(x=550, y=550)
    ctk.CTkLabel(assign_label1, text="Total Amount (RM):", font=label_font, bg_color='LavenderBlush2').place(x=250,
                                                                                                             y=600)
    total_entry = ctk.CTkEntry(assign_label1, width=300, font=entry_font, state='readonly')
    total_entry.place(x=550, y=600)
    # Payment by date
    ctk.CTkLabel(assign_label1, text="Payment due by:", font=label_font, bg_color='LavenderBlush2').place(x=250, y=650)
    last_payment_entry = DateEntry(assign_label1, width=27, background='darkblue', foreground='white', borderwidth=2,
                                   font=entry_font, calendar_position='above', mindate=datetime.now(),
                                   date_pattern='yy-mm-dd')
    last_payment_entry.place(x=550, y=650)

    # Update payment due date when contract start date changes
    def update_payment_due_date(*args):
        start_date = contract_start_entry.get_date()
        # Set payment due date to 7 days after the start date
        payment_due_date = start_date + timedelta(days=7)
        # Update the last payment entry with the calculated payment due date
        last_payment_entry.set_date(payment_due_date)
        # Update reminder date whenever payment due date changes
        reminder_date = payment_due_date - timedelta(days=3)
        reminder_entry.set_date(reminder_date)
        reminder_entry.configure(state='readonly')

    contract_start_entry.bind('<<DateEntrySelected>>', update_payment_due_date)
    # Reminder date
    ctk.CTkLabel(assign_label1, text="Reminder Date:", font=label_font, bg_color='LavenderBlush2').place(x=250, y=700)
    reminder_entry = DateEntry(assign_label1, width=27, background='darkblue', foreground='white', borderwidth=2,
                               font=entry_font, calendar_position='above', mindate=datetime.now(),
                               date_pattern='yy-mm-dd')  # Set date format to yyyy-mm-dd
    reminder_entry.place(x=550, y=700)

    # Update reminder date when payment due date changes
    def update_reminder_date(*args):
        payment_due = last_payment_entry.get_date()
        reminder_date = payment_due - timedelta(days=3)
        reminder_entry.set_date(reminder_date)
        reminder_entry.configure(state='readonly')

    # Bind to both DateEntrySelected and when payment due date is updated
    last_payment_entry.bind('<<DateEntrySelected>>', update_reminder_date)
    # Initial updates
    update_payment_due_date()  # This will also update the reminder date
    ctk.CTkLabel(assign_label2, text="Contract Agreement:", font=label_font, bg_color='LavenderBlush2').place(x=250,
                                                                                                              y=50)
    # Create a frame to show agreement preview
    agreement_preview_frame = Frame(assign_label2, bg='mint cream')
    agreement_preview_frame.place(x=100, y=100)
    # Create scrollable text widget for preview
    preview_text = Text(agreement_preview_frame, wrap=WORD, font=("Helvetica", 12), width=80, height=30)
    preview_text.pack(fill=BOTH, expand=True)

    def generate_agreement():
        # Verify all fields are filled
        if not all([stall_combobox.get(), tenant_id_entry.get(), tenant_username_entry.get(),
                    rental_period_combobox.get(), rental_amount_entry.get(), deposit_entry.get()]):
            messagebox.showerror("Error", "Please fill in all required fields before generating agreement")
            return
        # Set all entry fields and comboboxes to readonly state
        search_postcode_entry.configure(state='disabled')
        stall_combobox.configure(state='disabled')
        tenant_id_entry.configure(state='disabled')
        rental_period_combobox.configure(state='disabled')
        contract_start_entry.configure(state='disabled')
        last_payment_entry.configure(state='disabled')
        update_rental_button.configure(state='disabled')
        contract_end_entry.configure(state='disabled')  # Disable contract end date
        reminder_entry.configure(state='disabled')  # Disable reminder date
        # Clear previous content
        preview_text.delete(1.0, END)
        # Get all the entered details
        stall_details = stall_combobox.get().split(",")
        stall_id = stall_details[0].split(":")[1].strip()
        stall_address = stall_combobox.get().split(":", 2)[2].strip()
        tenant_id = tenant_id_entry.get()
        tenant_username = tenant_username_entry.get()
        rental_period = rental_period_combobox.get()
        start_date = contract_start_entry.get_date()
        end_date = contract_end_entry.get_date()
        rental_amount = rental_amount_entry.get()
        deposit = deposit_entry.get()
        # Fetch tenant IC from database
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Tenant_IC_Number FROM Tenant WHERE Tenant_Username = ?", (tenant_username,))
        tenant_ic = cursor.fetchone()[0]
        conn.close()
        # Insert agreement content for preview
        preview_text.insert(END, "RENTAL AGREEMENT\n\n", "title")
        preview_text.insert(END, f"Tenant Name: {tenant_username}\n")
        preview_text.insert(END, f"Tenant IC: {tenant_ic}\n")
        preview_text.insert(END, f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n")
        preview_text.insert(END, f"Stall ID: {stall_id}\n")
        preview_text.insert(END, f"Stall Address: {stall_address}\n")
        preview_text.insert(END, f"Tenant ID: {tenant_id}\n")
        preview_text.insert(END, f"Tenant Name: {tenant_username}\n")
        preview_text.insert(END, f"Rental Period: {rental_period}\n")
        preview_text.insert(END, f"Contract Start Date: {start_date}\n")
        preview_text.insert(END, f"Contract End Date: {end_date}\n")
        preview_text.insert(END, f"Monthly Rental Amount: RM {rental_amount}\n")
        preview_text.insert(END, f"Security Deposit: RM {deposit}\n")
        preview_text.insert(END, f"Total Amount: RM {total_entry.get()}\n")
        preview_text.insert(END, f"\n\nPlease paid by: {last_payment_entry.get_date()}\n\n", "bold_red")
        # Get current logged in admin info
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Admin_ID, Admin_Name FROM Admin WHERE Admin_IC_Number = ?", (admin_ic,))
        admin = cursor.fetchone()
        conn.close()
        if admin:
            preview_text.insert(END, f"Admin ID: {admin[0]} | Admin Name: {admin[1]} \n")
        # Fetch and insert business information
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Business_Name, Licence_No, Business_Hours, Location, Contact_No, Email_Address FROM Business_Information")
        business_info = cursor.fetchone()
        conn.close()
        if business_info:
            preview_text.insert(END, f"\n{business_info[0]}\n")
            preview_text.insert(END, f"License No: {business_info[1]}\n")
            preview_text.insert(END, f"{business_info[2]}\n")
            preview_text.insert(END, f"{business_info[3]}\n")
            preview_text.insert(END, f"Contact No: {business_info[4]}, Email: {business_info[5]}\n")
        # Configure text styles
        preview_text.tag_configure("title", font=("Helvetica", 16, "bold"))
        preview_text.tag_configure("bold_red", font=("Helvetica", 12, "bold"), foreground="red")
        preview_text.config(state=DISABLED)
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            # Generate PDF file path
            pdf_path = f"{tenant_username}_{tenant_id}_{start_date}.pdf"
            # Store the PDF path as a global variable
            global current_agreement_path
            current_agreement_path = pdf_path
            # Create PDF
            c = canvas.Canvas(pdf_path, pagesize=letter)
            # First page content
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, 750, "RENTAL AGREEMENT")
            c.setFont("Helvetica", 12)
            c.drawString(50, 720, f"Tenant Name: {tenant_username}")
            c.drawString(50, 700, f"Tenant IC: {tenant_ic}")
            c.drawString(50, 680, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
            # Main content
            c.drawString(50, 640, f"Stall ID: {stall_id}")
            c.drawString(50, 620, f"Stall Address: {stall_address}")
            c.drawString(50, 600, f"Tenant ID: {tenant_id}")
            c.drawString(50, 580, f"Rental Period: {rental_period}")
            c.drawString(50, 560, f"Contract Start Date: {start_date}")
            c.drawString(50, 540, f"Contract End Date: {end_date}")
            # Financial details
            y_pos = 520
            for text in [
                f"Monthly Rental Amount: RM {rental_amount}",
                f"Security Deposit: RM {deposit}",
                f"Total Amount: RM {total_entry.get()}",
                f"Contract Status: Active",
                f"Please paid by: {last_payment_entry.get_date()}"
            ]:
                c.drawString(50, y_pos, text)
                y_pos -= 20
            # Admin and business info
            if admin:
                y_pos -= 20
                c.drawString(50, y_pos, f"Admin ID: {admin[0]}, Admin Name: {admin[1]}")
                c.drawString(50, y_pos - 20, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
            if business_info:
                y_pos -= 60
                for text in [
                    f"{business_info[0]}",
                    f"License No: {business_info[1]}",
                    f"{business_info[2]}",
                    f"{business_info[3]}",
                    f"Contact No: {business_info[4]}, Email: {business_info[5]}"
                ]:
                    c.drawString(50, y_pos, text)
                    y_pos -= 20
            # Second page - Terms & Conditions
            c.showPage()
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, 750, "Terms & Conditions")
            c.setFont("Helvetica", 12)
            y = 700
            line_height = 20
            penalty = float(rental_amount) * 0.3
            terms = [
                f"Monthly rental of RM{rental_amount} is due at 8th of each month.",
                f"Late payments will incur a 30% penalty, amounting to RM{penalty:.2f}.",
                f"The rental period begins on {start_date} and ends on {end_date} for an initial term of {rental_period}.",
                "The Tenant cannot assign, transfer, or sublet the stall to others.",
                "The Tenant is responsible for maintaining cleanliness and repairing any damages caused.",
                "The Landlord may inspect the stall with prior notice to ensure compliance.",
                "Upon termination or expiration, the Tenant must return the stall in its original condition, considering normal wear and tear.",
                "Cleaning or repair costs will be deducted from the security deposit.",
                "Breaching any terms, including subletting or unauthorized activities, may result in immediate termination of the Agreement.",
                "Following termination for breach, the Tenant will be banned from renting government stalls in the future.",
                "This Agreement supersedes any prior agreements and can only be amended in writing and signed by both parties."
            ]
            # Add terms with word wrapping
            for term in terms:
                words = term.split()
                line = ''
                for word in words:
                    test_line = line + word + ' '
                    if len(test_line) * 6 > 500:
                        c.drawString(50, y, line)
                        y -= line_height
                        line = word + ' '
                    else:
                        line = test_line
                c.drawString(50, y, line)
                y -= line_height * 1.5
            # Add stamp image
            try:
                from reportlab.lib.utils import ImageReader
                import os
                current_dir = os.path.dirname(os.path.abspath(__file__))
                image_path = os.path.join(current_dir, "images", "Gov_Agreement_Stamp.png")
                if os.path.exists(image_path):
                    img = ImageReader(image_path)
                    img_width = 200
                    img_height = 200
                    x = (letter[0] - img_width) / 2
                    c.drawImage(img, x, y - 20, width=img_width, height=img_height)
            except Exception as e:
                print(f"Could not add image: {str(e)}")
            c.save()
            print("Agreement preview generated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate agreement: {str(e)}")
        # Store tenant_id, tenant_username, and stall_id as global variables
        global generated_tenant_id, generated_tenant_username, generated_stall_id
        generated_tenant_id = tenant_id
        generated_tenant_username = tenant_username
        generated_stall_id = stall_id

    agreement_button = ctk.CTkButton(assign_label2, text="Preview Agreement", font=('Arial', 12, 'bold'),
                                     command=generate_agreement)
    agreement_button.place(x=500, y=50)

    # Modify assign_stall function to save agreement path
    def assign_stall():
        import sys
        if not hasattr(sys.modules[__name__], 'current_agreement_path'):
            messagebox.showerror("Error", "Please preview agreement first. ")
            return
        selected_stall = stall_combobox.get()
        if not selected_stall:
            messagebox.showerror("Error", "Please select a stall to assign.")
            return
        stall_id = selected_stall.split(",")[0].split(":")[1].strip()
        stall_address = selected_stall.split(",")[1].split(":")[1].strip()
        # Get all form values
        tenant_id = tenant_id_entry.get()
        tenant_username = tenant_username_entry.get()
        rental_period = rental_period_combobox.get()
        rental_amount = rental_amount_entry.get()
        deposit_amount = deposit_entry.get()
        # Convert date string to proper format (YY-MM-DD)
        try:
            payment_date = datetime.strptime(last_payment_entry.get(), '%y-%m-%d')
            last_payment_date = payment_date.strftime('%y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YY-MM-DD format")
            return
        # Parse rental period correctly
        rental_period = rental_period_combobox.get()
        if rental_period == "6 months":
            rental_months = 6
        elif rental_period == "1 year":
            rental_months = 12
        elif rental_period == "2 years":
            rental_months = 24
        else:
            messagebox.showerror("Error", "Invalid rental period selected")
            return
        # Contract start and end dates
        contract_start_date = contract_start_entry.get_date()
        # Calculate contract end date based on rental period
        contract_end_date = contract_start_date + relativedelta(months=rental_months)
        contract_end_date_str = contract_end_date.strftime('%Y-%m-%d')
        contract_end_entry.delete(0, 'end')  # Clear any previous value
        contract_end_entry.insert(0, contract_end_date_str)  # Insert the calculated end date
        contract_end_entry.configure(state='readonly')  # Set to read-only after insertion
        # Reminder date
        reminder_date = reminder_entry.get_date().strftime('%Y-%m-%d')
        reminder_entry.delete(0, 'end')  # Clear any previous value
        reminder_entry.insert(0, reminder_date)  # Insert the reminder date
        reminder_entry.configure(state='readonly')  # Set to read-only after insertion
        # Payment due date (example: set as the contract start date here)
        payment_due_date_str = contract_start_date.strftime('%Y-%m-%d')
        try:
            last_payment_entry.configure(state='normal')  # Set to normal before modification
            last_payment_entry.delete(0, 'end')  # Clear any previous value
            last_payment_entry.insert(0, payment_due_date_str)  # Insert the payment due date
            last_payment_entry.configure(state='readonly')  # Set back to readonly
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set payment due date: {str(e)}")
            return
        # Validate required fields
        if not all([tenant_id, tenant_username, rental_period, rental_amount, deposit_amount, last_payment_date]):
            messagebox.showerror("Error", "All fields are required!")
            return
        # Validate numeric inputs
        try:
            rental_amount_float = float(rental_amount)
            deposit_amount_float = float(deposit_amount)
        except ValueError:
            messagebox.showerror("Error", "Rental amount and deposit amount must be valid numbers.")
            return
        try:
            conn = sqlite3.connect('govRental.db')
            cursor = conn.cursor()
            # Update Stall table
            cursor.execute('''UPDATE Stall 
                            SET Stall_Status = ?,
                                Tenant_ID = ?,
                                Tenant_Username = ?, 
                                Rental_Period = ?,
                                Contract_Start_Date = ?,
                                Contract_End_Date = ?,
                                Rental_Amount = ?,
                                Deposit_Amount = ?,
                                Payment_Due = ?,
                                Contract_Status = ?,
                                Renewal_Status = ?,
                                Reminder_Date = ?,
                                Contract_File = ?
                            WHERE Stall_ID = ?''',
                           (1, tenant_id, tenant_username, rental_period,
                            contract_start_date.strftime('%Y-%m-%d'),
                            contract_end_date_str,
                            rental_amount_float, deposit_amount_float,
                            last_payment_date, 'Active', 0,
                            reminder_date, current_agreement_path, stall_id))
            if cursor.rowcount == 0:
                raise Exception("No rows were updated in the database.")
            cursor.execute("SELECT Postcode FROM Stall WHERE Stall_ID = ?", (stall_id,))
            postcode = cursor.fetchone()[0]
            # Get the last payment ID
            cursor.execute("SELECT MAX(CAST(SUBSTR(Payment_ID, 4) AS INTEGER)) FROM Payment_Manage")
            last_id = cursor.fetchone()[0]
            next_id = 1 if last_id is None else last_id + 1
            # Insert payment records for each month of the rental period
            # Generate payment records for each month
            for month in range(rental_months):
                payment_id = f"PMT{str(next_id).zfill(5)}"
                # Calculate payment due date for each month
                payment_due_date = contract_start_date + relativedelta(months=month, day=8)
                reminder_date_for_month = payment_due_date - relativedelta(days=7)
                # Keep trying until we successfully insert with a unique payment ID
                while True:
                    try:
                        # Insert payment record
                        cursor.execute('''INSERT INTO Payment_Manage (
                            Payment_ID, Payment_Due, Tenant_ID, Tenant_Name, Stall_ID,
                            Postcode, Rental_Amount, Status, Due_Date, Overdue_Status, 
                            Overdue_Amount, Total_Amount, Reminder_Date
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                       (payment_id,
                                        payment_due_date.strftime('%Y-%m-%d'),
                                        tenant_id,
                                        tenant_username,
                                        stall_id,
                                        postcode,
                                        rental_amount_float,
                                        'Pending',
                                        payment_due_date.strftime('%Y-%m-%d'),
                                        'No',
                                        0,
                                        rental_amount_float,
                                        reminder_date_for_month.strftime('%Y-%m-%d')))
                        # If insert succeeds, increment ID and break loop
                        next_id += 1
                        break
                    except sqlite3.IntegrityError as e:
                        if "UNIQUE constraint failed: Payment_Manage.Payment_ID" in str(e):
                            # If duplicate ID found, increment and try again with new ID
                            next_id += 1
                            payment_id = f"PMT{str(next_id).zfill(5)}"
                        else:
                            raise e
                    except sqlite3.Error as e:
                        # Log any other database errors
                        print(f"Error inserting payment record: {str(e)}")
                        raise e
            # Update Tenant table with Stall_ID and Stall_Address
            cursor.execute('''UPDATE Tenant 
                            SET Stall_ID = ?, 
                                Stall_Address = ?
                            WHERE Tenant_ID = ?''',
                           (stall_id, stall_address, tenant_id))
            conn.commit()
            messagebox.showinfo("Success", "Stall assigned to tenant successfully!")
            # Open the generated agreement PDF
            try:
                os.startfile(current_agreement_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open agreement PDF: {str(e)}")
            clear_form()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to assign stall: {str(e)}")
        finally:
            conn.close()

    assign_button = Button(assign_label2, text="Assign Stall", command=assign_stall, font=('Arial', 16, 'bold'),
                           fg='white', bg='#fd5602', activebackground='white')
    assign_button.place(x=450, y=760)
    # Tenant Register Tab - Center elements
    register_container = Frame(tenant_register_frame, width=1200, height=1000, bg='ivory2')
    register_container.pack(fill='both', expand=True)
    register_container.pack_propagate(False)
    # Add authentication image
    auth_image = Image.open(r"C:/Kai_Shuang/vennis2.jpg")
    auth_image = auth_image.resize((250, 250), Image.Resampling.LANCZOS)  # Resize to reasonable dimensions
    auth_photo = ImageTk.PhotoImage(auth_image)
    auth_label = Label(register_container, image=auth_photo, bg='ivory2')
    auth_label.image = auth_photo  # Keep a reference to prevent garbage collection
    auth_label.pack(pady=(50, 0))
    ic_frame = Frame(register_container, bg='ivory2')
    ic_frame.pack(pady=(150, 0))
    Label(ic_frame, text="Tenant IC Number: ", font=label_font, anchor='w', bg='ivory2').pack(side=LEFT, padx=5)
    tenant_ic_entry = ctk.CTkEntry(ic_frame, width=300, font=entry_font)
    tenant_ic_entry.pack(side=LEFT)
    name_frame = Frame(register_container, bg='ivory2')
    name_frame.pack(pady=20)
    Label(name_frame, text="Tenant Name:", font=label_font, anchor='w', bg='ivory2').pack(side=LEFT, padx=5)
    tenant_username_entry = ctk.CTkEntry(name_frame, width=300, font=entry_font)
    tenant_username_entry.pack(side=LEFT)
    shining_label = Label(register_container,
                          text="* * * Temporary Password for every tenant is set refer to their IC Number. * * *",
                          font=('Arial', 12, 'italic', 'bold'), fg='blue', bg='ivory2')
    shining_label.pack(pady=5)

    def shine():
        colors = ['blue', 'navy', 'royal blue', 'dodger blue']
        current_color = shining_label.cget('fg')
        next_color = colors[(colors.index(current_color) + 1) % len(colors)]
        shining_label.config(fg=next_color)
        register_container.after(500, shine)

    shine()
    pass_frame = Frame(register_container, bg='ivory2')
    pass_frame.pack(pady=20)
    Label(pass_frame, text="Temporary Password :", font=label_font, anchor='w', bg='ivory2').pack(side=LEFT, padx=5)
    pass_entry = ctk.CTkEntry(pass_frame, width=300, font=entry_font, state='normal')
    pass_entry.pack(side=LEFT)

    def update_password(*args):
        ic = tenant_ic_entry.get()
        pass_entry.configure(state='normal')
        pass_entry.delete(0, 'end')
        pass_entry.insert(0, ic)
        pass_entry.configure(state='readonly')

    tenant_ic_entry.bind('<KeyRelease>', update_password)
    add_button = ctk.CTkButton(register_container, text="Register New Tenant", command=add_tenant,
                               font=('Arial', 12, 'bold'), fg_color='#fd5602',
                               hover_color='#db4a02', width=200)
    add_button.pack(pady=20)
    # change Tenant database to Null for others except Tenant_IC_Number, Tenant_Username, Password


def payment_management():
    payment_manage_frame = Frame(main_frame)
    payment_manage_frame.place(relwidth=1, relheight=1)

    def search_payments():
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()
        # Clear existing items in treeview
        for item in transaction_tree.get_children():
            transaction_tree.delete(item)
        try:
            # Query payments within date range with calculated fields
            cursor.execute("""
            SELECT Payment_ID, Tenant_ID, Tenant_Name, Transaction_Date, 
                   Rental_Amount, Status, Overdue_Status, Overdue_Amount, Total_Amount
            FROM Payment_Manage
            WHERE Transaction_Date BETWEEN ? AND ?
            """, (start_date, end_date))
            payments = cursor.fetchall()
            # Insert payments into treeview
            for payment in payments:
                transaction_tree.insert('', 'end', values=payment)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    def load_all_payments():
        # Clear existing items in treeview
        for item in transaction_tree.get_children():
            transaction_tree.delete(item)
        try:
            # Query all payments with calculated fields
            cursor.execute("""
            SELECT Payment_ID, Tenant_ID, Tenant_Name, Transaction_Date, 
                   Rental_Amount, Status, Overdue_Status, Overdue_Amount, Total_Amount
            FROM Payment_Manage
        """)
            payments = cursor.fetchall()
            # Insert payments into treeview
            for payment in payments:
                transaction_tree.insert('', 'end', values=payment)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    def view_monthly_payments():
        # Clear existing items in treeview
        for item in transaction_tree.get_children():
            transaction_tree.delete(item)
        try:
            # Query payments grouped by month with calculated fields
            cursor.execute("""
            SELECT Payment_ID, Tenant_ID, Tenant_Name, Transaction_Date, 
                   Rental_Amount, Status, Overdue_Status, Overdue_Amount, Total_Amount
            FROM Payment_Manage
            ORDER BY strftime('%Y-%m', Transaction_Date)
            """)
            payments = cursor.fetchall()
            # Insert payments into treeview
            for payment in payments:
                transaction_tree.insert('', 'end', values=payment)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    Label(payment_manage_frame, text="Admin- Payment Management", fg='black', font=("Arial", 35, "bold")).place(x=650,
                                                                                                                y=30)

    # Define font for labels
    font = ("Arial", 14, "bold")
    notebook = ttk.Notebook(payment_manage_frame)
    notebook.place(x=0, y=100, width=1920, height=930)
    # Create Transaction History tab
    transaction_frame = Frame(notebook, bg='mint cream')
    notebook.add(transaction_frame, text='  Payment Management', padding=10)
    style = ttk.Style()
    style.configure('TNotebook.Tab', font=('Arial', 16, 'bold'))
    # Configure notebook tab width and selected color
    style.configure('TNotebook', tabposition='n', width=1920)
    style.configure('TNotebook.Tab', width=960)  # Split width evenly between 2 tabs
    style.map('TNotebook.Tab', foreground=[('selected', '#fd5602')])
    # Create Overdue Payments tab
    overdue_frame = Frame(notebook, bg='mint cream')
    notebook.add(overdue_frame, text='  Overdue Management', padding=10)
    # Add date selection and search to Transaction History tab
    date_frame = Frame(transaction_frame, bg='mint cream')
    date_frame.pack(pady=10, fill=X)  # Added fill=X to make frame expand horizontally
    # Label for Start Date
    start_date_label = Label(date_frame, text="Start Date:", font=("Arial", 14, "bold"), bg='mint cream')
    start_date_label.pack(side=LEFT, padx=15)  # Changed to pack layout
    # Date Entry for Start Date
    start_date_entry = DateEntry(date_frame, font=font, width=12, background='darkblue', foreground='white',
                                 date_pattern='yyyy-mm-dd')
    start_date_entry.pack(side=LEFT, padx=15)  # Changed to pack layout
    # Label for End Date
    end_date_label = Label(date_frame, text="End Date:", font=("Arial", 14, "bold"), bg='mint cream')
    end_date_label.pack(side=LEFT, padx=15)  # Changed to pack layout
    # Date Entry for End Date
    end_date_entry = DateEntry(date_frame, font=font, width=12, background='darkblue', foreground='white',
                               date_pattern='yyyy-mm-dd')
    end_date_entry.pack(side=LEFT, padx=15)  # Changed to pack layout
    # Search Button
    search_button = ttk.Button(date_frame, text="Search",
                               command=lambda: search_payments(start_date_entry.get(), end_date_entry.get()),
                               style="TButton")

    style = ttk.Style()
    style.configure("TButton", font=font)
    search_button.pack(side=LEFT, padx=15)  # Changed to pack layout

    # Function to search payments between dates
    def search_payments(start_date, end_date):
        # Clear existing items in treeview
        for item in transaction_tree.get_children():
            transaction_tree.delete(item)
        try:
            # Query payments between selected dates
            cursor.execute("""
            SELECT Payment_ID, Tenant_ID, Tenant_Name, Transaction_Date, 
                   Rental_Amount, Status, Overdue_Status, Overdue_Amount, Total_Amount
            FROM Payment_Manage
                WHERE DATE(Transaction_Date) BETWEEN ? AND ?
            """, (start_date, end_date))
            payments = cursor.fetchall()
            # Insert filtered payments into treeview
            for payment in payments:
                transaction_tree.insert('', 'end', values=payment)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    # Create Treeview for Transaction History
    transaction_tree = ttk.Treeview(transaction_frame, columns=(
        "Payment ID", "Tenant ID", "Tenant Name", "Date", "Amount", "Status", "Overdue Status", "Overdue Amount",
        "Total Amount"), show="headings", height=20)
    # Configure Transaction History columns with center alignment
    # Configure column headings
    transaction_tree.heading("Payment ID", text="Payment ID", anchor=CENTER)
    transaction_tree.heading("Tenant ID", text="Tenant ID", anchor=CENTER)
    transaction_tree.heading("Tenant Name", text="Tenant Name", anchor=CENTER)
    transaction_tree.heading("Date", text="Date", anchor=CENTER)
    transaction_tree.heading("Amount", text="Amount", anchor=CENTER)
    transaction_tree.heading("Status", text="Status", anchor=CENTER)
    transaction_tree.heading("Overdue Status", text="Overdue", anchor=CENTER)
    transaction_tree.heading("Overdue Amount", text="Penalty", anchor=CENTER)
    transaction_tree.heading("Total Amount", text="Total", anchor=CENTER)
    # Configure column widths and center alignment
    transaction_tree.column("Payment ID", width=120, anchor=CENTER)
    transaction_tree.column("Tenant ID", width=120, anchor=CENTER)
    transaction_tree.column("Tenant Name", width=150, anchor=CENTER)
    transaction_tree.column("Date", width=150, anchor=CENTER)
    transaction_tree.column("Amount", width=120, anchor=CENTER)
    transaction_tree.column("Status", width=120, anchor=CENTER)
    transaction_tree.column("Overdue Status", width=120, anchor=CENTER)
    transaction_tree.column("Overdue Amount", width=120, anchor=CENTER)
    transaction_tree.column("Total Amount", width=120, anchor=CENTER)
    # Fetch and display data
    for item in transaction_tree.get_children():
        transaction_tree.delete(item)
    try:
        cursor.execute("""
            SELECT Payment_ID, Tenant_ID, Tenant_Name, Transaction_Date, 
                   Rental_Amount, Status, Overdue_Status, Overdue_Amount, Total_Amount
            FROM Payment_Manage
        """)
        payments = cursor.fetchall()
        for payment in payments:
            transaction_tree.insert('', 'end', values=payment)
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
    # Configure fonts
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 14, "bold"))
    style.configure("Treeview", font=("Arial", 12))
    # Add scrollbar for Transaction History
    # transaction_scrollbar = ttk.Scrollbar(transaction_frame, orient=VERTICAL, command=transaction_tree.yview)
    # transaction_tree.configure(yscrollcommand=transaction_scrollbar.set)
    # Place Transaction History treeview and scrollbar
    # transaction_scrollbar.pack(side=RIGHT, fill=Y)
    transaction_tree.place(x=15, y=80)
    # Load initial data into transaction tree
    load_all_payments()

    def view_payment_details():
        selected_item = transaction_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Please select a payment to view details")
            return
        payment_id = transaction_tree.item(selected_item)['values'][0]
        try:
            # Clear previous details in side frame first, except the details_label
            for widget in side_frame.winfo_children():
                if widget != details_label:
                    widget.destroy()
            # Get payment details
            cursor.execute("""
                SELECT * FROM Payment_Manage 
                WHERE Payment_ID = ?
            """, (payment_id,))
            payment_details = cursor.fetchone()
            if payment_details:
                # Create treeview to display details
                details_tree = ttk.Treeview(side_frame, columns=("Field", "Value"), show="headings", height=16)
                details_tree.heading("Field", text="Field")
                details_tree.heading("Value", text="Value")
                details_tree.column("Field", width=200)
                details_tree.column("Value", width=300)
                # Insert payment details into treeview
                details = [
                    ("Payment ID", payment_details[0]),
                    ("Tenant ID", payment_details[1]),
                    ("Tenant Name", payment_details[2]),
                    ("Stall ID", payment_details[3]),
                    ("Postcode", payment_details[4]),
                    ("Rental Amount", payment_details[5]),
                    ("Transaction Date", payment_details[6]),
                    ("Remarks", payment_details[7]),
                    ("Bank Slip", payment_details[8]),
                    ("Status", payment_details[9]),
                    ("Gov Receipts", payment_details[10]),
                    ("Due Date", payment_details[11]),
                    ("Overdue Status", payment_details[12]),
                    ("Overdue Amount", payment_details[13]),
                    ("Total Amount", payment_details[14])
                ]
                for field, value in details:
                    details_tree.insert("", "end", values=(field, value))
                details_tree.pack(padx=10, pady=(0, 10))
                # Create a frame for buttons
                button_frame = Frame(side_frame, bg='white')
                button_frame.pack(pady=10)

                def view_bank_slip(bank_slip_path):
                    if bank_slip_path and os.path.exists(bank_slip_path):
                        try:
                            os.startfile(bank_slip_path)  # For Windows
                        except:
                            try:
                                import subprocess
                                subprocess.run(['xdg-open', bank_slip_path])  # For Linux
                            except:
                                try:
                                    subprocess.run(['open', bank_slip_path])  # For macOS
                                except:
                                    messagebox.showerror("Error", "Could not open bank slip file")
                    else:
                        messagebox.showerror("Error", "Bank slip file not found")

                def view_gov_receipt(receipt_path):
                    if receipt_path and os.path.exists(receipt_path):
                        try:
                            os.startfile(receipt_path)  # For Windows
                        except:
                            try:
                                import subprocess
                                subprocess.run(['xdg-open', receipt_path])  # For Linux
                            except:
                                try:
                                    subprocess.run(['open', receipt_path])  # For macOS
                                except:
                                    messagebox.showerror("Error", "Could not open government receipt file")
                    else:
                        messagebox.showerror("Error", "Government receipt file not found")

                # Add buttons to the button frame
                Button(button_frame, text='View Bank Slip', fg='black', bg='ivory2', activebackground='#fd5602',
                       font=('Times new roman', 14), width=15, command=lambda: view_bank_slip(payment_details[8])).pack(
                    side=LEFT, padx=10)
                Button(button_frame, text='View Gov Receipt', fg='black', bg='ivory2', activebackground='#fd5602',
                       font=('Times new roman', 14), width=15,
                       command=lambda: view_gov_receipt(payment_details[10])).pack(
                    side=LEFT, padx=10)

                def show_status_options():
                    # Create frame for radio buttons below button frame
                    status_frame = Frame(side_frame, bg='white')
                    status_frame.pack(pady=10)
                    # Create StringVar to store selected status
                    status_var = StringVar()
                    status_var.set('Completed')  # Default selection
                    # Create radio buttons
                    Radiobutton(status_frame, text='Completed', variable=status_var, value='Completed', bg='white',
                                font=('Arial', 12, 'bold')).pack(side=LEFT, padx=10)
                    Radiobutton(status_frame, text='Pending', variable=status_var, value='Pending', bg='white',
                                font=('Arial', 12, 'bold')).pack(side=LEFT, padx=10)
                    # Add save button below radio buttons
                    save_btn = Button(status_frame, text='Save Changes', fg='white', bg='blue',
                                      activebackground='white',
                                      font=('Times new roman', 12), width=12,
                                      command=lambda: save_status_changes(payment_details[0], status_var.get(),
                                                                          status_frame, update_status_btn))
                    save_btn.pack(pady=10)
                    # Disable the update status button while editing
                    update_status_btn.config(state='disabled')

                def save_status_changes(payment_id, new_status, status_frame, update_btn):
                    try:
                        # Update status in database
                        cursor.execute("""
                            UPDATE Payment_Manage 
                            SET Status = ? 
                            WHERE Payment_ID = ?
                        """, (new_status, payment_id))
                        conn.commit()
                        messagebox.showinfo("Status Update",
                                            f"Payment ID {payment_id}: Status updated to {new_status}.")
                        # Refresh the transaction tree view
                        show_all_data()
                        # Forget (remove) the status frame containing radio buttons and save button
                        status_frame.pack_forget()
                        # Re-enable the update status button
                        update_btn.config(state='normal')
                    except sqlite3.Error as e:
                        messagebox.showerror("Database Error", f"Failed to update status: {str(e)}")

                update_status_btn = Button(button_frame, text='Update Status', fg='black', bg='#fd5602',
                                           activebackground='ivory2', font=('Times new roman', 14), width=15,
                                           command=show_status_options)
                update_status_btn.pack(side=LEFT, padx=10)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    def show_all_data():
        # Clear existing items in treeview
        for item in transaction_tree.get_children():
            transaction_tree.delete(item)
        try:
            # Query all payment details from database
            cursor.execute("""
                    SELECT Payment_ID, Tenant_ID, Tenant_Name, Transaction_Date, 
                           Rental_Amount, Status, Overdue_Status, Overdue_Amount, Total_Amount
                    FROM Payment_Manage
                """)
            payments = cursor.fetchall()
            # Insert all payments into treeview
            for payment in payments:
                transaction_tree.insert('', 'end', values=payment)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    show_all_button = Button(transaction_frame, text='Show All', font=('Arial', 12, 'bold'), bg='#fd5602',
                             activebackground='white', command=show_all_data, width=12)
    show_all_button.place(x=350, y=550)
    view_details_button = Button(transaction_frame, text='View Details', font=('Arial', 12, 'bold'), bg='#fd5602',
                                 activebackground='white', command=view_payment_details, width=12)
    view_details_button.place(x=600, y=550)
    # Create frame beside transaction treeview
    side_frame = Frame(transaction_frame, bg='white', width=650, height=600, relief="solid", borderwidth=1)
    side_frame.place(x=1200, y=80)
    side_frame.pack_propagate(False)  # Prevent the frame from shrinking
    # Create details label at the top of side frame
    details_label = Label(side_frame, text='Details:', font=("Times new roman", 20), bg='white', fg='black')
    details_label.pack(padx=10, pady=10, anchor='nw')
    # Create Treeview for Overdue Payments
    # Create label to show current time
    Label(overdue_frame, text="Current Date & Time: ", font=("Times new roman", 20), fg="blue", bg='mint cream').place(
        x=25, y=20)
    current_time_label = Label(overdue_frame, text="", font=("Times new roman", 20), fg="blue", bg='mint cream')
    current_time_label.place(x=280, y=20)

    def update_time():
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_time_label.config(text=current_time)
        current_time_label.after(1000, update_time)  # Update every 1 second

    update_time()  # Start the time update
    '''
    # Add a checkbox at the right top on the same line as current_time
    show_time_var = IntVar()
    show_time_checkbox = Checkbutton(overdue_frame, text="Show Time", variable=show_time_var, font=("Times new roman", 14), bg='mint cream')
    show_time_checkbox.place(x=600, y=20)
    '''
    # Create frames for checkboxes and labels
    checkbox_frame = Frame(overdue_frame, bg='mint cream')
    checkbox_frame.place(x=1570, y=20)
    label_frame = Frame(overdue_frame, bg='mint cream')
    label_frame.place(x=1570, y=50)
    # Create the monthly label
    monthly_label = Label(label_frame, text="", font=("Times new roman", 14), bg='mint cream')
    monthly_label.pack(anchor='w')
    # Initialize variables
    show_monthly_var = IntVar()
    show_all_var = IntVar()
    # Create both checkboxes at initialization
    show_monthly_checkbox = Checkbutton(
        checkbox_frame,
        text="Show Current Month Records",
        variable=show_monthly_var,
        font=("Times new roman", 14),
        bg='mint cream',
        command=lambda: filter_monthly_records()
    )
    show_all_checkbox = Checkbutton(
        checkbox_frame,
        text="Show All Records",
        variable=show_all_var,
        font=("Times new roman", 14),
        bg='mint cream',
        command=lambda: show_all_records()
    )
    # Initially show only the monthly checkbox
    show_monthly_checkbox.pack(anchor='w')

    def show_all_records():
        # Clear existing items in the treeview
        for item in overdue_tree.get_children():
            overdue_tree.delete(item)
        # Update label
        monthly_label.config(text="All Records Shown", fg='green')
        # Reset checkboxes
        show_monthly_var.set(0)
        show_all_var.set(1)
        # Show monthly checkbox, hide all records checkbox
        show_all_checkbox.pack_forget()
        show_monthly_checkbox.pack(anchor='w')
        # Query and display all records
        try:
            cursor.execute("""
            SELECT Payment_ID, Tenant_ID, Tenant_Name, Rental_Amount, Payment_Due, 
                   Overdue_Status, Overdue_Amount, Total_Amount, Reminder_Date
            FROM Payment_Manage
            """)
            payments = cursor.fetchall()
            for payment in payments:
                overdue_tree.insert('', 'end', values=payment)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    def filter_monthly_records():
        # Clear existing items in the treeview
        for item in overdue_tree.get_children():
            overdue_tree.delete(item)
        # Update label and show all records checkbox
        monthly_label.config(text="Current Month Records Shown", fg='red')
        show_monthly_checkbox.pack_forget()
        show_all_checkbox.pack(anchor='w')
        # Get current month and year
        current_month = datetime.now().month
        current_year = datetime.now().year
        # Query and filter records
        try:
            cursor.execute("""
            SELECT Payment_ID, Tenant_ID, Tenant_Name, Rental_Amount, Payment_Due, 
                   Overdue_Status, Overdue_Amount, Total_Amount, Reminder_Date
            FROM Payment_Manage
            """)
            payments = cursor.fetchall()
            for payment in payments:
                if payment[4] is None:
                    continue
                try:
                    payment_due_date = datetime.strptime(payment[4], "%Y-%m-%d")
                    if payment_due_date.month == current_month and payment_due_date.year == current_year:
                        overdue_tree.insert('', 'end', values=payment)
                except ValueError:
                    continue
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    overdue_tree = ttk.Treeview(overdue_frame, columns=(
        "Payment ID", "Tenant ID", "Tenant Name", "Rental Amount", "Due Date", "Overdue Status", "Overdue Amount",
        "Total Amount", "Reminder Date"), show="headings", height=12)
    # Configure Overdue Payments columns with center alignment
    overdue_tree.heading("Payment ID", text="Payment ID", anchor=CENTER)
    overdue_tree.heading("Tenant ID", text="Tenant ID", anchor=CENTER)
    overdue_tree.heading("Tenant Name", text="Tenant Name", anchor=CENTER)
    overdue_tree.heading("Rental Amount", text="Rental Amount", anchor=CENTER)
    overdue_tree.heading("Due Date", text="Due Date", anchor=CENTER)
    overdue_tree.heading("Overdue Status", text="Overdue Status", anchor=CENTER)
    overdue_tree.heading("Overdue Amount", text="Overdue Amount", anchor=CENTER)
    overdue_tree.heading("Total Amount", text="Total Amount", anchor=CENTER)
    overdue_tree.heading("Reminder Date", text="Reminder Date", anchor=CENTER)
    # Configure column widths and center alignment
    overdue_tree.column("Payment ID", width=180, anchor=CENTER)
    overdue_tree.column("Tenant ID", width=180, anchor=CENTER)
    overdue_tree.column("Tenant Name", width=260, anchor=CENTER)
    overdue_tree.column("Rental Amount", width=220, anchor=CENTER)
    overdue_tree.column("Due Date", width=180, anchor=CENTER)
    overdue_tree.column("Overdue Status", width=200, anchor=CENTER)
    overdue_tree.column("Overdue Amount", width=200, anchor=CENTER)
    overdue_tree.column("Total Amount", width=200, anchor=CENTER)
    overdue_tree.column("Reminder Date", width=220, anchor=CENTER)

    overdue_tree.place(x=25, y=90)
    # Configure fonts
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 14, "bold"))
    style.configure("Treeview", font=("Arial", 12))

    # Add scrollbar for Overdue Payments
    # overdue_scrollbar = ttk.Scrollbar(overdue_frame, orient=VERTICAL, command=overdue_tree.yview)
    # overdue_tree.configure(yscrollcommand=overdue_scrollbar.set)
    # Place Overdue Payments treeview and scrollbar
    # Function to load overdue payments
    def load_overdue_payments():
        # Clear existing items
        for item in overdue_tree.get_children():
            overdue_tree.delete(item)
        try:
            conn = sqlite3.connect('govRental.db')
            cursor = conn.cursor()
            # Get overdue payments with all required fields
            cursor.execute("""
                SELECT 
                    Payment_ID,
                    Tenant_ID,
                    Tenant_Name,
                    Rental_Amount,
                    Payment_Due,
                    Overdue_Status,
                    Overdue_Amount,
                    Total_Amount,
                    Reminder_Date
                FROM Payment_Manage
                WHERE Transaction_Date IS NULL
                AND Status = 'Pending'
            """)
            overdue_payments = cursor.fetchall()
            # Insert payments into treeview
            for payment in overdue_payments:
                payment_id = payment[0]
                tenant_id = payment[1]
                tenant_username = payment[2]
                rental_amount = payment[3]
                payment_due = payment[4] if payment[4] is not None else "N/A"
                overdue_status = payment[5]
                overdue_amount = payment[6]
                total_amount = payment[7] if payment[7] is not None else 0.0  # Handle NoneType for total_amount
                reminder_date = payment[8]
                overdue_tree.insert('', 'end', values=(
                    payment_id,
                    tenant_id,
                    tenant_username,
                    f'RM {rental_amount:.2f}',
                    payment_due,
                    overdue_status,
                    f'RM {overdue_amount:.2f}',
                    f'RM {total_amount:.2f}',
                    reminder_date
                ))
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    # Load overdue payments initially
    load_overdue_payments()
    # Add a label below overdue_tree
    reminder_label = Label(overdue_frame, text="Reminder Message", font=("Arial", 16, "bold"), fg='blue',
                           bg='mint cream')
    reminder_label.place(x=25, y=400)
    '''
    # Add a new Treeview below the label
    reminder_tree = ttk.Treeview(overdue_frame, columns=("Reminder ID", "Message"), show="headings", height=5)
    # Configure Reminder Treeview columns
    reminder_tree.heading("Reminder ID", text="Reminder ID", anchor=CENTER)
    reminder_tree.heading("Message", text="Message", anchor=CENTER)
    # Configure column widths and center alignment
    reminder_tree.column("Reminder ID", width=180, anchor=CENTER)
    reminder_tree.column("Message", width=400, anchor=CENTER)
    # Place Reminder Treeview
    reminder_tree.place(x=25, y=450)
    '''

    def check_and_send_reminders():
        # Get the current date in YYYY-MM-DD format
        current_date = datetime.now().strftime("%Y-%m-%d")
        # Query to find tenants with reminders set for today in Payment_Manage
        cursor.execute("""
        SELECT pm.Stall_ID, pm.Tenant_ID, pm.Tenant_Name, pm.Reminder_Date
        FROM Payment_Manage pm
        WHERE pm.Reminder_Date = ?
        """, (current_date,))
        results = cursor.fetchall()
        for row in results:
            stall_id, tenant_id, tenant_username, reminder_date = row
            reminder_message = "This is a reminder for your upcoming payment due."
            # Insert a new reminder entry into the Reminder table
            cursor.execute("""
            INSERT INTO Reminder (Tenant_ID, Tenant_Username, Tenant_Email_Address, Stall_ID, Reminder_Message, Sent_Date)
            VALUES (?, ?, '', ?, ?, ?)
            """, (tenant_id, tenant_username, stall_id, reminder_message, current_date))
        # Commit the changes
        conn.commit()

    def display_reminders():
        # Query to fetch reminder details for the Treeview display
        cursor.execute("""
        SELECT Reminder_ID, Tenant_ID, Tenant_Username, Sent_Date, Reminder_Message FROM Reminder
        """)
        reminders = cursor.fetchall()
        # Configure Treeview
        reminder_tree = ttk.Treeview(overdue_frame, columns=(
            "Reminder_ID", "Tenant_ID", "Tenant_Username", "Sent_Date", "Reminder_Message"),
                                     show="headings")
        reminder_tree.heading("Reminder_ID", text="Reminder ID")
        reminder_tree.heading("Tenant_ID", text="Tenant ID")
        reminder_tree.heading("Tenant_Username", text="Tenant Username")
        reminder_tree.heading("Sent_Date", text="Sent Date")
        reminder_tree.heading("Reminder_Message", text="Message")
        # Insert data into Treeview
        for reminder in reminders:
            reminder_tree.insert("", "end", values=reminder)
        reminder_tree.place(x=25, y=450)

    check_and_send_reminders()
    display_reminders()


def admin_inbox():
    # Variables
    Unit = StringVar()
    Inbox = StringVar(value="Inbox")
    SearchText = StringVar()
    AttachmentPath = StringVar()
    SendToAll = BooleanVar()
    PostCode = StringVar()
    # List of available units and inbox categories
    inbox_set = ['Inbox', 'Read', 'Sent']
    ##FIXME: Placeholder for current user - replace with actual login system in production
    current_user = "Admin"  # This line resolves the 'current_user' warnings
    admin_frame = Frame(main_frame)
    admin_frame.place(relwidth=1, relheight=1)

    def generate_message_id():
        """Generate a unique message ID"""
        return str(uuid.uuid4())

    def filter_inbox(event):
        typed_text = Inbox.get().lower()
        filtered_inbox = [i for i in inbox_set if typed_text in i.lower()]
        inbox_combo['values'] = filtered_inbox

    def on_stall_id_entry(event):
        stall_id = stall_id_entry.get().strip()
        update_message_display(stall_id_filter=stall_id)

    ATTACHMENTS_DIR = "attachments"
    if not os.path.exists(ATTACHMENTS_DIR):
        os.makedirs(ATTACHMENTS_DIR)

    def save_attachment(file_path):
        """
        Save attachment to attachments directory and return the new path
        """
        if not file_path:
            return None

        # Create unique filename
        file_ext = os.path.splitext(file_path)[1]
        new_filename = f"{str(uuid.uuid4())}{file_ext}"
        new_path = os.path.join(ATTACHMENTS_DIR, new_filename)

        # Copy file to attachments directory
        shutil.copy2(file_path, new_path)
        return new_path

    def open_attachment(attachment_path):
        """
        Open the attachment using system default application
        """
        if attachment_path and os.path.exists(attachment_path):
            import platform
            if platform.system() == 'Darwin':  # macOS
                os.system(f'open "{attachment_path}"')
            elif platform.system() == 'Windows':  # Windows
                os.system(f'start "" "{attachment_path}"')
            else:  # Linux
                os.system(f'xdg-open "{attachment_path}"')
        else:
            messagebox.showerror("Error", "Attachment not found!")

    def browse_file(window):
        from tkinter import filedialog
        file_types = (
            ("All files", "*.*"),
            ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("Documents", "*.pdf *.doc *.docx *.txt")
        )
        file_path = filedialog.askopenfilename(
            title="Select file",
            parent=window,
            filetypes=file_types
        )
        if file_path:
            AttachmentPath.set(file_path)
            attachment_entry.config(state='normal')  # Enable the entry to update the path
            attachment_entry.delete(0, END)  # Clear the entry
            attachment_entry.insert(0, file_path)  # Insert the new file path
            attachment_entry.config(state='readonly')  # Set the entry back to readonly

    def fetch_postcodes():
        conn = sqlite3.connect('govRental.db')
        c = conn.cursor()

        try:
            c.execute("SELECT DISTINCT Postcode FROM Stall")
            postcodes = [row[0] for row in c.fetchall()]
            return postcodes
        finally:
            conn.close()  # Ensure connection is closed after fetching

    def fetch_stall_ids_by_postcode(postcode):
        conn = sqlite3.connect('govRental.db')
        c = conn.cursor()

        try:
            # Query to select stall_ids based on the provided postcode
            c.execute("SELECT stall_id FROM Stall WHERE Postcode = ?", (postcode,))
            stall_ids = [row[0] for row in c.fetchall()]  # Fetch all stall_ids
            return stall_ids
        finally:
            conn.close()  # Ensure connection is closed after fetching

    def generate_message_id():
        return str(uuid.uuid4())  # Generates a unique ID using UUID

    def insert_message_to_tables(sender, recipient, subject, message, attachment=None):
        """Insert message into both notif_sent_reply and notif_inbox tables"""
        conn = sqlite3.connect('govRental.db')
        c = conn.cursor()

        try:
            # Generate a unique message ID
            message_id = generate_message_id()

            # Insert into notif_sent_reply table
            c.execute(''' 
                INSERT INTO notif_sent_reply (
                    message_id, sender, recipient, subject, message, attachment, timestamp_sent_reply
                ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (message_id, sender, recipient, subject, message, attachment))

            # Print the inserted message ID
            print(f"Inserted message into notif_sent_reply with ID: {message_id}")

            # Insert into notif_inbox table with 'New' status
            c.execute(''' 
                INSERT INTO notif_inbox (
                    message_id, sender, recipient, subject, message, attachment, 
                    timestamp_receive, timestamp_read, status
                ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, NULL, 'New')
            ''', (message_id, sender, recipient, subject, message, attachment))

            # Print the inserted message ID
            print(f"Inserted message into notif_inbox with ID: {message_id}")

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def send_message(send_to_all):
        import tkinter as tk
        subject = subject_entry.get().strip()
        message = message_text.get(1.0, tk.END).strip()
        attachment_path = AttachmentPath.get().strip()

        # Debug prints to check values
        print(f"Subject: '{subject}'")
        print(f"Message: '{message}'")
        print(f"Attachment path: '{attachment_path}'")

        # Check if message only contains whitespace
        if not subject or message.isspace():
            messagebox.showwarning("Missing Information", "Please enter both subject and message!")
            return

        conn_rental = sqlite3.connect('govRental.db')
        c_rental = conn_rental.cursor()

        try:
            if send_to_all:
                # Fetch all stall IDs across all postcodes
                c_rental.execute("SELECT Stall_ID FROM Stall")
                stall_IDs = [str(row[0]) for row in c_rental.fetchall()]
                print(f"All Stall IDs retrieved: {stall_IDs}")  # Debug print

                if not stall_IDs:
                    messagebox.showwarning("No Stalls", "No stalls found in the database!")
                    return

                # Insert message for each stall ID
                for stall_id in stall_IDs:
                    if not insert_message_to_tables(current_user, stall_id, subject, message, attachment_path):
                        messagebox.showerror("Insert Error", "Failed to send message.")
                        return

            else:
                # Use specified postcode and selected stall ID
                postcode = PostCode.get().strip()
                if not postcode:
                    messagebox.showwarning("Invalid Postcode", "Please enter a valid postcode!")
                    return

                unit = stall_id_combo.get().strip()
                if not unit:
                    messagebox.showwarning("Missing Stall ID", "Please select a stall ID!")
                    return

                # Insert message for the selected stall ID
                if not insert_message_to_tables(current_user, unit, subject, message, attachment_path):
                    messagebox.showerror("Insert Error", "Failed to send message.")
                    return

            messagebox.showinfo("Success", "Message sent successfully!")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn_rental.close()

    def get_messages(user, category):
        conn = sqlite3.connect('govRental.db')
        c = conn.cursor()

        try:
            if category == "Sent":
                query = """
                    SELECT message_id, sender, recipient, subject, message, attachment, timestamp_sent_reply, 'Sent' as status
                    FROM notif_sent_reply 
                    WHERE sender = ? 
                    ORDER BY timestamp_sent_reply DESC
                """
                c.execute(query, (user,))

            elif category == "Read":
                query = """
                    SELECT message_id, sender, recipient, subject, message, attachment, timestamp_receive, status
                    FROM notif_inbox 
                    WHERE recipient = ? 
                    AND status = 'Read'
                    ORDER BY timestamp_receive DESC
                """
                c.execute(query, (user,))

            else:  # "Inbox" - new messages
                query = """
                    SELECT message_id, sender, recipient, subject, message, attachment, timestamp_receive, status
                    FROM notif_inbox 
                    WHERE recipient = ? 
                    AND status = 'New'
                    ORDER BY timestamp_receive DESC
                """
                c.execute(query, (user,))

            return c.fetchall()

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()

    def update_message_display(stall_id_filter=None):
        import tkinter as tk
        """Update the message listbox with messages from the selected category and filtered by stall_id if provided."""
        message_listbox.delete(0, tk.END)
        selected_category = Inbox.get()
        messages = get_messages(current_user, selected_category)

        # Filter messages by stall_id if a filter is provided
        if stall_id_filter:
            messages = [msg for msg in messages if msg[2] == stall_id_filter]  # Assuming `recipient` is at index 2

        for message in messages:
            message_id, sender, recipient, subject, message_text, attachment, timestamp, status = message

            # Format timestamp for display
            try:
                timestamp_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                formatted_date = timestamp_obj.strftime("%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                formatted_date = "Unknown date"

            # Create display text based on category
            if selected_category == "Sent":
                display_text = f"To: {recipient} | Subject: {subject} | Date: {formatted_date}"
            else:
                display_text = f"From: {sender} | Subject: {subject} | Date: {formatted_date}"

            # Add attachment indicator if present
            if attachment:
                display_text += " 📎"

            message_listbox.insert(tk.END, display_text)

            # Set background color for new messages
            if status == 'New':
                message_listbox.itemconfig(message_listbox.size() - 1, {'bg': '#FFE4B5'})  # Light orange background

    def show_full_message(event):
        import tkinter as tk
        selection = message_listbox.curselection()
        if not selection:
            return

        selected_index = selection[0]
        selected_category = Inbox.get()
        messages = get_messages(current_user, selected_category)
        selected_message = messages[selected_index]

        # Unpack the message details
        message_id, sender, recipient, subject, message, attachment, timestamp, status = selected_message

        # Clear previous content
        for widget in full_message_frame.winfo_children():
            widget.destroy()

        # Create a new frame for message details
        details_frame = tk.Frame(full_message_frame, bg="#F5F5F5")
        details_frame.pack(fill=tk.X, padx=10, pady=10)

        # Add message details
        tk.Label(details_frame, text=f"Subject: {subject}", font=("Helvetica", 12, "bold"), bg="#F5F5F5",
                 anchor="w").pack(fill=tk.X)
        tk.Label(details_frame, text=f"From: {sender}", font=("Helvetica", 12), bg="#F5F5F5", anchor="w").pack(
            fill=tk.X)
        tk.Label(details_frame, text=f"To: {recipient}", font=("Helvetica", 12), bg="#F5F5F5", anchor="w").pack(
            fill=tk.X)
        tk.Label(details_frame, text=f"Date: {timestamp}", font=("Helvetica", 10), bg="#F5F5F5", anchor="w").pack(
            fill=tk.X)

        if attachment:
            attachment_frame = tk.Frame(details_frame, bg="#F5F5F5")
            attachment_frame.pack(fill=tk.X, pady=5)

            attachment_label = tk.Label(
                attachment_frame,
                text=f"📎 {os.path.basename(attachment)}",
                font=("Helvetica", 10),
                bg="#F5F5F5",
                fg="blue",
                cursor="hand2"
            )
            attachment_label.pack(side=tk.LEFT)
            attachment_label.bind("<Button-1>", lambda e: open_attachment(attachment))

        # Create a frame for the message body and replies
        message_body_frame = tk.Frame(full_message_frame)
        message_body_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Add scrollbar
        scrollbar = tk.Scrollbar(message_body_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add canvas for scrolling
        canvas = tk.Canvas(message_body_frame, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)

        # Create a frame inside the canvas for message content
        content_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor="nw")

        # Split the message into original message and replies
        message_parts = message.split("\n--- Reply from ")
        original_message = message_parts[0]

        # Display original message
        original_message_frame = tk.Frame(content_frame, bg="#ffcf90", bd=1, relief=tk.SOLID)
        original_message_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(original_message_frame, text="Original Message", font=("Helvetica", 10, "bold"), bg="#ffcf90").pack(
            anchor="w")
        tk.Label(original_message_frame, text=original_message, font=("Helvetica", 10), bg="#ffcf90", justify=tk.LEFT,
                 wraplength=700).pack(anchor="w", padx=5, pady=5)

        # Display replies
        if len(message_parts) > 1:
            tk.Label(content_frame, text="Replies:", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(10, 5))
            for reply in message_parts[1:]:
                reply_frame = tk.Frame(content_frame, bg="white", bd=1, relief=tk.SOLID)
                reply_frame.pack(fill=tk.X, padx=5, pady=5)

                # Split the reply into sender and content
                try:
                    reply_sender, reply_content = reply.split(" ---\n", 1)
                except ValueError:
                    # Handle cases where the format might be different
                    reply_sender = "Unknown"
                    reply_content = reply

                tk.Label(reply_frame, text=f"Reply from {reply_sender}", font=("Helvetica", 10, "bold"),
                         bg="white").pack(anchor="w")
                tk.Label(reply_frame, text=reply_content, font=("Helvetica", 10), bg="white", justify=tk.LEFT,
                         wraplength=700).pack(anchor="w", padx=5, pady=5)

        # Update scroll region
        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Add reply frame at the bottom
        reply_frame = tk.Frame(full_message_frame, bg="#F5F5F5")
        reply_frame.pack(fill=tk.X, padx=10, pady=10)

        # Add reply text field
        reply_text = tk.Text(reply_frame, height=4, font=("Helvetica", 12))
        reply_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Add reply button
        reply_button = tk.Button(
            reply_frame,
            text="Send Reply",
            font=("Helvetica", 12),
            bg="#ff8210",
            fg="white",
            command=lambda: handle_reply_send(
                sender=current_user,
                recipient=sender,  # Send reply to original sender
                subject=f"Re: {subject.replace('Re: ', '')}",  # Avoid multiple "Re:" prefixes
                reply_message=reply_text.get("1.0", tk.END).strip(),
                original_message_id=message_id,
                reply_text=reply_text
            )
        )
        reply_button.pack(side=tk.RIGHT)

        if status == "New":
            mark_message_as_read(message_id)

    def mark_message_as_read(message_id):
        """
        Mark a message as read in the notif_inbox table
        """
        conn = sqlite3.connect('govRental.db')
        c = conn.cursor()

        try:
            # First check if the message is in 'New' status
            c.execute("""
                SELECT status 
                FROM notif_inbox 
                WHERE message_id = ? AND recipient = ? AND status = 'New'
            """, (message_id, current_user))

            if c.fetchone():  # Only update if message is in 'New' status
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("""
                    UPDATE notif_inbox 
                    SET status = 'Read', timestamp_read = ? 
                    WHERE message_id = ? AND recipient = ? AND status = 'New'
                """, (current_timestamp, message_id, current_user))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
        finally:
            conn.close()
            update_message_display()

    def delete_message():
        """
        Delete selected message from inbox/sent_reply and move it to delete table
        Only deletes from the user's perspective (admin in this case)
        """
        selected_index = message_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Selection Error", "Please select a message to delete.")
            return

        selected_category = Inbox.get()
        messages = get_messages(current_user, selected_category)

        if selected_index[0] >= len(messages):
            messagebox.showwarning("Error", "Invalid selection.")
            return

        message = messages[selected_index[0]]
        message_id = message[0]  # First element is message_id

        # Confirm deletion
        if not messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this message?"):
            return

        conn = sqlite3.connect('govRental.db')
        c = conn.cursor()

        try:
            # Begin transaction
            conn.execute('BEGIN')

            # Store message in notif_deleted table
            c.execute("""
                INSERT INTO notif_deleted (
                    message_id, sender, recipient, subject, message, 
                    attachment, source, timestamp_deleted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                message_id,
                message[1],  # sender
                message[2],  # recipient
                message[3],  # subject
                message[4],  # message
                message[5],  # attachment
                selected_category  # source table
            ))

            # Remove from appropriate source table based on category
            if selected_category == "Sent":
                # Delete from notif_sent_reply where current user is sender
                c.execute("""
                    DELETE FROM notif_sent_reply 
                    WHERE message_id = ? AND sender = ?
                """, (message_id, current_user))
            else:
                # Delete from notif_inbox where current user is recipient
                c.execute("""
                    DELETE FROM notif_inbox 
                    WHERE message_id = ? AND recipient = ?
                """, (message_id, current_user))

            conn.commit()
            messagebox.showinfo("Success", "Message deleted successfully")

            # Refresh the message display
            update_message_display()

            # Clear the full message display
            for widget in full_message_frame.winfo_children():
                widget.destroy()

        except sqlite3.Error as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to delete message: {str(e)}")
        finally:
            conn.close()

    def compose_message():
        global compose_win, message_text, PostCode, stall_id_combo, note_label, subject_entry, AttachmentPath, attachment_entry

        compose_win = Toplevel(admin_frame)
        compose_win.title("Compose Message")
        compose_win.geometry("800x600")
        compose_win.config(bg="#D3D3D3")

        main_frame = Frame(compose_win, bg="#D3D3D3")
        main_frame.pack(expand=True, fill=BOTH, padx=20, pady=20)

        main_frame.grid_columnconfigure(1, weight=1)

        # Send to All Checkbox
        SendToAll = BooleanVar(value=False)
        send_all_cb = Checkbutton(
            main_frame,
            text="Send to ALL Units (across all postcodes)",
            variable=SendToAll,
            font=("helvetica", 12),
            bg="#D3D3D3",
            command=lambda: toggle_postcode_unit_fields(SendToAll.get(), postcode_entry, stall_id_combo, note_label)
        )
        send_all_cb.grid(row=0, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")

        # Postcode Entry
        PostCode = StringVar()
        Label(main_frame, text="Search by Postcode", font=("helvetica", 16), bg="#D3D3D3").grid(
            row=1, column=0, padx=10, pady=10, sticky="w")
        postcode_entry = Entry(main_frame, textvariable=PostCode, font=("helvetica", 16), width=40)
        postcode_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Trigger filtering function when Enter is pressed
        postcode_entry.bind("<Return>", lambda e: update_stall_ids(PostCode.get()))

        # Stall ID Combo Box
        Label(main_frame, text="Stall ID", font=("helvetica", 16), bg="#D3D3D3").grid(
            row=2, column=0, padx=10, pady=10, sticky="w")
        stall_id_combo = ttk.Combobox(main_frame, font=("helvetica", 16), width=40)
        stall_id_combo.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # Note label for auto-selection
        note_label = Label(
            main_frame,
            text="Note: If no unit is selected, message will be sent to all units in the postcode",
            font=("helvetica", 12, "italic"),
            fg="gray",
            bg="#D3D3D3"
        )
        note_label.grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")

        # Subject Entry
        Label(main_frame, text="Subject", font=("helvetica", 16), bg="#D3D3D3").grid(
            row=4, column=0, padx=10, pady=10, sticky="w")
        subject_entry = Entry(main_frame, font=("helvetica", 16))
        subject_entry.grid(row=4, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        # Message Text Area
        Label(main_frame, text="Message", font=("helvetica", 16), bg="#D3D3D3").grid(
            row=5, column=0, padx=10, pady=10, sticky="nw")
        message_text = Text(main_frame, font=("helvetica", 16), width=50, height=10)
        message_text.grid(row=5, column=1, columnspan=2, padx=10, pady=10, sticky="nsew")

        main_frame.grid_rowconfigure(5, weight=1)

        # Attachment Section
        AttachmentPath = StringVar()
        Label(main_frame, text="Attachment", font=("helvetica", 16), bg="#D3D3D3").grid(
            row=6, column=0, padx=10, pady=10, sticky="w")
        attachment_entry = Entry(main_frame, textvariable=AttachmentPath, font=("helvetica", 16), state='readonly')
        attachment_entry.grid(row=6, column=1, padx=10, pady=10, sticky="ew")
        Button(main_frame, text="Browse", font=("helvetica", 16),
               command=lambda: browse_file(compose_win)).grid(
            row=6, column=2, padx=10, pady=10, sticky="e")

        # Send Button
        send_button = Button(main_frame, text="Send", font=("helvetica", 16),
                             bg="#ff8210", fg="white",
                             command=lambda: send_message(SendToAll.get()))
        send_button.grid(row=7, column=1, padx=10, pady=20, sticky="ew")

    def update_stall_ids(selected_postcode):
        # Fetch stall IDs for the selected postcode and update stall_id_combo values
        stall_ids = fetch_stall_ids_by_postcode(selected_postcode)  # Assumes this function returns a list of stall IDs
        stall_id_combo['values'] = stall_ids  # Update ComboBox options

    def toggle_postcode_unit_fields(send_to_all, postcode_entry, unit_combo, note_label):
        """Toggle the state of postcode and unit fields based on Send to All checkbox"""
        if send_to_all:
            postcode_entry.configure(state='disabled')
            unit_combo.configure(state='disabled')
            note_label.configure(text="Note: Message will be sent to ALL units across ALL postcodes")
        else:
            postcode_entry.configure(state='normal')
            unit_combo.configure(state='normal')
            note_label.configure(text="Note: If no unit is selected, message will be sent to all units in the postcode")

    def reply_message(original_sender, original_subject, original_message):
        reply_win = tk.Toplevel(root)
        reply_win.title("Reply Message")
        reply_win.geometry("800x600")
        reply_win.config(bg="#D3D3D3")

        # Create main frame
        main_frame = tk.Frame(reply_win, bg="#D3D3D3")
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        # Recipient and Subject display
        tk.Label(main_frame, text=f"To: {original_sender}", font=("Helvetica", 14), bg="#D3D3D3").pack(anchor="w")
        tk.Label(main_frame, text=f"Subject: Re: {original_subject}", font=("Helvetica", 14, "bold"),
                 bg="#D3D3D3").pack(
            anchor="w")

        # Frame for previous messages
        previous_messages_frame = tk.Frame(main_frame)
        previous_messages_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

        # Scrollable text area for previous messages
        previous_messages = tk.Text(previous_messages_frame, font=("Helvetica", 12), wrap=tk.WORD, padx=10, pady=10)
        previous_messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        previous_messages.insert(tk.END,
                                 f"From: {original_sender}\nSubject: {original_subject}\n\n{original_message}\n\n")
        previous_messages.config(state=tk.DISABLED)  # Disable editing

        # Scrollbar for previous messages
        scrollbar = tk.Scrollbar(previous_messages_frame, command=previous_messages.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        previous_messages.config(yscrollcommand=scrollbar.set)

        # Frame for new message
        new_message_frame = tk.Frame(main_frame)
        new_message_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

        tk.Label(new_message_frame, text="Your Reply:", font=("Helvetica", 14), bg="#D3D3D3").pack(anchor="w")

        # Text area for user reply
        reply_text = tk.Text(new_message_frame, font=("Helvetica", 12), wrap=tk.WORD, height=5)
        reply_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Send button for sending the reply
        send_reply_button = tk.Button(main_frame, text="Send Reply", font=("Helvetica", 12), bg="#ff8210", fg="white",
                                      command=lambda: send_reply(original_sender, f"Re: {original_subject}",
                                                                 reply_text.get(1.0, tk.END).strip(), reply_win))
        send_reply_button.pack(pady=10)

    def send_reply(sender, recipient, subject, reply_message, original_message_id):
        """
        Send a reply message and store it in both notif_sent_reply and notif_inbox tables
        """
        if not reply_message.strip():
            messagebox.showwarning("Missing Reply", "Please enter your reply message!")
            return False

        conn = sqlite3.connect('govRental.db')
        c = conn.cursor()

        try:
            # Generate a new message_id for the reply
            new_message_id = generate_message_id()
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # First, get the original message thread
            c.execute("""
                SELECT message FROM notif_sent_reply 
                WHERE message_id = ?
            """, (original_message_id,))
            original_message = c.fetchone()[0]

            # Create the updated message thread content
            updated_message = f"{original_message}\n--- Reply from {sender} ---\n{current_timestamp}: {reply_message}"

            # Insert reply into notif_sent_reply
            c.execute("""
                INSERT INTO notif_sent_reply (
                    message_id, sender, recipient, subject, message, 
                    attachment, timestamp_sent_reply
                ) VALUES (?, ?, ?, ?, ?, NULL, ?)
            """, (new_message_id, sender, recipient, subject, updated_message, current_timestamp))

            # Insert reply into notif_inbox
            c.execute("""
                INSERT INTO notif_inbox (
                    message_id, sender, recipient, subject, message,
                    attachment, timestamp_receive, timestamp_read, status
                ) VALUES (?, ?, ?, ?, ?, NULL, ?, NULL, 'New')
            """, (new_message_id, sender, recipient, subject, updated_message, current_timestamp))

            conn.commit()
            messagebox.showinfo("Reply Sent", "Your reply has been sent successfully!")
            return True

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            messagebox.showerror("Error", "Failed to send reply. Please try again.")
            return False
        finally:
            conn.close()

    def handle_reply_send(sender, recipient, subject, reply_message, original_message_id, reply_text):
        import tkinter as tk
        """Helper function to handle reply sending and UI updates"""
        if send_reply(sender, recipient, subject, reply_message, original_message_id):
            reply_text.delete("1.0", tk.END)  # Clear reply field
            update_message_display()  # Refresh message list
            show_full_message(None)  # Refresh full message view

    # Main frame for entries
    entries_frame = Frame(admin_frame, bg="ivory2")
    entries_frame.pack(side=TOP, fill=BOTH)
    # Configure grid columns
    for i in range(7):
        entries_frame.grid_columnconfigure(i, weight=1)
    # Header label
    Label(entries_frame, text="Admin - INBOX", font=("Helvetica", 30, "bold"), bg="ivory2").grid(
        row=0, column=0, columnspan=7, padx=10, pady=(20, 10), sticky="nsew"
    )
    # Category label and combo box
    Label(entries_frame, text="Category:", font=("Helvetica", 16), bg="ivory2").grid(
        row=1, column=2, padx=10, pady=10, sticky="nsew"
    )
    # Assuming Inbox and inbox_set are defined somewhere in your code
    inbox_combo = ttk.Combobox(entries_frame, textvariable=Inbox, font=("Helvetica", 16), width=30, values=inbox_set)
    inbox_combo.grid(row=1, column=3, padx=10, pady=10, sticky="nsew")
    inbox_combo.bind("<KeyRelease>", filter_inbox)
    inbox_combo.bind("<<ComboboxSelected>>", lambda e: update_message_display())
    # Frame for the stall ID filter
    stall_id_frame = Frame(entries_frame, bg="#F5F5F5")
    stall_id_frame.grid(row=2, column=2, columnspan=3, padx=10, pady=10, sticky="ew")
    # Frame for buttons
    button_frame = Frame(entries_frame, bg="ivory2")
    button_frame.grid(row=4, column=1, columnspan=4, padx=10, pady=10, sticky="ew")
    # Configure button frame columns
    for i in range(3):
        button_frame.columnconfigure(i, weight=1)
    # Add buttons with improved styling
    button_style = {
        "font": ("Helvetica", 16),
        "bg": "#ff8210",
        "fg": "white",
        "activebackground": "#ff6930",
        "activeforeground": "white"
    }
    Button(button_frame, text="Compose Message", command=compose_message, **button_style).grid(row=0, column=1,
                                                                                               padx=5, pady=5,
                                                                                               sticky="ew")
    Button(button_frame, text="Delete Message", command=delete_message, **button_style).grid(row=0, column=2, padx=5,
                                                                                             pady=5, sticky="ew")
    '''
    # Move the frame to the position of the result label
    result_label = Label(entries_frame, text="Results:", font=("Helvetica", 16), bg="#F5F5F5")
    result_label.grid(row=4, column=0, columnspan=7, padx=10, pady=10, sticky="w")
    '''
    # Message display setup
    lower_frame = Frame(admin_frame)
    lower_frame.pack(side=TOP, fill=BOTH, expand=True)
    # Frame for the message list
    message_frame = Frame(lower_frame)
    message_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
    message_listbox = Listbox(message_frame, font=("Helvetica", 12))
    message_listbox.pack(side=LEFT, fill=BOTH, expand=True)
    message_scrollbar = Scrollbar(message_frame, orient=VERTICAL, command=message_listbox.yview)
    message_scrollbar.pack(side=RIGHT, fill=Y)
    message_listbox.config(yscrollcommand=message_scrollbar.set)
    # Bind selection of message listbox to show full message
    message_listbox.bind("<<ListboxSelect>>", show_full_message)
    # Frame for displaying the full message
    full_message_frame = Frame(lower_frame)
    full_message_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)
    full_message_text = Text(full_message_frame, font=("Helvetica", 12), wrap=WORD)
    full_message_text.pack(side=LEFT, fill=BOTH, expand=True)
    # Initialize the message display
    update_message_display()


def general_setting():
    def fetch_admin_id():
        admin_ic = admin_ic_entry.get()
        if admin_ic:
            cursor.execute("SELECT Admin_ID, Admin_Name FROM Admin WHERE Admin_IC_Number = ?", (admin_ic,))
            result = cursor.fetchone()
            if result:
                admin_id_entry.delete(0, END)  # Clear existing entry
                admin_id_entry.insert(0, result[0])  # Insert fetched Admin ID
                admin_id_entry.configure(state='readonly')
                admin_name_entry.delete(0, END)  # Clear existing entry
                admin_name_entry.insert(0, result[1])  # Insert fetched Admin ID
                admin_name_entry.configure(state='readonly')
            else:
                admin_id_entry.delete(0, END)  # Clear if not found

    def update_passcode():
        new_passcode = new_passcode_entry.get()
        confirm_passcode = confirm_passcode_entry.get()
        old_passcode = old_passcode_entry.get()
        admin_id = admin_id_entry.get()
        admin_ic = admin_ic_entry.get()
        admin_name = admin_name_entry.get()
        if not admin_id or not admin_ic or not admin_name:
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        # Verify admin credentials
        cursor.execute("SELECT Admin_ID, Admin_Name FROM Admin WHERE Admin_IC_Number = ?", (admin_ic,))
        result = cursor.fetchone()
        if not result or result[0] != admin_id or result[1] != admin_name:
            messagebox.showerror("Error", "Invalid admin credentials. Please check your IC number, ID and name.")
            admin_ic_entry.delete(0, END)
            admin_id_entry.delete(0, END)
            admin_name_entry.delete(0, END)
            old_passcode_entry.delete(0, END)
            new_passcode_entry.delete(0, END)
            confirm_passcode_entry.delete(0, END)
            return
        if not old_passcode or not new_passcode or not confirm_passcode:
            messagebox.showerror("Error", "Please fill in all passcode fields.")
            old_passcode_entry.delete(0, END)
            new_passcode_entry.delete(0, END)
            confirm_passcode_entry.delete(0, END)
            return
        if new_passcode != confirm_passcode:
            messagebox.showerror("Error", "New passcode and confirm passcode do not match.")
            new_passcode_entry.delete(0, END)
            confirm_passcode_entry.delete(0, END)
            return
        # Check if old passcode matches
        cursor.execute("SELECT Admin_Passcode FROM Admin WHERE Admin_ID = ?", (admin_id,))
        result = cursor.fetchone()
        if result and result[0] == old_passcode:
            try:
                cursor.execute("UPDATE Admin SET Admin_Passcode = ? WHERE Admin_ID = ?", (new_passcode, admin_id))
                conn.commit()
                messagebox.showinfo("Success", "Passcode updated successfully!")
                admin_ic_entry.delete(0, END)
                admin_id_entry.config(state='normal')
                admin_id_entry.delete(0, END)
                admin_name_entry.config(state='normal')
                admin_name_entry.delete(0, END)
                old_passcode_entry.delete(0, END)
                new_passcode_entry.delete(0, END)
                confirm_passcode_entry.delete(0, END)
                return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update passcode: {e}")
                admin_ic_entry.delete(0, END)
                admin_id_entry.delete(0, END)
                admin_name_entry.delete(0, END)
                old_passcode_entry.delete(0, END)
                new_passcode_entry.delete(0, END)
                confirm_passcode_entry.delete(0, END)
                return
        else:
            messagebox.showerror("Error", "Old passcode is incorrect.")
            admin_ic_entry.delete(0, END)
            admin_id_entry.delete(0, END)
            admin_name_entry.delete(0, END)
            old_passcode_entry.delete(0, END)
            new_passcode_entry.delete(0, END)
            confirm_passcode_entry.delete(0, END)
            return

    def fetch_business_info(event):
        # Fetch business information from the database
        cursor.execute(
            "SELECT Business_ID, Licence_No, Business_Name, Business_Hours, Location, Contact_No, Email_Address FROM Business_Information")  # Adjust your table name and columns
        result = cursor.fetchone()
        if result:
            business_id_entry.delete(0, END)
            business_id_entry.insert(0, result[0])  # Business_ID
            business_id_entry.config(state='readonly')
            license_entry.delete(0, END)
            license_entry.insert(0, result[1])  # Licence_No
            license_entry.config(state='readonly')
            firm_name_entry.delete(0, END)
            firm_name_entry.insert(0, result[2])  # Business_Name
            firm_name_entry.config(state='readonly')
            business_hours_entry.delete(0, END)
            business_hours_entry.insert(0, result[3])  # Business_Hours
            business_hours_entry.config(state='readonly')
            location_entry.delete(0, END)
            location_entry.insert(0, result[4])  # Location
            location_entry.config(state='readonly')
            contact_entry.delete(0, END)  # Clear existing entry for contact
            contact_entry.insert(0, result[5])  # Contact_No
            contact_entry.config(state='readonly')
            email_entry.delete(0, END)  # Clear existing entry for email
            email_entry.insert(0, result[6])  # Email_Address
            email_entry.config(state='readonly')
        else:
            messagebox.showinfo("Info", "No business information found.")

    # root = Tk()
    # root.title("Admin Settings")
    # root.geometry("1920x1080")
    # welcome_label = Label(root, text='Welcome, Dear Admin.', fg='#fd5602', font=("Arial", 30, "bold"))
    # welcome_label.place(x=720, y=120)  # Adjust the x and y coordinates as needed
    setting_frame = Frame(main_frame)
    setting_frame.place(relwidth=1, relheight=1)
    welcome_label = Label(setting_frame, text='Welcome, Dear Admin.', fg='black', font=("Arial", 30, "bold"))
    welcome_label.place(x=720, y=100)  # Adjust the x and y coordinates as needed
    # Create a Notebook (tabs)
    # notebook = ttk.Notebook(root)
    # notebook.place(x=350, y=220, width=1200, height=600)  # Adjust the placement of the notebook
    notebook = ttk.Notebook(setting_frame)
    notebook.place(x=350, y=200, width=1200, height=600)  # Adjust the placement of the notebook
    # Create frames for the tabs with white background
    passcode_frame = Frame(notebook, width=1200, height=600, bg='white')  # Added white background
    business_info_frame = Frame(notebook, width=1200, height=600, bg='white')  # Added white background
    # Add frames to the notebook
    notebook.add(passcode_frame, text="Change Passcode")
    notebook.add(business_info_frame, text="Edit Business Information")

    # Add buttons beside notebook
    def logout():
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to quit?"):
            root.destroy()  # Close the entire window

    logout_button = Button(setting_frame, text="Log Out", command=logout, font=('Arial', 12, 'bold'), fg='white',
                           bg='#fd5602', width=15)
    logout_button.place(x=1600, y=200)
    label_font = ("Arial", 16, "bold")
    entry_font = ("Helvetica", 16)
    # Change Passcode Tab
    Label(passcode_frame, text="Admin IC:", bg='white', font=label_font).place(x=150, y=50)
    admin_ic_entry = Entry(passcode_frame, width=30, font=entry_font)
    admin_ic_entry.place(x=450, y=50)
    # Add the binding after creating the Entry widget
    admin_ic_entry.bind('<KeyRelease>', lambda e: fetch_admin_id())
    Label(passcode_frame, text="Admin ID:", bg='white', font=label_font).place(x=150, y=100)
    admin_id_entry = Entry(passcode_frame, width=30, font=entry_font)
    admin_id_entry.place(x=450, y=100)
    Label(passcode_frame, text="Your Name:", bg='white', font=label_font).place(x=150, y=150)
    admin_name_entry = Entry(passcode_frame, width=30, font=entry_font)
    admin_name_entry.place(x=450, y=150)
    Label(passcode_frame, text="Old Passcode:", bg='white', font=label_font).place(x=150, y=200)
    old_passcode_entry = Entry(passcode_frame, width=30, show='*', font=entry_font)
    old_passcode_entry.place(x=450, y=200)
    Label(passcode_frame, text="* * *  Must be 6 digit passcode.  * * *", bg='white', font=('Arial', 12, 'bold'),
          fg='blue').place(x=450, y=235)
    Label(passcode_frame, text="New Passcode:", bg='white', font=label_font).place(x=150, y=270)
    new_passcode_entry = Entry(passcode_frame, width=30, show='*', font=entry_font)
    new_passcode_entry.place(x=450, y=270)
    Label(passcode_frame, text="Confirm New Passcode:", bg='white', font=label_font).place(x=150, y=320)
    confirm_passcode_entry = Entry(passcode_frame, width=30, show='*', font=entry_font)
    confirm_passcode_entry.place(x=450, y=320)
    update_passcode_button = Button(passcode_frame, text="Update Passcode", command=update_passcode, width=20,
                                    font=label_font, bg="#fd5602", fg="white")
    update_passcode_button.place(x=310, y=400)
    cancel_button = Button(passcode_frame, text="Cancel", width=20, font=label_font, bg="grey", fg="white",
                           command=lambda: [admin_ic_entry.delete(0, END),
                                            admin_id_entry.config(state='normal'),
                                            admin_id_entry.delete(0, END),
                                            admin_name_entry.config(state='normal'),
                                            admin_name_entry.delete(0, END),
                                            old_passcode_entry.delete(0, END),
                                            new_passcode_entry.delete(0, END),
                                            confirm_passcode_entry.delete(0, END)])
    cancel_button.place(x=610, y=400)
    # Edit Business Information Tab
    Label(business_info_frame, text="Business ID:", bg='white', font=label_font).place(x=150, y=55)
    business_id_entry = Entry(business_info_frame, width=12, font=entry_font)
    business_id_entry.place(x=300, y=55)
    Label(business_info_frame, text="Licence No:", bg='white', font=label_font).place(x=580, y=55)
    license_entry = Entry(business_info_frame, width=12, font=entry_font)
    license_entry.place(x=720, y=55)
    Label(business_info_frame, text="Firm Name:", bg='white', font=label_font).place(x=150, y=110)
    firm_name_entry = Entry(business_info_frame, width=40, font=entry_font)
    firm_name_entry.place(x=450, y=110)
    Label(business_info_frame, text="Business Hours:", bg='white', font=label_font).place(x=150, y=160)
    business_hours_entry = Entry(business_info_frame, width=40, font=entry_font)
    business_hours_entry.place(x=450, y=160)
    Label(business_info_frame, text="Location:", bg='white', font=label_font).place(x=150, y=210)
    location_entry = Entry(business_info_frame, width=40, font=entry_font)
    location_entry.place(x=450, y=210)
    Label(business_info_frame, text="Contact:", bg='white', font=label_font).place(x=150, y=260)
    Label(business_info_frame, text="+6", bg='white', font=label_font).place(x=445, y=260)
    contact_entry = Entry(business_info_frame, width=35, font=entry_font)
    contact_entry.place(x=480, y=260)
    Label(business_info_frame, text="Email Address:", bg='white', font=label_font).place(x=150, y=310)
    email_entry = Entry(business_info_frame, width=40, font=entry_font)
    email_entry.place(x=450, y=310)
    # Bind the tab change event
    notebook.bind("<<NotebookTabChanged>>", fetch_business_info)

    def toggle_business_info_editability():
        # Check the current state of the business hour entry
        current_state = business_hours_entry['state']
        # Determine the new state
        new_state = 'normal' if current_state == 'readonly' else 'readonly'
        # Set the state for the relevant entries
        business_hours_entry.config(state=new_state)
        location_entry.config(state=new_state)
        contact_entry.config(state=new_state)
        email_entry.config(state=new_state)
        Label(business_info_frame, text="* * *  Only Certain Data Can Be Edit  * * *", bg='white',
              font=('Arial', 14, 'bold'), fg='blue').place(x=400, y=15)
        edit_business_info_button.place_forget()
        # save function, save changes in database
        save_business_info_button = Button(business_info_frame, text="Save Changes", width=20, font=label_font,
                                           bg="#002400", fg="white",
                                           command=lambda: [
                                               cursor.execute("""UPDATE business_information 
                                                             SET business_hours = ?, location = ?, 
                                                                 contact_no = ?, email_address = ?
                                                             WHERE business_id = ?""",
                                                              (business_hours_entry.get(), location_entry.get(),
                                                               contact_entry.get(), email_entry.get(),
                                                               business_id_entry.get())),
                                               conn.commit(),
                                               business_hours_entry.config(state='readonly'),
                                               location_entry.config(state='readonly'),
                                               contact_entry.config(state='readonly'),
                                               email_entry.config(state='readonly'),
                                               save_business_info_button.place_forget(),
                                               cancel_button.place_forget(),
                                               edit_business_info_button.place(x=450, y=400),
                                               messagebox.showinfo("Success",
                                                                   "Business information updated successfully!")
                                           ])
        save_business_info_button.place(x=310, y=400)
        # reset the changes with database original records
        cancel_button = Button(business_info_frame, text="Cancel", width=20, font=label_font, bg="red", fg="white",
                               command=lambda: [
                                   messagebox.showinfo("Attention", "Changes you made will not be saved."),
                                   fetch_business_info(None),  # Re-fetch data from database
                                   business_hours_entry.config(state='readonly'),
                                   location_entry.config(state='readonly'),
                                   contact_entry.config(state='readonly'),
                                   email_entry.config(state='readonly'),
                                   save_business_info_button.place_forget(),
                                   cancel_button.place_forget(),
                                   edit_business_info_button.place(x=450, y=400)
                               ])
        cancel_button.place(x=610, y=400)

    edit_business_info_button = Button(business_info_frame, text="Edit Business Info", width=20, font=label_font,
                                       bg="#fd5602", fg="white", command=toggle_business_info_editability)
    edit_business_info_button.place(x=450, y=400)
    # Configure the tab size and style
    notebook.tab(0, padding=[10, 10])  # Add padding to the first tab
    notebook.tab(1, padding=[10, 10])  # Add padding to the second tab
    # Configure tab size
    style = ttk.Style()
    style.configure('TNotebook', tabposition='n')  # 'n' for top position
    style.configure('TNotebook.Tab', padding=[30, 10], font=('Arial', 18, 'italic', 'bold'),
                    justify='left')  # Increased padding for longer tabs
    style.configure('TNotebook.Tab', anchor='w')  # 'w' stands for west (left)
    style.configure('TNotebook.Tab', width=150)  # Fixed width for the tab labels
    # Add these lines to configure the selected tab color
    style.map('TNotebook.Tab', foreground=[("selected", "gold4")])


main_frame = Frame(root)
main_frame.pack(side=RIGHT)
main_frame.pack_propagate(False)
main_frame.configure(height=1080, width=1920)
admin_login_register()
# live_location()
root.mainloop()