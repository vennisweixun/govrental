import tkinter as tk
from tkinter import StringVar, Frame, Label, Entry, Button, Radiobutton, filedialog, scrolledtext
import sqlite3
import tkinter.messagebox as messagebox
from tkinter import messagebox as mess
import tkinter.simpledialog as tsd
import geopy
from PIL import Image, ImageTk
import cv2, os
import csv
import smtplib
import random
import json
import datetime
import time
from deepface import DeepFace
import sqlite3
import pickle
import urllib.request
import threading
import webbrowser
from flask import Flask, render_template
from turtle import distance
from urllib import request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import validate_email
from email_validator import validate_email, EmailNotValidError
from tkcalendar import DateEntry
import tkinter.ttk as ttk
import customtkinter as ctk
from flask import request, jsonify
import uuid
import shutil
import sys
import subprocess
from geopy import distance

app = Flask(__name__)
ctk.set_appearance_mode("light")


# 视频背景类
class VideoApp:
    def __init__(self, root, video_path, duration=20):
        self.root = root
        self.video_path = video_path
        self.duration = duration

        # 获取屏幕尺寸并设置全屏
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_width}x{self.screen_height}")

        # 打开视频文件
        self.cap = cv2.VideoCapture(self.video_path)

        if not self.cap.isOpened():
            print("Error: 无法打开视频文件。")
            return

        # 创建一个Canvas来显示视频帧
        self.canvas = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 用于存储图像的引用，避免被垃圾回收
        self.tk_image = None

        # 启动视频播放
        self.play_video()

    def play_video(self):
        ret, frame = self.cap.read()

        if ret:
            # 调整视频帧大小以适应窗口大小
            frame = cv2.resize(frame, (self.screen_width, self.screen_height))

            # 转换颜色 BGR -> RGB（PIL和Tkinter使用RGB格式）
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 转换为PIL图像
            image = Image.fromarray(frame)

            # 转换为ImageTk对象
            self.tk_image = ImageTk.PhotoImage(image)

            # 清除先前的图像
            self.canvas.delete("all")

            # 在Canvas上显示图
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

            # 在指定的持续时间后调用自身以继续播放
            self.root.after(int(self.duration), self.play_video)
        else:
            # 如果视频播放完毕，重头开始播放
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.play_video()


class RentalSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Main")
        self.root.geometry("1920x1080")
        self.root.state("zoomed")

        # Load images
        self.profile_image_original = Image.open(r"C:/Kai Shuang/Logo_Profile.png")
        self.profile_image_resized = self.profile_image_original.resize((32, 32))
        self.profile_image = ImageTk.PhotoImage(self.profile_image_resized)

        self.maybank_logo_original = Image.open(r"C:/Kai Shuang/Maybank-Logo.png")
        self.maybank_logo_resized = self.maybank_logo_original.resize((100, 75))
        self.maybank_logo = ImageTk.PhotoImage(self.maybank_logo_resized)

        self.hsbc_logo_original = Image.open(r"C:/Kai Shuang/hsbc-logo.png")
        self.hsbc_logo_resized = self.hsbc_logo_original.resize((100, 75))
        self.hsbc_logo = ImageTk.PhotoImage(self.hsbc_logo_resized)

        self.create_widgets()

    def create_widgets(self):
        # 创建顶部布局
        self.create_top_bar()

        # 创建中间按钮部分
        self.create_buttons()

    # 创建顶部栏
    def create_top_bar(self):
        self.top_frame = tk.Frame(self.root, bg="#FD5602", height=100)
        self.top_frame.pack(fill=tk.X)

        # 左侧图标
        home_button = tk.Button(self.top_frame, text="🏛", font=("Arial", 20), bg="#FD5602", fg="khaki1",
                                command=self.on_home_click)
        home_button.pack(side=tk.LEFT, padx=10)

        # 中间标题 (使用expand=True将其居中对齐)
        title = tk.Label(self.top_frame, text="Government Rental System", font=("Tw Cen MT Condensed Extra Bold", 24),
                         bg="#FD5602", fg="khaki1")
        title.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        # 右侧 Profile 按钮（带图标）
        profile_button = tk.Button(self.top_frame, image=self.profile_image, bg="#FD5602",
                                   command=self.on_profile_click)
        profile_button.pack(side=tk.LEFT, padx=10)

    # 创建四个按钮
    def create_buttons(self):
        # Create main buttons frame with fixed size and prevent resizing
        self.buttons_frame = tk.Frame(self.root, bg="floral white", width=1920, height=1080)  # Set to full window size
        self.buttons_frame.pack(expand=True, fill="both", padx=20)
        self.buttons_frame.pack_propagate(False)  # Prevent the frame from resizing

        # Create a container frame for all content to maintain layout
        container_frame = tk.Frame(self.buttons_frame, bg="floral white")
        container_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the container

        # Logout button in the top-right corner
        logout_button = ctk.CTkButton(
            self.buttons_frame,  # Attach to buttons_frame instead of container
            text="Back To\nHome Screen",
            font=("Tw Cen MT Condensed Extra Bold", 20),
            fg_color="IndianRed3",
            hover_color="#8B2323",
            text_color="white",
            width=150,
            height=50,
            corner_radius=15,
            command=self.log_out
        )
        logout_button.place(relx=0.98, rely=0.01, anchor="ne")  # Position absolutely in top-right

        # First row of buttons
        row1_frame = tk.Frame(container_frame, bg="floral white")
        row1_frame.pack(pady=20)

        # Create frames and buttons for first row
        attendance_frame = tk.Frame(row1_frame, bg="honeydew", relief="groove", borderwidth=10)
        attendance_frame.pack(side=tk.LEFT, padx=18, pady=10)

        attendance_button = ctk.CTkButton(
            attendance_frame,
            text=" 🕰️Attendance\n \n-------------------------------------------\n   🟢 Clock In   \n   🔴 Clock Out   ",
            font=("Tw Cen MT Condensed Extra Bold", 24),
            fg_color=["#98FF98", "#32CD32"],
            hover_color="medium sea green",
            text_color="black",
            width=300,
            height=250,
            corner_radius=20,
            command=attendance
        )
        attendance_button.pack()

        mystall_frame = tk.Frame(row1_frame, bg="light blue", relief="groove", borderwidth=10)
        mystall_frame.pack(side=tk.LEFT, padx=18, pady=10)

        my_stall_button = ctk.CTkButton(
            mystall_frame,
            text=" 🏪 My Stall\n \n-------------------------------------------\n   📑 View Contract   \n   🤝 Renewal Contract   ",
            font=("Tw Cen MT Condensed Extra Bold", 24),
            fg_color=["#87CEEB", "#4682B4"],  # Sky blue to steel blue
            hover_color="#104E8B",  # Dark blue
            text_color="black",
            width=300,
            height=250,
            corner_radius=20,
            command=self.on_my_stall_click
        )
        my_stall_button.pack()

        notification_frame = tk.Frame(row1_frame, bg="peach puff", relief="groove", borderwidth=10)
        notification_frame.pack(side=tk.LEFT, padx=18, pady=10)

        notification_button = ctk.CTkButton(
            notification_frame,
            text="🔔 My Notification\n \n-------------------------------------------\n 👀 Reminders",
            font=("Tw Cen MT Condensed Extra Bold", 24),
            fg_color=["#FFE4B5", "#FFA07A"],  # Moccasin to light salmon
            hover_color="#CD6839",  # Dark salmon
            text_color="black",
            width=300,
            height=250,
            corner_radius=20,
            command=self.on_show_notification
        )
        notification_button.pack()

        # Second row of buttons
        row2_frame = tk.Frame(container_frame, bg="floral white")
        row2_frame.pack(pady=20)

        feedback_frame = tk.Frame(row2_frame, bg="light steel blue", relief="groove", borderwidth=10)
        feedback_frame.pack(side=tk.LEFT, padx=18, pady=10)

        feedback_button = ctk.CTkButton(
            feedback_frame,
            text=" 📬 Inbox\n \n-------------------------------------------\n   💬 ChatBox   \n   📩 View Response   ",
            font=("Tw Cen MT Condensed Extra Bold", 24),
            fg_color=["#B0C4DE", "#4682B4"],  # Light steel blue to steel blue
            hover_color="#27408B",  # Dark steel blue
            text_color="black",
            width=300,
            height=250,
            corner_radius=20,
            command=self.on_feedback_click
        )
        feedback_button.pack()

        payment_frame = tk.Frame(row2_frame, bg="cornsilk", relief="groove", borderwidth=10)
        payment_frame.pack(side=tk.LEFT, padx=18, pady=10)

        payment_button = ctk.CTkButton(
            payment_frame,
            text=" 💳 Payment\n \n-------------------------------------------\n   🏦 Payment Information   \n   📈 Update Payment Information   ",
            font=("Tw Cen MT Condensed Extra Bold", 24),
            fg_color=["#FFF8DC", "green"],  # Cornsilk to gold
            hover_color="khaki1",  # Dark gold
            text_color="black",
            width=300,
            height=250,
            corner_radius=20,
            command=self.on_payment_click
        )
        payment_button.pack()

        payment_his_frame = tk.Frame(row2_frame, bg="mint cream", relief="groove", borderwidth=10)
        payment_his_frame.pack(side=tk.LEFT, padx=18, pady=10)

        payment_his_button = ctk.CTkButton(
            payment_his_frame,
            text=" 📅 Payment History/Receipt\n \n-------------------------------------------\n   📚 View Payment History  ",
            font=("Tw Cen MT Condensed Extra Bold", 24),
            fg_color=["#F0FFF0", "#90EE90"],  # Honeydew to light green
            hover_color="#2E8B57",  # Dark sea green
            text_color="black",
            width=300,
            height=250,
            corner_radius=20,
            command=self.on_show_payment_history
        )
        payment_his_button.pack()

    def log_out(self):
        self.root.destroy()  # 关闭当前窗口
        root.deiconify()  # 恢复主窗口显示
        show_login_frame()  # 显示登录页面

    def on_feedback_click(self):
        self.buttons_frame.pack_forget()
        self.create_feedback_screen()

    # Creating feedback screen
    def create_feedback_screen(self):
        if hasattr(self, 'history_frame'):
            self.history_frame.pack_forget()
        if hasattr(self, 'central_feedback_frame'):
            self.central_feedback_frame.pack_forget()

        self.central_feedback_frame = tk.Frame(self.root, bg="white")
        self.central_feedback_frame.pack(expand=True, fill="both")

        # Title Label
        title_label = tk.Label(self.central_feedback_frame, text="Tenant - INBOX", font=("Arial", 24, "bold"),
                               bg="white")
        title_label.pack(pady=20)

        # Button Frame
        button_frame = tk.Frame(self.central_feedback_frame, bg="white")
        button_frame.pack(pady=10)

        # Inbox and View Response buttons
        inbox_btn = ctk.CTkButton(
            button_frame,
            text="Inbox",
            font=("Arial", 12),
            fg_color="#FFB05D",
            text_color="black",
            hover_color="#FF9933",
            command=self.show_inbox,
            width=120,
            height=35,
            corner_radius=8
        )
        inbox_btn.pack(side="left", padx=5)

        view_response_btn = ctk.CTkButton(
            button_frame,
            text="View Response",
            font=("Arial", 12),
            fg_color="#FFB05D",
            text_color="black",
            hover_color="#FF9933",
            command=self.show_response,
            width=120,
            height=35,
            corner_radius=8
        )
        view_response_btn.pack(side="left", padx=5)

        # Main content frame
        content_frame = tk.Frame(self.central_feedback_frame, bg="white")
        content_frame.pack(expand=True, fill="both", padx=200, pady=20)

        # To Admin label
        tk.Label(content_frame, text="To : Admin", font=("Arial", 12), bg="white").pack(anchor="w", pady=5)

        # Subject Frame
        subject_frame = tk.Frame(content_frame, bg="white")
        subject_frame.pack(fill="x", pady=5)

        tk.Label(subject_frame, text="Subject : ", font=("Arial", 12), bg="white").pack(side="left")

        # Replace standard Entry with CTkEntry for subject
        self.subject_entry = ctk.CTkEntry(
            subject_frame,
            width=400,
            height=35,
            corner_radius=10,
            font=("Arial", 12),
            placeholder_text="Enter subject"
        )
        self.subject_entry.pack(side="left", fill="x", expand=True)

        # Message Frame with orange border
        message_frame = tk.Frame(content_frame, bg="white")
        message_frame.pack(fill="both", expand=True, pady=10)

        # Replace standard Text with CTkTextbox for message
        self.message_text = ctk.CTkTextbox(
            message_frame,
            height=200,
            corner_radius=10,
            font=("Arial", 12),
            border_color="#FFB05D",
            border_width=2
        )
        self.message_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Attachment Frame
        attachment_frame = tk.Frame(content_frame, bg="white")
        attachment_frame.pack(fill="x", pady=5)

        tk.Label(attachment_frame, text="Attachment : ", font=("Arial", 12), bg="white").pack(side="left")

        # Replace standard Entry with CTkEntry for attachment
        self.attachment_path = StringVar()
        attachment_entry = ctk.CTkEntry(
            attachment_frame,
            textvariable=self.attachment_path,
            width=300,
            height=35,
            corner_radius=10,
            font=("Arial", 12),
            state='readonly'
        )
        attachment_entry.pack(side="left", padx=5)

        browse_btn = ctk.CTkButton(
            attachment_frame,
            text="Browse",
            command=lambda: self.browse_file(self.central_feedback_frame),
            fg_color="#FFB05D",
            text_color="black",
            hover_color="#FF9933",
            width=80,
            height=30,
            corner_radius=8,
            font=("Arial", 12)
        )
        browse_btn.pack(side="left", padx=5)

        # Send Button
        send_btn = ctk.CTkButton(
            content_frame,
            text="Send",
            command=self.submit_feedback,
            fg_color="#FFB05D",
            text_color="black",
            hover_color="#FF9933",
            width=200,
            height=40,
            corner_radius=8,
            font=("Arial", 14)
        )
        send_btn.pack(pady=10)

        # Back Button
        back_btn = ctk.CTkButton(
            content_frame,
            text="Back",
            command=self.go_back,
            fg_color="red",
            text_color="white",
            hover_color="#8B0000",
            width=200,
            height=40,
            corner_radius=8,
            font=("Arial", 14)
        )
        back_btn.pack(pady=5)

    def submit_feedback(self):
        subject = self.subject_entry.get().strip()
        message = self.message_text.get("1.0", tk.END).strip()
        attachment = self.attachment_path.get()

        if not subject or not message:
            messagebox.showerror("Error", "Please enter both subject and message.")
            return

        try:
            conn = sqlite3.connect("govRental.db")
            cursor = conn.cursor()

            # Get tenant ID from login profile
            tenant_id = self.fetch_tenant_id(login_profile['IC_Number'], login_profile['Password'])
            if not tenant_id:
                messagebox.showerror("Error", "Could not retrieve tenant ID")
                return

            # Generate message ID
            message_id = str(int(time.time() * 1000))
            current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Save attachment if provided
            saved_attachment = None
            if attachment:
                saved_attachment = self.save_attachment(attachment)

            # Insert into notif_sent_reply
            cursor.execute("""
                INSERT INTO notif_sent_reply (
                    message_id, sender, recipient, subject, message, 
                    attachment, timestamp_sent_reply
                ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                           (message_id, str(tenant_id), 'Admin', subject, message, saved_attachment, current_timestamp))
            # Insert into notif_inbox
            cursor.execute("""
                INSERT INTO notif_inbox (
                    message_id, sender, recipient, subject, message,
                    attachment, timestamp_receive, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'New')""",
                           (message_id, str(tenant_id), 'Admin', subject, message, saved_attachment, current_timestamp))
            conn.commit()
            messagebox.showinfo("Success", "Feedback submitted successfully!")

            # Clear the form
            self.subject_entry.delete(0, tk.END)
            self.message_text.delete("1.0", tk.END)
            self.attachment_path.set("")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    def browse_file(self, window):
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
            self.attachment_path.set(file_path)

    def save_attachment(self, file_path):
        if not file_path:
            return None

        attachments_dir = "attachments"
        if not os.path.exists(attachments_dir):
            os.makedirs(attachments_dir)

        file_ext = os.path.splitext(file_path)[1]
        new_filename = f"{str(uuid.uuid4())}{file_ext}"
        new_path = os.path.join(attachments_dir, new_filename)

        shutil.copy2(file_path, new_path)
        return new_path

    def show_feedback_tab(self):
        self.feedback_text.delete("1.0", tk.END)  # Clear text for new feedback
        self.history_frame.pack
        self.create_feedback_screen()

    def show_history_tab(self):
        self.central_feedback_frame.pack
        self.create_history_screen()

    def create_history_screen(self):
        if hasattr(self, 'central_feedback_frame'):
            self.central_feedback_frame.pack_forget()
        if hasattr(self, 'history_frame'):
            self.history_frame.pack_forget()

        self.history_frame = tk.Frame(self.root, bg="white", padx=20, pady=30)
        self.history_frame.pack(expand=True)

        # Title
        title_label = tk.Label(self.history_frame, text="FEEDBACK HISTORY", font=("Arial", 24, "bold"), bg="white")
        title_label.pack(pady=10)

        # Tab buttons frame
        tab_frame = tk.Frame(self.history_frame, bg="white")
        tab_frame.pack(pady=10)

        # Replace standard buttons with CTkButton
        feedback_tab = ctk.CTkButton(
            tab_frame,
            text="Feedback",
            font=("Arial", 12),
            fg_color="#FFB05D",
            text_color="black",
            hover_color="#FF9933",
            command=self.show_feedback_tab,
            width=120,
            height=35,
            corner_radius=8
        )
        feedback_tab.grid(row=0, column=0, padx=10)

        history_tab = ctk.CTkButton(
            tab_frame,
            text="View Response",
            font=("Arial", 12),
            fg_color="#FFB05D",
            text_color="black",
            hover_color="#FF9933",
            command=self.show_history_tab,
            width=120,
            height=35,
            corner_radius=8
        )
        history_tab.grid(row=0, column=1, padx=10)

        # Date frame
        date_frame = tk.Frame(self.history_frame, bg="white")
        date_frame.pack(pady=5)

        submit_date_label = tk.Label(date_frame, text="Submit Date", font=("Arial", 12), bg="#FFB05D", fg="black")
        submit_date_label.pack(side=tk.LEFT, padx=5)

        # Create a frame to wrap the DateEntry for styling
        date_wrapper = tk.Frame(date_frame, bg="white", highlightbackground="#3E454A",
                                highlightthickness=1, bd=0)
        date_wrapper.pack(side=tk.LEFT)

        # Add DateEntry with rounded appearance
        self.submit_date_entry = DateEntry(
            date_wrapper,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=0,
            font=("Arial", 10),
            selectbackground='gray75',
            selectforeground='black',
            normalbackground='white',
            normalforeground='black',
            highlightthickness=0,
            relief="flat"
        )
        self.submit_date_entry.pack(padx=1, pady=1)

        # Add a button to fetch and display records for the selected date
        def fetch_date_records():
            selected_date = self.submit_date_entry.get_date()
            formatted_date = selected_date.strftime("%Y-%m-%d")

            try:
                conn = sqlite3.connect("govRental.db")
                cursor = conn.cursor()
                tenant_id = 1  # Placeholder for the tenant currently logged in

                cursor.execute(
                    """SELECT Feedback, Response, Feedback_Date, Response_Date 
                       FROM Feedback_Manage 
                       WHERE Tenant_ID = ? AND Feedback_Date = ?""",
                    (tenant_id, formatted_date)
                )
                feedback_entries = cursor.fetchall()

                # Clear existing text
                history_display.delete('1.0', tk.END)

                if feedback_entries:
                    for entry in feedback_entries:
                        feedback_text = f"Feedback: {entry[0]}\nResponse: {entry[1]}\nDate: {entry[2]}\nResponse Date: {entry[3]}\n\n"
                        history_display.insert(tk.END, feedback_text)
                else:
                    history_display.insert(tk.END, "No feedback records found for the selected date.")

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
            finally:
                if conn:
                    conn.close()

        # Add Filter button
        filter_button = ctk.CTkButton(
            date_frame,
            text="Filter",
            font=("Arial", 12),
            fg_color="#FFB05D",
            text_color="black",
            hover_color="#FF9933",
            command=fetch_date_records,
            width=100,
            height=30,
            corner_radius=8
        )
        filter_button.pack(side=tk.LEFT, padx=10)

        # History display box
        history_display = scrolledtext.ScrolledText(self.history_frame, width=60, height=20, wrap=tk.WORD,
                                                    font=("Arial", 10))
        history_display.pack(pady=10)

        # Display all feedback initially
        try:
            conn = sqlite3.connect("govRental.db")
            cursor = conn.cursor()
            tenant_id = 1  # Placeholder for the tenant currently logged in

            cursor.execute(
                "SELECT Feedback, Response, Feedback_Date, Response_Date FROM Feedback_Manage WHERE Tenant_ID = ?",
                (tenant_id,)
            )
            feedback_entries = cursor.fetchall()

            for entry in feedback_entries:
                feedback_text = f"Feedback: {entry[0]}\nResponse: {entry[1]}\nDate: {entry[2]}\nResponse Date: {entry[3]}\n\n"
                history_display.insert(tk.END, feedback_text)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

        # Back button
        back_button = ctk.CTkButton(
            self.history_frame,
            text="Back",
            font=("Arial", 12),
            fg_color="orange",
            text_color="black",
            hover_color="#FF8C00",
            command=self.back_feedback,
            width=200,
            height=40,
            corner_radius=8
        )
        back_button.pack(pady=10)

    def go_back(self):
        self.central_feedback_frame.pack_forget()

        self.buttons_frame.pack(fill=tk.X)

    def back_feedback(self):
        self.history_frame.pack_forget()

        self.buttons_frame.pack(fill=tk.X)

    def on_show_notification(self):
        self.buttons_frame.pack_forget()

        self.notification_frame = tk.Frame(self.root, bg="floral white")
        self.notification_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)

        def fetch_dates(read_status):
            """Fetch dates based on the `read` status of reminders."""
            try:
                conn = sqlite3.connect("govRental.db")
                cursor = conn.cursor()

                tenant_ic_number = login_profile.get('IC_Number')  # Using Tenant_Username instead of IC_Number
                cursor.execute("SELECT Tenant_ID FROM Tenant WHERE Tenant_IC_Number= ?", (tenant_ic_number,))
                tenant_id_result = cursor.fetchone()

                if not tenant_id_result:
                    return []

                tenant_id = tenant_id_result[0]

                cursor.execute(f"""
                    SELECT DISTINCT date(Date_Time) FROM Reminders
                    WHERE Tenant_ID = ? AND read = ?
                    ORDER BY Date_Time ASC
                """, (tenant_id, read_status))
                dates = [row[0] for row in cursor.fetchall()]
                return dates
            except Exception as e:
                print(f"Error fetching dates: {e}")
                return []
            finally:
                conn.close()

        def check_reminder(reminder_label, selected_date, read_status):
            """Fetch and display reminders for the selected date."""
            try:
                conn = sqlite3.connect("govRental.db")
                cursor = conn.cursor()

                tenant_ic_number = login_profile.get('IC_Number')  # Using Tenant_Username instead of IC_Number
                cursor.execute("SELECT Tenant_ID FROM Tenant WHERE Tenant_IC_Number= ?", (tenant_ic_number,))
                tenant_id_result = cursor.fetchone()

                if not tenant_id_result:
                    reminder_label.config(text="Tenant not found.")
                    return

                tenant_id = tenant_id_result[0]

                cursor.execute(f"""
                    SELECT Reminder_ID, Message, Date_Time FROM Reminders
                    WHERE Tenant_ID = ? AND date(Date_Time) = ? AND read = ?
                    ORDER BY Date_Time ASC
                """, (tenant_id, selected_date, read_status))
                reminders = cursor.fetchall()

                if reminders:
                    reminder_messages = ""
                    for reminder_id, message, reminder_datetime in reminders:
                        reminder_messages += f"Reminder: {message}\nScheduled for: {reminder_datetime}\n\n"

                        if read_status == 0:  # Mark as read if it's an unread reminder
                            cursor.execute("UPDATE Reminders SET read = 1 WHERE Reminder_ID = ?", (reminder_id,))
                            conn.commit()

                    reminder_label.config(text=reminder_messages)

                    if read_status == 0:  # Refresh the unread dates list if checking unread reminders
                        refresh_dates(fetch_dates(0))
                else:
                    reminder_label.config(text="No reminders found for the selected date.")

            except Exception as e:
                reminder_label.config(text=f"Error checking reminders: {e}")
            finally:
                conn.close()

        def refresh_dates(dates):
            """Refresh the listbox with the given dates."""
            date_listbox.delete(0, tk.END)
            for date in dates:
                date_listbox.insert(tk.END, date)

        def display_reminder_window():
            global date_listbox  # Allow date_listbox to be used across functions

            # Left frame for displaying dates
            left_frame = tk.Frame(self.notification_frame, width=300, height=400, bg='#FFB05D')
            left_frame.pack(side='left', fill='both')

            date_label = tk.Label(left_frame, text="Available Dates:", bg='#FFB05D', font=('Arial', 14, 'bold'))
            date_label.pack(pady=10)

            date_listbox = tk.Listbox(left_frame, font=('Arial', 14, 'bold'), height=20, width=20)
            date_listbox.pack(pady=5, padx=10)

            # Right frame for displaying reminders
            right_frame = tk.Frame(self.notification_frame, bg='white')
            right_frame.pack(side='right', fill='both', expand=True)

            reminder_label = tk.Label(
                right_frame,
                text="Select a date to view reminders.",
                bg='white',
                font=("Arial", 14, 'bold'),
                wraplength=250,
                justify="left",
            )
            reminder_label.pack(pady=100, padx=10)

            # Fetch and populate the Listbox with unread dates
            refresh_dates(fetch_dates(0))

            # Event handler for date selection
            def on_date_select(event, read_status=0):
                selected_date = date_listbox.get(date_listbox.curselection())
                check_reminder(reminder_label, selected_date, read_status)

            date_listbox.bind("<<ListboxSelect>>", lambda event: on_date_select(event, read_status=0))

            # History label for displaying read reminders
            def show_history():
                refresh_dates(fetch_dates(1))  # Fetch read reminders (1 = read)
                reminder_label.config(text="Select a date to view history.")

                # Update event handler to load history reminders
                date_listbox.bind("<<ListboxSelect>>", lambda event: on_date_select(event, read_status=1))

                # Add a "Back to Notifications" label
                back_label.pack(side='bottom', pady=5)

            # "Back to Notifications" label
            def back_to_notifications():
                refresh_dates(fetch_dates(0))  # Fetch unread reminders (0 = unread)
                reminder_label.config(text="Select a date to view reminders.")

                # Update event handler to load unread reminders
                date_listbox.bind("<<ListboxSelect>>", lambda event: on_date_select(event, read_status=0))
                back_label.pack_forget()  # Hide the "Back to Notifications" label

            back_label = tk.Label(left_frame, text="Back to Notifications", bg='#FFB05D', fg='black',
                                  font=("Helvetica", 12, "bold"), cursor="hand2")
            back_label.bind("<Button-1>", lambda e: back_to_notifications())

            history_label = tk.Label(left_frame, text="History", bg='#FFB05D', fg='black',
                                     font=("Helvetica", 12, "bold"),
                                     cursor="hand2")
            history_label.pack(side='bottom', pady=100)
            history_label.bind("<Button-1>", lambda e: show_history())

        display_reminder_window()

    def on_show_payment_history(self):
        self.buttons_frame.pack_forget()

        self.show_payment_history()

    def show_payment_history(self):
        # Open a new window for payment history
        if hasattr(self, "history_frame"):
            self.history_frame.destroy()  # Clear existing frame if present

        self.history_frame = tk.Frame(self.root, bg="white")
        self.history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame for Date Selection
        date_frame = tk.Frame(self.history_frame, bg="white")
        date_frame.pack(fill=tk.X, pady=(10, 0), padx=10)

        # Add a label and date selection dropdown
        date_label = tk.Label(date_frame, text="Select Date:", font=("Arial", 12), bg="white")
        date_label.pack(side=tk.LEFT, padx=(0, 10))

        # Create a frame to wrap the DateEntry for styling
        date_wrapper = tk.Frame(date_frame, bg="white", highlightbackground="#3E454A",
                                highlightthickness=1, bd=0)
        date_wrapper.pack(side=tk.LEFT)

        # Modified DateEntry with rounded appearance
        date_entry = DateEntry(
            date_wrapper,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=0,
            font=("Arial", 10),
            selectbackground='gray75',
            selectforeground='black',
            normalbackground='white',
            normalforeground='black',
            highlightthickness=0,
            relief="flat"
        )
        date_entry.pack(padx=1, pady=1)

        # Add a button to fetch and display records for the selected date
        def fetch_records():
            # Clear existing records in the Treeview
            for item in tree.get_children():
                tree.delete(item)

            # Get selected date and format it to match the database format with two-digit year
            selected_date = date_entry.get_date().strftime("%m/%d/%y")
            print("Selected date:", selected_date)  # For debugging

            # Fetch data from the Payment table for the selected date
            conn = sqlite3.connect("govRental.db")
            cursor = conn.cursor()

            # Retrieve payment history records for the selected date
            query = """
            SELECT Transaction_Date, Rental_Amount, Bank_Slip 
            FROM Payment_Manage
            WHERE Transaction_Date = ?
            """
            cursor.execute(query, (selected_date,))
            rows = cursor.fetchall()

            if rows:  # Check if any rows are returned
                # Insert each row into the Treeview
                for row in rows:
                    tree.insert("", tk.END, values=row)
            else:
                print("No records found for the selected date.")  # Debugging output

            # Close the database connection
            conn.close()

        # Filter button
        filter_button = ctk.CTkButton(
            date_frame,
            text="Filter",
            command=fetch_records,
            font=("Arial", 12),
            fg_color="#4B0082",  # Indigo color
            text_color="black",
            hover_color="#2E0854",  # Darker indigo for hover
            width=120,
            height=35,
            corner_radius=8
        )
        filter_button.pack(side=tk.LEFT, padx=10)

        # Logout button
        logout_button = ctk.CTkButton(
            date_frame,
            text="Log Out",
            command=self.payment_his_log_out,
            font=("Arial", 12),
            fg_color="#DC143C",  # Crimson red
            text_color="black",
            hover_color="#8B0000",  # Darker red for hover
            width=120,
            height=35,
            corner_radius=8
        )
        logout_button.pack(side=tk.RIGHT, padx=10)

        # Frame for Treeview and Scrollbars
        tree_frame = tk.Frame(self.history_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        # Style configuration for Treeview
        style = ttk.Style()
        style.configure("Treeview",
                        background="white",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="white")
        style.configure("Treeview.Heading",
                        background="gray75",
                        foreground="black",
                        relief="flat")
        style.map("Treeview.Heading",
                  relief=[('active', 'groove'), ('pressed', 'sunken')])

        # Define Treeview Columns
        columns = ("Transaction_Date", "Rental_Amount", "Bank_Slip")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="Treeview")

        # Set up column headings and widths
        tree.heading("Transaction_Date", text="Date")
        tree.heading("Rental_Amount", text="Amount")
        tree.heading("Bank_Slip", text="Receipt")

        # Set column widths
        tree.column("Transaction_Date", width=200, anchor="center")
        tree.column("Rental_Amount", width=100, anchor="center")
        tree.column("Bank_Slip", width=400, anchor="center")

        # Add Scrollbars to Treeview
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)

    # End of show_payment_history function

    def payment_his_log_out(self):
        self.history_frame.pack_forget()

        # 重新显示按钮和视频框架
        self.buttons_frame.pack(fill=tk.X)

    def create_stall_frame(self, Stall_ID):
        # Create StringVar instances
        address_image_var = StringVar()
        stall_address_var = StringVar()
        postcode_var = StringVar()
        rental_period_var = StringVar()
        contract_start_date_var = StringVar()
        contract_end_date_var = StringVar()
        rental_amount_var = StringVar()
        deposit_amount_var = StringVar()

        # Fetch stall information from the database using Stall_ID
        try:
            conn = sqlite3.connect("govRental.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Address_Image, Stall_Address, Postcode, Rental_Period, Contract_Start_Date,
                       Contract_End_Date, Rental_Amount, Deposit_Amount, Contract_File
                FROM Stall
                WHERE Stall_ID = ?
            """, (Stall_ID,))
            stall_info = cursor.fetchone()

            if stall_info:
                # Set the values to StringVars
                address_image_var.set(stall_info[0])
                stall_address_var.set(stall_info[1])
                postcode_var.set(stall_info[2])
                rental_period_var.set(stall_info[3])
                contract_start_date_var.set(stall_info[4])
                contract_end_date_var.set(stall_info[5])
                rental_amount_var.set(stall_info[6])
                deposit_amount_var.set(stall_info[7])
                contract_file = stall_info[8]
        except Exception as e:
            messagebox.showerror("Database Error", f"Error fetching stall information: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

        # Create the main stall frame
        self.stall_frame = tk.Frame(self.root, bg="floral white", padx=50, pady=50)
        self.stall_frame.pack(expand=True)

        # Top title and image section
        self.upload_stall_frame = tk.Frame(self.stall_frame, bg="floral white", padx=60, pady=60)
        self.upload_stall_frame.pack()

        stall_label = tk.Label(self.upload_stall_frame, text="My Stall", font=("Times New Roman", 30, "bold"),
                               bg="floral white")
        stall_label.grid(row=0, column=1, columnspan=2, pady=20)

        # Load and resize the image
        image = Image.open(address_image_var.get())
        image = image.resize((300, 300), Image.Resampling.LANCZOS)
        image_tk = ImageTk.PhotoImage(image)

        # Image label
        address_image_label = tk.Label(self.upload_stall_frame, image=image_tk, bg="#C7D3FF")
        address_image_label.image = image_tk
        address_image_label.grid(row=1, column=0, rowspan=6, padx=1, pady=10)

        # Label and Entry fields in a grid layout
        tk.Label(self.upload_stall_frame, text="Stall Address", bg="white", font=('Times New Roman', 14)).grid(row=1,
                                                                                                               column=1,
                                                                                                               sticky="e",
                                                                                                               padx=5,
                                                                                                               pady=5)
        ctk.CTkEntry(self.upload_stall_frame, textvariable=stall_address_var, font=('Times New Roman', 16),
                     state="readonly",
                     width=200, height=60, corner_radius=10).grid(row=1, column=2, padx=5, pady=5)

        tk.Label(self.upload_stall_frame, text="Postcode", bg="white", font=('Times New Roman', 14)).grid(row=2,
                                                                                                          column=1,
                                                                                                          sticky="e",
                                                                                                          padx=5,
                                                                                                          pady=5)
        ctk.CTkEntry(self.upload_stall_frame, textvariable=postcode_var, font=('Times New Roman', 16), state="readonly",
                     width=200, height=30, corner_radius=10).grid(row=2, column=2, padx=5, pady=5)

        tk.Label(self.upload_stall_frame, text="Rental Amount", bg="white", font=('Times New Roman', 14)).grid(row=3,
                                                                                                               column=1,
                                                                                                               sticky="e",
                                                                                                               padx=5,
                                                                                                               pady=5)
        ctk.CTkEntry(self.upload_stall_frame, textvariable=rental_amount_var, font=('Times New Roman', 16),
                     state="readonly",
                     width=200, height=30, corner_radius=10).grid(row=3, column=2, padx=5, pady=5)

        tk.Label(self.upload_stall_frame, text="Deposit Amount", bg="white", font=('Times New Roman', 14)).grid(row=4,
                                                                                                                column=1,
                                                                                                                sticky="e",
                                                                                                                padx=5,
                                                                                                                pady=5)
        ctk.CTkEntry(self.upload_stall_frame, textvariable=deposit_amount_var, font=('Times New Roman', 16),
                     state="readonly",
                     width=200, height=30, corner_radius=10).grid(row=4, column=2, padx=5, pady=5)

        tk.Label(self.upload_stall_frame, text="Contract Start Date", bg="white", font=('Times New Roman', 14)).grid(
            row=5, column=1,
            sticky="e", padx=5,
            pady=5)
        ctk.CTkEntry(self.upload_stall_frame, textvariable=contract_start_date_var, font=('Times New Roman', 16),
                     state="readonly",
                     width=200, height=30, corner_radius=10).grid(row=5, column=2, padx=5, pady=5)

        tk.Label(self.upload_stall_frame, text="Contract End Date", bg="white", font=('Times New Roman', 14)).grid(
            row=6, column=1,
            sticky="e", padx=5,
            pady=5)
        ctk.CTkEntry(self.upload_stall_frame, textvariable=contract_end_date_var, font=('Times New Roman', 16),
                     state="readonly",
                     width=200, height=30, corner_radius=10).grid(row=6, column=2, padx=5, pady=5)

        tk.Label(self.upload_stall_frame, text="Rental Period", bg="white", font=('Times New Roman', 14)).grid(row=7,
                                                                                                               column=1,
                                                                                                               sticky="e",
                                                                                                               padx=5,
                                                                                                               pady=5)
        ctk.CTkEntry(self.upload_stall_frame, textvariable=rental_period_var, font=('Times New Roman', 16),
                     state="readonly",
                     width=200, height=30, corner_radius=10).grid(row=7, column=2, padx=5, pady=5)

        # Function to open contract file in browser
        def open_contract_file():
            if contract_file:
                import webbrowser
                webbrowser.open_new(contract_file)
            else:
                messagebox.showerror("Error", "No contract file available.")

        # Buttons
        btn_view_contract = ctk.CTkButton(self.upload_stall_frame, text="View Contract", font=("Arial", 12),
                                          fg_color='#FFCC80', text_color="black",
                                          hover_color='#FFA500', width=200, height=40, corner_radius=8,
                                          command=open_contract_file)
        btn_view_contract.grid(row=8, column=1, pady=10, columnspan=2)

        btn_back = ctk.CTkButton(self.upload_stall_frame, text="Back", font=("Arial", 12), fg_color='red',
                                 text_color="black", hover_color='#8B0000',
                                 width=200, height=40, corner_radius=8, command=self.stall_log_out)
        btn_back.grid(row=9, column=1, pady=10, columnspan=2)

    def stall_log_out(self):
        self.stall_frame.pack_forget()
        self.upload_stall_frame.pack_forget()

        # 重新显示按钮和视框架
        self.buttons_frame.pack(fill=tk.X)

    def on_home_click(self):
        # Destroy all possible frames
        frames_to_check = [
            'stall_frame',
            'history_frame',
            'central_frame',
            'upload_payment_frame',
            'upload_stall_frame',
            'central_feedback_frame',
            'response_frame',
            'profile_frame',
            'payment_frame',
            'upload_frame',
            'notification_frame'
        ]

        # Destroy each frame if it exists
        for frame_name in frames_to_check:
            if hasattr(self, frame_name):
                frame = getattr(self, frame_name)
                frame.destroy()
                delattr(self, frame_name)  # Remove the reference

        # Hide the buttons frame if it exists
        if hasattr(self, 'buttons_frame'):
            self.buttons_frame.pack_forget()

        # Recreate and show the buttons frame
        self.create_buttons()

    def on_profile_click(self):
        # Hide all possible frames
        if hasattr(self, 'buttons_frame'):
            self.buttons_frame.pack_forget()
        if hasattr(self, 'stall_frame'):
            self.stall_frame.pack_forget()
        if hasattr(self, 'history_frame'):
            self.history_frame.pack_forget()
        if hasattr(self, 'central_frame'):
            self.central_frame.pack_forget()
        if hasattr(self, 'upload_payment_frame'):
            self.upload_payment_frame.pack_forget()
        if hasattr(self, 'upload_stall_frame'):
            self.upload_stall_frame.pack_forget()
        if hasattr(self, 'central_feedback_frame'):
            self.central_feedback_frame.pack_forget()
        if hasattr(self, 'history_frame'):
            self.history_frame.pack_forget()
        if hasattr(self, 'response_frame'):
            self.response_frame.pack_forget()
        if hasattr(self, 'profile_frame'):
            self.profile_frame.pack_forget()
        if hasattr(self, 'notification_frame'):
            self.notification_frame.pack_forget()
        self.profile()

    def profile(self):
        def fetch_tenant_data(Tenant_ID):
            conn = sqlite3.connect("govRental.db")
            cursor = conn.cursor()

            # Fetch tenant data
            cursor.execute(
                "SELECT Tenant_Username, Tenant_IC_Number, Tenant_Gender ,Tenant_Email_Address , Tenant_Phone_Number , Tenant_Password  FROM Tenant WHERE Tenant_ID = ?",
                (Tenant_ID,))
            tenant_data = cursor.fetchone()

            return tenant_data

        def update_tenant_data(Tenant_ID, new_Username, new_IC_Number, new_Gender, new_Email_Address, new_Phone_Number,
                               new_Password):
            conn = sqlite3.connect("govRental.db")
            cursor = conn.cursor()

            try:
                # Check if the new username is already in use by another tenant
                cursor.execute("SELECT Tenant_ID FROM Tenant WHERE Tenant_Username = ? AND Tenant_ID != ?",
                               (new_IC_Number, Tenant_ID))
                existing_tenant = cursor.fetchone()

                if existing_tenant:
                    messagebox.showerror("IC Number Error",
                                         "IC Number already exists. Please choose a different username.")
                    return False

                # Update tenant data
                cursor.execute(
                    "UPDATE Tenant SET Tenant_Username = ?,Tenant_IC_Number=?, Tenant_Gender=? ,Tenant_Email_Address = ?, Tenant_Phone_Number = ?, Tenant_Password = ? WHERE Tenant_ID = ?",
                    (new_Username, new_IC_Number, new_Gender, new_Email_Address, new_Phone_Number, new_Password,
                     Tenant_ID))
                conn.commit()

                # Update logged_in_user
                login_profile['Tenant_IC_Number'] = new_IC_Number
                login_profile['Tenant_Password'] = new_Password

                return True

            except sqlite3.Error as e:
                print(f"SQLite error: {e}")
                return False

        # Function to load tenant data into labels and allow editing
        def load_tenant_data_view(Tenant_ID):
            tenant_data = fetch_tenant_data(Tenant_ID)
            if tenant_data:
                username_var.set(tenant_data[0])
                ic_number_var.set(tenant_data[1])
                gender_var.set(tenant_data[2])
                email_address_var.set(tenant_data[3])
                phone_number_var.set(tenant_data[4])
                password_var.set(tenant_data[5])

        # Function to save tenant data
        def save_tenant_data(Tenant_ID):
            username = username_var.get()
            ic_number = ic_number_var.get  # 强制转换为字符串，确保包括前导0
            gender = gender_var.get()
            phone_number = phone_number_var.get()
            email_address = email_address_var.get()
            password = password_var.get()
            if update_tenant_data(Tenant_ID, username, ic_number, gender, email_address, phone_number, password):
                load_tenant_data_view(Tenant_ID)
                messagebox.showinfo("Success", "Tenant information updated successfully!")
            else:
                load_tenant_data_view(Tenant_ID)

        Tenant_ID = self.fetch_tenant_id(login_profile['IC_Number'], login_profile['Password'])
        # Create entry variables
        username_var = StringVar()
        ic_number_var = StringVar()
        gender_var = StringVar()
        email_address_var = StringVar()
        phone_number_var = StringVar()
        password_var = StringVar()
        # Load tenant data into the entry variables
        load_tenant_data_view(Tenant_ID)
        self.profile_frame = tk.Frame(self.root, bg="#f0f0f0", padx=100, pady=100)
        self.profile_frame.pack(expand=True)
        profile_frame = tk.Frame(self.profile_frame, bg="#FFCC80", padx=100, pady=130)
        profile_frame.pack()
        title_label = tk.Label(profile_frame, text="My Profile", font=("Arial", 25, "bold"), bg="#FFCC80")
        title_label.grid(row=0, column=0, pady=10)
        title_label = tk.Label(profile_frame, text=" 👤 Username:", font=("Arial", 20),
                               bg='#FFCC80')
        title_label.grid(row=1, column=0, pady=20)
        title_label = tk.Label(profile_frame, text=" 🪪 IC Number:", font=("Arial", 20),
                               bg='#FFCC80')
        title_label.grid(row=2, column=0, pady=20)
        title_label = tk.Label(profile_frame, text=" ⚥ Gender:", font=("Arial", 20), bg='#FFCC80')
        title_label.grid(row=3, column=0, pady=20)
        title_label = tk.Label(profile_frame, text=" 📞 Phone Number:", font=("Arial", 20),
                               bg='#FFCC80')
        title_label.grid(row=4, column=0, pady=20)
        title_label = tk.Label(profile_frame, text=" 📧 Email Address:", font=("Arial", 20),
                               bg='#FFCC80')
        title_label.grid(row=5, column=0, pady=20)
        title_label = tk.Label(profile_frame, text=" 🔒 Password:", font=("Arial", 20),
                               bg='#FFCC80')
        title_label.grid(row=6, column=0, pady=20)
        # Create labels and entry fields on the canvas
        username_entry = ctk.CTkEntry(profile_frame, textvariable=username_var, font=("Arial", 20),
                                      width=250, height=30, corner_radius=10, state="readonly")
        username_entry.grid(row=1, column=1, padx=5, pady=20)
        Ic_number_entry = ctk.CTkEntry(profile_frame, textvariable=ic_number_var, font=("Arial", 20),
                                       width=250, height=30, corner_radius=10, state="readonly")
        Ic_number_entry.grid(row=2, column=1, padx=5, pady=20)
        Gender_entry = ctk.CTkEntry(profile_frame, textvariable=gender_var, font=("Arial", 20),
                                    width=250, height=30, corner_radius=10, state="readonly")
        Gender_entry.grid(row=3, column=1, padx=5, pady=20)
        phone_entry = ctk.CTkEntry(profile_frame, textvariable=phone_number_var, font=("Arial", 20),
                                   width=250, height=30, corner_radius=10, state="readonly")
        phone_entry.grid(row=4, column=1, padx=5, pady=20)
        email_address_entry = ctk.CTkEntry(profile_frame, textvariable=email_address_var,
                                           font=("Arial", 20), width=250, height=30,
                                           corner_radius=10, state="readonly")
        email_address_entry.grid(row=5, column=1, padx=5, pady=20)
        password_entry = ctk.CTkEntry(profile_frame, textvariable=password_var, show='*',
                                      font=("Arial", 20), width=250, height=30,
                                      corner_radius=10, state="readonly")
        password_entry.grid(row=6, column=1, padx=5, pady=20)
        btn_change_password = ctk.CTkButton(profile_frame, text="Change Password",
                                            font=("Arial", 20), text_color="black", fg_color="#FD5602",
                                            hover_color="orange", width=200, height=40,
                                            corner_radius=8, command=self.change_password_window)
        btn_change_password.grid(row=7, column=0, padx=20, pady=10)
        btn_logout = ctk.CTkButton(profile_frame, text="Logout", font=("Arial", 20), text_color="black",
                                   fg_color="#FD5602", hover_color="orange", width=200,
                                   height=40, corner_radius=8, command=self.back_click)
        btn_logout.grid(row=7, column=1, padx=20, pady=10)

    def back_click(self):
        # 隐藏支付界面
        self.profile_frame.pack_forget()

        # 重新显示按钮和视频框架
        self.buttons_frame.pack(fill=tk.X)

    def change_password_window(self):
        # 创建一个新窗口
        change_password_window = tk.Toplevel()
        change_password_window.title("Change Password")
        change_password_window.geometry("500x300")
        change_password_window.config(bg='floral white')

        # 创建密码输入框
        label_new_password = Label(change_password_window, text="New Password:", font=("Times New Roman", 15),
                                   bg='white')
        label_new_password.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        # Replace standard Entry with CTkEntry
        entry_new_password = ctk.CTkEntry(
            change_password_window,
            show='*',
            font=("Times New Roman", 15),
            width=200,
            height=30,
            corner_radius=10
        )
        entry_new_password.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        label_confirm_password = Label(change_password_window, text="Confirm Password:", font=("Times New Roman", 15),
                                       bg='white')
        label_confirm_password.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        # Replace standard Entry with CTkEntry
        entry_confirm_password = ctk.CTkEntry(
            change_password_window,
            show='*',
            font=("Times New Roman", 15),
            width=200,
            height=30,
            corner_radius=10
        )
        entry_confirm_password.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # 创建保存按钮
        btn_save_password = ctk.CTkButton(
            change_password_window,
            text="Save Password",
            font=("Times New Roman", 15),
            fg_color='#FFCC80',
            text_color="black",
            hover_color='#FFA500',
            command=lambda: self.save_password(entry_new_password, entry_confirm_password, change_password_window),
            width=150,
            height=40,
            corner_radius=8
        )
        btn_save_password.grid(row=2, columnspan=2, pady=20)

        btn_cancel = ctk.CTkButton(
            change_password_window,
            text="Cancel",
            font=("Times New Roman", 15),
            fg_color='#FFCC80',
            text_color="black",
            hover_color='#FFA500',
            command=change_password_window.destroy,
            width=150,
            height=40,
            corner_radius=8
        )
        btn_cancel.grid(row=3, columnspan=2, pady=10)

    def save_password(self, entry_new_password, entry_confirm_password, window):
        new_password = entry_new_password.get()
        confirm_password = entry_confirm_password.get()

        # 查密码是否配
        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        if len(new_password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long!")
            return

        try:
            # 更新数据库中的密码
            Tenant_ID = self.fetch_tenant_id(login_profile['IC_Number'], login_profile['Password'])
            conn = sqlite3.connect("govRental.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE Tenant SET Tenant_Password = ? WHERE Tenant_ID = ?", (new_password, Tenant_ID))
            conn.commit()
            messagebox.showinfo("Success", "Password updated successfully!")

            # 更新全局变量
            login_profile['Password'] = new_password

            # 关闭窗口
            window.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error updating password: {e}")

    # 支付按钮被点击时的功能
    def on_payment_click(self):
        # 隐藏按钮和框架
        self.buttons_frame.pack_forget()

        # 创建支付界面
        self.create_payment_screen()

    # 创建支界面
    def create_payment_screen(self):
        # 创建中央框架
        self.central_frame = tk.Frame(self.root, bg="white", padx=80, pady=80)
        self.central_frame.pack(expand=True)

        self.payment_frame = tk.Frame(self.central_frame, bg="white", padx=70, pady=70)
        self.payment_frame.pack()

        # 标题
        title_label = tk.Label(self.payment_frame, text="ONLINE BANKING", font=("Arial", 32, "bold"), bg="white")
        title_label.grid(row=0, column=0, columnspan=2, pady=20)

        # 支付信息框架
        info_frame = tk.Frame(self.payment_frame, bg="lightgrey", padx=100, pady=100)
        info_frame.grid(row=1, column=0, columnspan=2)

        instruction_label = tk.Label(info_frame, text="Please select Interbank Giro (IBG) mode", font=("Arial", 20),
                                     bg="lightgrey")
        instruction_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Maybank信息和logo
        maybank_logo_label = tk.Label(info_frame, image=self.maybank_logo, bg="lightgrey")
        maybank_logo_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        maybank_details = tk.Label(info_frame, text="Account No: 5071 3424 2666\nPayee Name: XXXXXXX",
                                   font=("Arial", 18), bg="lightgrey")
        maybank_details.grid(row=1, column=1, sticky="w")

        # HSBC信和logo
        hsbc_logo_label = tk.Label(info_frame, image=self.hsbc_logo, bg="lightgrey")
        hsbc_logo_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        hsbc_details = tk.Label(info_frame, text="Account No: 105 154421 101\nPayee Name: XXXXXXX", font=("Arial", 18),
                                bg="lightgrey")
        hsbc_details.grid(row=3, column=1, sticky="w")

        # 指示标签
        reference_label = tk.Label(self.payment_frame,
                                   text="Please specify your User ID or IC/Passport as reference during payment transfer.",
                                   font=("Arial", 18), fg="red", bg="white")
        reference_label.grid(row=2, column=0, columnspan=2, pady=10)

        upload_label = tk.Label(self.payment_frame,
                                text="Click on Upload Payment button once you have completed the payment.",
                                font=("Arial", 18), fg="black", bg="white")
        upload_label.grid(row=3, column=0, columnspan=2, pady=10)

        # Replace standard buttons with CTkButton
        # 上传付款按钮
        upload_button = ctk.CTkButton(
            self.payment_frame,
            text="UPLOAD PAYMENT",
            font=("Arial", 16),
            fg_color="red",
            text_color="black",
            hover_color="#8B0000",  # Darker red for hover
            command=self.create_upload_payment_screen,
            width=200,
            height=40,
            corner_radius=8
        )
        upload_button.grid(row=4, column=0, pady=20, padx=20)

        # 返回按钮
        back_button = ctk.CTkButton(
            self.payment_frame,
            text="BACK",
            font=("Arial", 16),
            fg_color="grey",
            hover_color="#696969",  # Darker grey for hover
            text_color="black",
            command=self.on_back_click,
            width=200,
            height=40,
            corner_radius=8
        )
        back_button.grid(row=4, column=1, pady=20, padx=20)

    def create_upload_payment_screen(self):
        self.central_frame.destroy()
        self.payment_frame.destroy()

        self.upload_payment_frame = tk.Frame(self.root, bg="#C19A6B", padx=80, pady=80)
        self.upload_payment_frame.pack(expand=True)

        # 支付信息框架
        self.upload_frame = tk.Frame(self.upload_payment_frame, bg="#C19A6B", padx=70, pady=70)
        self.upload_frame.pack()

        title_label = tk.Label(self.upload_frame, text="UPLOAD PAYMENT PAGE", font=("Arial", 24, "bold"), bg="#C19A6B",
                               fg="White")
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # 交易日期
        transaction_date_label = tk.Label(self.upload_frame, text="Transaction Date:", font=("Arial", 15), bg="#C19A6B")
        transaction_date_label.grid(row=1, column=0, sticky="e", padx=10, pady=8)
        self.transaction_date_entry = DateEntry(self.upload_frame, width=19, background="darkblue", foreground="white",
                                                borderwidth=2)
        self.transaction_date_entry.grid(row=1, column=1, padx=10, pady=8)

        # Tenant ID field - automatically filled and read-only
        tenant_id_label = tk.Label(self.upload_frame, text="Tenant ID:", font=("Arial", 15), bg="#C19A6B")
        tenant_id_label.grid(row=2, column=0, sticky="e", padx=10, pady=8)
        self.tenant_id_entry = ctk.CTkEntry(self.upload_frame, width=200, height=30, corner_radius=10, state="disabled")
        self.tenant_id_entry.grid(row=2, column=1, padx=10, pady=8)

        # Get and set Tenant ID, Stall ID, and Total Amount
        try:
            conn = sqlite3.connect("govRental.db")
            cursor = conn.cursor()

            # Get Tenant ID
            tenant_id = self.fetch_tenant_id(login_profile['IC_Number'], login_profile['Password'])
            self.tenant_id_entry.configure(state="normal")
            self.tenant_id_entry.delete(0, tk.END)
            self.tenant_id_entry.insert(0, str(tenant_id))
            self.tenant_id_entry.configure(state="disabled")

            # Fetch Stall ID and Total Amount
            cursor.execute("""
                SELECT Stall_ID, Total_Amount 
                FROM Stall 
                WHERE Tenant_ID = ?
            """, (tenant_id,))
            result = cursor.fetchone()

            if result:
                stall_id, total_amount = result
            else:
                stall_id, total_amount = "N/A", "0.00"

        except Exception as e:
            print(f"Error fetching data: {e}")
            stall_id, total_amount = "N/A", "0.00"
        finally:
            if 'conn' in locals():
                conn.close()

        # Stall ID field - automatically filled and read-only
        stall_id_label = tk.Label(self.upload_frame, text="Stall ID:", font=("Arial", 15), bg="#C19A6B")
        stall_id_label.grid(row=3, column=0, sticky="e", padx=10, pady=8)
        self.stall_id_entry = ctk.CTkEntry(self.upload_frame, width=200, height=30, corner_radius=10, state="disabled")
        self.stall_id_entry.grid(row=3, column=1, padx=10, pady=8)

        # Set Stall ID
        self.stall_id_entry.configure(state="normal")
        self.stall_id_entry.delete(0, tk.END)
        self.stall_id_entry.insert(0, str(stall_id))
        self.stall_id_entry.configure(state="disabled")

        # Amount field - automatically filled and read-only
        amount_label = tk.Label(self.upload_frame, text="Amount to Pay:", font=("Arial", 15), bg="#C19A6B")
        amount_label.grid(row=4, column=0, sticky="e", padx=10, pady=8)
        self.amount_entry = ctk.CTkEntry(self.upload_frame, width=200, height=30, corner_radius=10, state="disabled")
        self.amount_entry.grid(row=4, column=1, padx=10, pady=8)

        # Set Amount
        self.amount_entry.configure(state="normal")
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, f"RM {total_amount}")
        self.amount_entry.configure(state="disabled")

        # 备注
        remarks_label = tk.Label(self.upload_frame, text="Remarks:", font=("Arial", 15), bg="#C19A6B")
        remarks_label.grid(row=5, column=0, sticky="e", padx=10, pady=8)
        self.remarks_entry = ctk.CTkEntry(self.upload_frame, width=200, height=30, corner_radius=10)
        self.remarks_entry.grid(row=5, column=1, padx=10, pady=8)

        # 上传文件按钮
        upload_slip_label = tk.Label(self.upload_frame, text="Upload Slip:", font=("Arial", 15), bg="#C19A6B")
        upload_slip_label.grid(row=6, column=0, sticky="e", padx=10, pady=8)
        self.upload_button = ctk.CTkButton(self.upload_frame, text="Choose File", command=self.on_upload_click,
                                           width=150, height=30, corner_radius=8)
        self.upload_button.grid(row=6, column=1, padx=10, pady=8)

        # 这里我们添加一个label用于显示文件名
        self.file_name_label = tk.Label(self.upload_frame, text="", font=("Arial", 13), bg="#C19A6B")
        self.file_name_label.grid(row=6, column=2, padx=10, pady=8)

        # 上传按钮
        upload_button = ctk.CTkButton(self.upload_frame, text="UPLOAD", font=("Arial", 16), fg_color="red",
                                      text_color="black",
                                      command=self.database_payment, width=200, height=40, corner_radius=8)
        upload_button.grid(row=7, column=0, pady=30, padx=20)

        # 返回按钮
        back_button = ctk.CTkButton(self.upload_frame, text="BACK", font=("Arial", 16), fg_color="grey",
                                    text_color="black",
                                    command=self.payment_back_click, width=200, height=40, corner_radius=8)
        back_button.grid(row=7, column=1, pady=30, padx=20)

    # 返回按钮点击事件
    def on_back_click(self):
        # 隐藏支付界面
        self.central_frame.pack_forget()
        self.payment_frame.pack_forget()

        # 重新显示按钮和视频框架
        self.buttons_frame.pack(fill=tk.X)

    def payment_back_click(self):
        self.upload_payment_frame.pack_forget()
        self.upload_frame.pack_forget()

        # 重新显示按钮和视频框架
        self.buttons_frame.pack(fill=tk.X)

    def database_payment(self):
        # Check if any required fields are empty
        if not self.transaction_date_entry.get() or \
                not self.tenant_id_entry.get() or \
                not self.stall_id_entry.get() or \
                not self.amount_entry.get() or \
                not self.remarks_entry.get() or \
                not self.file_name_label.cget("text"):
            messagebox.showerror("Error", "Please fill in valid information before upload")
            return

        try:
            conn = sqlite3.connect("govRental.db")
            cursor = conn.cursor()

            # Insert data into the Payment table
            cursor.execute(
                """INSERT INTO Payment_Manage 
                   (Transaction_Date, Tenant_ID, Stall_ID, Rental_Amount, 
                    Remarks, Bank_Slip) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (self.transaction_date_entry.get(),
                 self.tenant_id_entry.get(),
                 self.stall_id_entry.get(),
                 self.amount_entry.get().replace("RM ", ""),  # Remove the "RM " prefix
                 self.remarks_entry.get(),
                 self.file_name_label.cget("text"))
            )
            conn.commit()

            # 显示上传成功的消息框
            messagebox.showinfo("Upload", "Upload Successful!")

            # 清除输入框
            self.transaction_date_entry.delete(0, tk.END)
            self.remarks_entry.delete(0, tk.END)
            self.file_name_label.config(text="")

            # 隐藏上界面，返回到支付界面
            self.upload_payment_frame.destroy()

            # 重新创建支付界面
            self.create_payment_screen()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    # 传按钮点击事件
    def on_upload_click(self):
        # 打开文件对话框，选择文件
        file_path = filedialog.askopenfilename(title="Select Payment Slip",
                                               filetypes=(
                                                   ("Image Files", "*.png;*.jpg;*.jpeg;*.pdf"), ("All Files", "*.*")))

        if file_path:
            # 将文件名显示在按钮面的label中
            file_name = file_path.split("/")[-1]  # 仅显示文件名，不显示整路径
            self.file_name_label.config(text=file_name)
            messagebox.showinfo("Upload Payment", "Payment slip uploaded successfully!")

    # 各个按钮的功能函数

    def on_my_stall_click(self):
        try:
            # Get the tenant's IC number and password from login_profile
            ic_number = login_profile['IC_Number']
            password = login_profile['Password']

            # Get the Tenant_ID
            tenant_id = self.fetch_tenant_id(ic_number, password)

            # Fetch Stall_ID for this tenant
            conn = sqlite3.connect("govRental.db")
            cursor = conn.cursor()
            cursor.execute("SELECT Stall_ID FROM Stall WHERE Tenant_ID = ?", (tenant_id,))
            result = cursor.fetchone()

            if result:
                Stall_ID = result[0]
                # Hide current frames
                self.buttons_frame.pack_forget()
                # Create stall frame with the fetched Stall_ID
                self.create_stall_frame(Stall_ID)
            else:
                messagebox.showerror("Error", "No stall assigned to this tenant.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch stall information: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def fetch_tenant_id(self, ic_number, password):
        try:
            conn = sqlite3.connect("govRental.db")
            cursor = conn.cursor()

            # 调试信息：打印传入的 IC Number 和密码
            print(f"Fetching tenant with IC Number: {ic_number} and Password: {password}")

            # 执行查询获取 Tenant_ID
            cursor.execute("""
                SELECT Tenant_ID, Tenant_Username 
                FROM Tenant 
                WHERE Tenant_IC_Number = ? AND Tenant_Password = ?
            """, (ic_number, password))
            result = cursor.fetchone()

            # 如果找到租户
            if result:
                tenant_id, tenant_username = result
                print(f"Found Tenant - ID: {tenant_id}, Username: {tenant_username}")  # Print both ID and username
                return tenant_id  # Return Tenant_id
            else:
                # 没找到租户时，抛出异常并输出调试信息
                print(f"No tenant found with IC Number: {ic_number}")
                raise ValueError("No tenant found with the provided credentials.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error retrieving tenant ID: {e}")
        finally:
            conn.close()

    def show_inbox(self):
        # Hide the current view
        if hasattr(self, 'response_frame'):
            self.response_frame.pack_forget()

        # Show inbox view
        self.create_feedback_screen()

    def show_response(self):
        # Hide current frames
        if hasattr(self, 'central_feedback_frame'):
            self.central_feedback_frame.pack_forget()
        if hasattr(self, 'response_frame'):
            self.response_frame.pack_forget()

        # Create response frame
        self.response_frame = ctk.CTkFrame(self.root, fg_color="white")
        self.response_frame.pack(expand=True, fill="both")

        # Title
        title_label = ctk.CTkLabel(
            self.response_frame,
            text="Tenant - Response",
            font=("Arial", 24, "bold"),
            text_color="black"
        )
        title_label.pack(pady=20)

        # Button Frame
        button_frame = ctk.CTkFrame(self.response_frame, fg_color="white")
        button_frame.pack(pady=10)

        # Inbox and View Response buttons
        inbox_btn = ctk.CTkButton(
            button_frame,
            text="Inbox",
            font=("Arial", 12),
            fg_color="#FFB05D",
            text_color="black",
            hover_color="#FF9933",
            command=self.show_inbox,
            width=120,
            height=35,
            corner_radius=10
        )
        inbox_btn.pack(side="left", padx=5)

        view_response_btn = ctk.CTkButton(
            button_frame,
            text="View Response",
            font=("Arial", 12),
            fg_color="#FFB05D",
            text_color="black",
            hover_color="#FF9933",
            command=self.show_response,
            width=120,
            height=35,
            corner_radius=10
        )
        view_response_btn.pack(side="left", padx=5)

        # Split view frame
        split_frame = ctk.CTkFrame(self.response_frame, fg_color="white")
        split_frame.pack(fill="both", expand=True)

        # Messages list frame (left side)
        messages_frame = ctk.CTkFrame(
            split_frame,
            fg_color="white",
            border_width=1,
            border_color="#E0E0E0",
            corner_radius=10
        )
        messages_frame.pack(side="left", fill="both", expand=True, padx=(10, 5))

        # Message details frame (right side)
        self.details_frame = ctk.CTkFrame(
            split_frame,
            fg_color="white",
            border_width=1,
            border_color="#E0E0E0",
            corner_radius=10
        )
        self.details_frame.pack(side="right", fill="both", expand=True, padx=(5, 10))

        # Category selection with delete button
        category_frame = ctk.CTkFrame(messages_frame, fg_color="white")
        category_frame.pack(fill="x", pady=5, padx=5)

        # Left side - Category selection
        category_label = ctk.CTkLabel(
            category_frame,
            text="Category:",
            font=("Arial", 12),
            text_color="black"
        )
        category_label.pack(side="left", padx=5)

        self.category_var = StringVar(value="Inbox")

        # Custom style for combobox
        style = ttk.Style()
        style.configure(
            "Rounded.TCombobox",
            borderwidth=0,
            relief="flat",
            background="white",
            arrowcolor="#FFB05D",
            foreground="black"
        )

        category_combo = ttk.Combobox(
            category_frame,
            textvariable=self.category_var,
            values=["Inbox", "Sent"],
            width=40,
            state="readonly",
            style="Rounded.TCombobox"
        )
        category_combo.pack(side="left", padx=5)
        category_combo.bind('<<ComboboxSelected>>', lambda e: self.update_message_display())

        # Right side - Delete button
        delete_btn = ctk.CTkButton(
            category_frame,
            text="Delete Message",
            font=("Arial", 12),
            fg_color="#FF4B4B",
            text_color="white",
            hover_color="#D43F3F",
            command=self.delete_message,
            width=120,
            height=35,
            corner_radius=10
        )
        delete_btn.pack(side="right", padx=5)

        # Message list with custom scrollbar
        messages_list_frame = ctk.CTkFrame(messages_frame, fg_color="white")
        messages_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.messages_list = tk.Listbox(
            messages_list_frame,
            font=("Arial", 10),
            selectmode="single",
            relief="flat",
            bg="white",
            selectbackground="#FFB05D",
            selectforeground="black",
            highlightthickness=1,
            highlightcolor="#E0E0E0",
            bd=0
        )
        self.messages_list.pack(side="left", fill="both", expand=True)

        # Custom scrollbar
        scrollbar = ctk.CTkScrollbar(
            messages_list_frame,
            command=self.messages_list.yview,
            button_color="gray",
            button_hover_color="grey"
        )
        scrollbar.pack(side="right", fill="y")
        self.messages_list.config(yscrollcommand=scrollbar.set)

        self.messages_list.bind('<<ListboxSelect>>', self.show_full_message)

        # Add back button
        back_btn = ctk.CTkButton(
            self.response_frame,
            text="Back",
            command=self.show_inbox,
            fg_color="red",
            text_color="white",
            hover_color="#8B0000",
            width=100,
            height=30,
            corner_radius=10
        )
        back_btn.pack(pady=10)

        # Load initial messages
        self.update_message_display()

    def get_messages(self, category, message_id=None):
        try:
            conn = sqlite3.connect("govRental.db")
            cursor = conn.cursor()

            # Get tenant ID
            tenant_id = self.fetch_tenant_id(login_profile['IC_Number'], login_profile['Password'])

            if category == "Sent":
                if message_id:
                    query = """SELECT message_id, sender, recipient, subject, message, attachment, timestamp_sent_reply
                               FROM notif_sent_reply 
                               WHERE message_id = ?"""
                    cursor.execute(query, (message_id,))
                else:
                    query = """SELECT message_id, sender, recipient, subject, message, attachment, timestamp_sent_reply
                               FROM notif_sent_reply 
                               WHERE sender = ?
                               ORDER BY timestamp_sent_reply DESC"""
                    cursor.execute(query, (tenant_id,))
            else:  # Inbox
                if message_id:
                    query = """SELECT message_id, sender, recipient, subject, message, attachment, timestamp_receive, status
                               FROM notif_inbox 
                               WHERE message_id = ?"""
                    cursor.execute(query, (message_id,))
                else:
                    query = """SELECT message_id, sender, recipient, subject, message, attachment, timestamp_receive, status
                              FROM notif_inbox
                              WHERE recipient = ? 
                              ORDER BY timestamp_receive DESC"""
                    cursor.execute(query, (tenant_id,))

            messages = cursor.fetchall()
            return messages

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            return []
        finally:
            if conn:
                conn.close()

    def update_message_display(self, event=None):
        # Clear existing items
        self.messages_list.delete(0, tk.END)

        # Get messages based on selected category
        category = self.category_var.get()
        messages = self.get_messages(category)

        # Add messages to listbox
        for msg in messages:
            if category == "Sent":
                display_text = f"To: {msg[2]} | Subject: {msg[3]} | Date: {msg[5]}"
            else:
                display_text = f"From: {msg[1]} | Subject: {msg[3]} | Date: {msg[6]}"

            self.messages_list.insert(tk.END, display_text)

            # Color code unread messages
            if category == "Inbox" and msg[7] == "New":
                self.messages_list.itemconfig(tk.END, {'bg': '#FFE4B5'})

    def show_full_message(self, event=None):
        """
        Display the full message with its reply thread
        """
        selection = self.messages_list.curselection()
        if not selection:
            return

        selected_index = selection[0]
        selected_category = self.category_var.get()
        messages = self.get_messages(selected_category)

        if not messages or selected_index >= len(messages):
            messagebox.showerror("No Messages", "There are no messages to display.")
            return

        # Get the selected message details
        message = messages[selected_index]
        message_id = message[0]

        # Get the full message details
        full_message = self.get_messages(selected_category, message_id=message_id)

        if not full_message or len(full_message) == 0:
            messagebox.showerror("Error", "Message not found.")
            return

        # Clear previous content
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        # Unpack message details based on category
        if selected_category == "Sent":
            message_id, sender, recipient, subject, message_content, attachment, timestamp = full_message[0]
            status = "Sent"
        else:
            message_id, sender, recipient, subject, message_content, attachment, timestamp, status = full_message[0]

        # Create message header frame using CTkFrame
        header_frame = ctk.CTkFrame(
            self.details_frame,
            fg_color="#FFB05D",
            corner_radius=10
        )
        header_frame.pack(fill=tk.X, padx=5, pady=5)

        # Display message details using CTkLabel
        ctk.CTkLabel(
            header_frame,
            text=f"Subject: {subject}",
            font=("Arial", 11, "bold"),
            text_color="black"
        ).pack(anchor="w", padx=5)

        ctk.CTkLabel(
            header_frame,
            text=f"From: {sender}",
            text_color="black"
        ).pack(anchor="w", padx=5)

        ctk.CTkLabel(
            header_frame,
            text=f"To: {recipient}",
            text_color="black"
        ).pack(anchor="w", padx=5)

        ctk.CTkLabel(
            header_frame,
            text=f"Date: {timestamp}",
            text_color="black"
        ).pack(anchor="w", padx=5)

        ctk.CTkLabel(
            header_frame,
            text=f"Status: {status}",
            text_color="black"
        ).pack(anchor="w", padx=5, pady=2)

        # Message content using CTkTextbox
        self.message_content = ctk.CTkTextbox(
            self.details_frame,
            height=200,
            wrap="word",
            font=("Arial", 12),
            border_color="#FFB05D",
            border_width=2,
            corner_radius=10,
            fg_color="white"
        )
        self.message_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Insert message content with reply history
        message_parts = message_content.split("\n--- Reply from ")
        self.message_content.insert(tk.END, message_parts[0])  # Original message

        # Insert replies with different background colors
        for i, reply in enumerate(message_parts[1:], 1):
            self.message_content.insert(tk.END, "\n\n--- Reply from " + reply)

        self.message_content.configure(state="disabled")  # Make text read-only

        # Reply section using CTkFrame
        reply_frame = ctk.CTkFrame(
            self.details_frame,
            fg_color="white",
            corner_radius=10
        )
        reply_frame.pack(fill=tk.X, padx=5, pady=5)

        ctk.CTkLabel(
            reply_frame,
            text="Add Reply:",
            font=("Arial", 11),
            text_color="black"
        ).pack(anchor="w", padx=5, pady=2)

        # Reply text area using CTkTextbox
        self.reply_text = ctk.CTkTextbox(
            reply_frame,
            height=100,
            wrap="word",
            font=("Arial", 12),
            border_color="#FFB05D",
            border_width=2,
            corner_radius=10,
            fg_color="white"
        )
        self.reply_text.pack(fill=tk.X, padx=5, pady=5)

        # Button frame using CTkFrame
        button_frame = ctk.CTkFrame(
            reply_frame,
            fg_color="white",
            corner_radius=10
        )
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        # Send Reply button
        send_reply_btn = ctk.CTkButton(
            button_frame,
            text="Send Reply",
            command=lambda: self.handle_reply_send(
                sender=self.fetch_tenant_id(login_profile['IC_Number'], login_profile['Password']),
                recipient=sender if selected_category == "Inbox" else recipient,
                subject=subject if subject.startswith("Re:") else f"Re: {subject}",
                reply_message=self.reply_text.get("1.0", tk.END).strip(),
                original_message_id=message_id,
                reply_text=self.reply_text
            ),
            fg_color="#FFB05D",
            text_color="black",
            hover_color="#FF9933",
            width=100,
            height=35,
            corner_radius=10,
            font=("Arial", 12)
        )
        send_reply_btn.pack(side="right", padx=5)

        # If there's an attachment, add an attachment button
        if attachment:
            attachment_btn = ctk.CTkButton(
                button_frame,
                text="View Attachment",
                command=lambda: self.open_attachment(attachment),
                fg_color="#4B0082",
                text_color="white",
                hover_color="#2E0854",
                width=120,
                height=35,
                corner_radius=10,
                font=("Arial", 12)
            )
            attachment_btn.pack(side="right", padx=5)

    def handle_reply_send(self, sender, recipient, subject, reply_message, original_message_id, reply_text):
        """
        Handle sending a reply message
        """
        if not reply_message:
            messagebox.showwarning("Empty Reply", "Please enter a reply message.")
            return

        try:
            conn = sqlite3.connect("govRental.db")
            cursor = conn.cursor()

            # Generate a new message ID for the reply
            new_message_id = str(int(time.time() * 1000))
            current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Get the original message thread
            cursor.execute("""
                SELECT message 
                FROM notif_inbox 
                WHERE message_id = ?
                UNION
                SELECT message 
                FROM notif_sent_reply 
                WHERE message_id = ?
            """, (original_message_id, original_message_id))

            result = cursor.fetchone()
            original_thread = result[0] if result else ""

            # Create the updated message thread content
            updated_message = f"{original_thread}\n--- Reply from {sender} ---\n{current_timestamp}: {reply_message}"

            # Insert into notif_sent_reply
            cursor.execute("""
                INSERT INTO notif_sent_reply (
                    message_id, sender, recipient, subject, message, 
                    attachment, timestamp_sent_reply
                ) VALUES (?, ?, ?, ?, ?, NULL, ?)""",
                           (new_message_id, sender, recipient, subject, updated_message, current_timestamp))

            # Insert into notif_inbox
            cursor.execute("""
                INSERT INTO notif_inbox (
                    message_id, sender, recipient, subject, message,
                    attachment, timestamp_receive, status
                ) VALUES (?, ?, ?, ?, ?, NULL, ?, 'New')""",
                           (new_message_id, sender, recipient, subject, updated_message, current_timestamp))

            conn.commit()

            # Clear the reply text box
            reply_text.delete("1.0", tk.END)

            # Update the message displays
            self.update_message_display()
            self.show_full_message(None)  # Refresh the full message view

            messagebox.showinfo("Success", "Reply sent successfully!")

        except sqlite3.Error as e:
            print(f"Database error: {e}. Error details: {e.args}")
            conn.rollback()
            messagebox.showerror("Error", "Failed to send reply. Please try again.")
        finally:
            if conn:
                conn.close()

    def delete_message(self):
        """
        Delete selected message from inbox/sent_reply and move it to delete table
        """
        current_user = self.fetch_tenant_id(login_profile['IC_Number'], login_profile['Password'])

        selected_index = self.messages_list.curselection()
        if not selected_index:
            messagebox.showwarning("Selection Error", "Please select a message to delete.")
            return

        selected_category = self.category_var.get()
        messages = self.get_messages(selected_category)

        if selected_index[0] >= len(messages):
            messagebox.showwarning("Error", "Invalid selection.")
            return

        message = messages[selected_index[0]]
        message_id = message[0]  # First element is message_id

        # Confirm deletion
        if not messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this message?"):
            return

        try:
            conn = sqlite3.connect("govRental.db")
            cursor = conn.cursor()

            # Begin transaction
            conn.execute('BEGIN')

            # Store message in notif_deleted table
            if selected_category == "Sent":
                message_id, sender, recipient, subject, message_content, attachment, timestamp = message
                cursor.execute("""
                    INSERT INTO notif_deleted (
                        message_id, sender, recipient, subject, message, 
                        attachment, source, timestamp_deleted
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    message_id,
                    sender,
                    recipient,
                    subject,
                    message_content,
                    attachment,
                    selected_category
                ))
            else:
                message_id, sender, recipient, subject, message_content, attachment, timestamp, status = message
                cursor.execute("""
                    INSERT INTO notif_deleted (
                        message_id, sender, recipient, subject, message, 
                        attachment, source, timestamp_deleted
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    message_id,
                    sender,
                    recipient,
                    subject,
                    message_content,
                    attachment,
                    selected_category
                ))

            # Remove from appropriate source table based on category
            if selected_category == "Sent":
                cursor.execute("""
                    DELETE FROM notif_sent_reply 
                    WHERE message_id = ? AND sender = ?
                """, (message_id, current_user))
            else:
                cursor.execute("""
                    DELETE FROM notif_inbox 
                    WHERE message_id = ? AND recipient = ?
                """, (message_id, current_user))

            conn.commit()
            messagebox.showinfo("Success", "Message deleted successfully")

            # Refresh the message display
            self.update_message_display()

            # Clear the full message display
            for widget in self.details_frame.winfo_children():
                widget.destroy()

        except sqlite3.Error as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to delete message: {str(e)}")
        finally:
            if conn:
                conn.close()

    def open_attachment(self, attachment_path):
        """
        Open the attachment file using the default system application
        """
        if not attachment_path:
            messagebox.showwarning("No Attachment", "This message has no attachment.")
            return

        try:
            if os.path.exists(attachment_path):
                # Use the default system application to open the file
                if sys.platform == 'win32':  # For Windows
                    os.startfile(attachment_path)
                elif sys.platform == 'darwin':  # For macOS
                    subprocess.call(['open', attachment_path])
                else:  # For Linux
                    subprocess.call(['xdg-open', attachment_path])
            else:
                messagebox.showerror("Error", "Attachment file not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open attachment: {str(e)}")


# Initialize Tkinter
root = tk.Tk()
root.title("Admin and Tenant Login")
root.geometry("1920x1080")
root.state("zoomed")

# Variables
USER_IC_NUMBER_LOGIN = StringVar()
PASSWORD_LOGIN = StringVar()
USERNAME_REGISTER = StringVar()
IC_NUMBER_REGISTER = StringVar()
GENDER = StringVar()
PHONE_NUMBER = StringVar()
EMAIL_ADDRESS = StringVar()
PASSWORD_REGISTER = StringVar()
CONFIRM_PASSWORD = StringVar()

conn = None  # connection to database
cursor = None  # use to execute the SQL queries and fetch results from db

login_profile = {}


# Connect to database and create table if it doesn't exist

def Database():
    global conn, cursor
    conn = sqlite3.connect("govRental.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA busy_timeout = 5000")  # 5秒等待时间

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Tenant (
            Tenant_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
            Tenant_Username TEXT NOT NULL, 
            Tenant_IC_Number TEXT NOT NULL CHECK(LENGTH(Tenant_IC_Number) = 12),  
            Tenant_Gender TEXT NOT NULL, 
            Tenant_Phone_Number TEXT NOT NULL CHECK(LENGTH(Tenant_Phone_Number) <= 11), 
            Tenant_Email_Address TEXT NOT NULL CHECK(LENGTH(Tenant_Email_Address) <= 100), 
            Tenant_Password TEXT NOT NULL CHECK(LENGTH(Tenant_Password) >= 8)
        )"""  # Fixed closing parenthesis
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Admin (
            Admin_ID INTEGER PRIMARY KEY NOT NULL, 
            Admin_Name TEXT NOT NULL, 
            Admin_IC_Number TEXT NOT NULL CHECK(LENGTH(Admin_IC_Number) = 12),  
            Admin_Gender TEXT NOT NULL, 
            Admin_Phone_Number TEXT NOT NULL CHECK(LENGTH(Admin_Phone_Number) <= 11), 
            Admin_Passcode TEXT NOT NULL,
            Admin_Email_Address TEXT NOT NULL CHECK(LENGTH(Admin_Email_Address) <= 100), 
            Admin_Join_Date TEXT NOT NULL
        )"""  # Fixed closing parenthesis
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Stall (
            Stall_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
            Address_Image TEXT,
            Stall_Address TEXT NOT NULL,  
            Postcode INTEGER NOT NULL, 
            Status INTEGER DEFAULT 0,  
            Tenant_ID INTEGER NOT NULL,  
            Tenant_Username TEXT NOT NULL, 
            Rental_Period INTEGER NOT NULL,
            Contract_Start_Date DATE,
            Contract_End_Date DATE,
            Rental_Amount FLOAT,
            Deposit_Amount FLOAT,
            Total_Amount REAL,
            Payment_Due DATETIME,
            Contract_Status TEXT,
            Renewal_Status TEXT,
            id INTEGER,
            Latitude REAL,
            Longitude REAL,
            Reminder_Date DATETIME,
            Contract_File TEXT,
            FOREIGN KEY (Tenant_ID) REFERENCES Tenant (Tenant_ID),
            FOREIGN KEY (id) REFERENCES markers (id))"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Feedback_Manage (
            Feedback_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
            Tenant_ID INTEGER NOT NULL,
            Admin_ID INTEGER NOT NULL,  
            Feedback TEXT NOT NULL, 
            Response TEXT NOT NULL, 
            Feedback_Date DATE NOT NULL,
            Response_Date DATE NOT NULL,
            FOREIGN KEY (Tenant_ID) REFERENCES Tenant (Tenant_ID),
            FOREIGN KEY (Admin_ID) REFERENCES Admin (Admin_ID))"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Payment_Manage (
            Payment_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
            Payment_Due DATETIME,
            Tenant_ID INTEGER ,
            Tenant_Name TEXT ,
            Stall_ID INTEGER ,
            Postcode INTEGER , 
            Rental_Amount REAL,
            Transaction_Date DATE ,
            Remarks TEXT ,  
            Bank_Slip TEXT ,
            Status TEXT ,
            Gov_Receipts TEXT ,
            Due_Date DATE ,
            Overdue_Status TEXT ,
            Overdue_Amount TEXT ,
            Total_Amount TEXT ,
            Reminder_Date DATETIME,
            FOREIGN KEY (Tenant_ID) REFERENCES Tenant (Tenant_ID),
            FOREIGN KEY (Stall_ID) REFERENCES Stall (Stall_ID))"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Business_Information (
            Business_ID INTEGER PRIMARY KEY NOT NULL, 
            Business_Name TEXT NOT NULL,
            Licence_No TEXT NOT NULL,
            Business_Hours TEXT NOT NULL, 
            Location TEXT NOT NULL, 
            Contact_No TEXT NOT NULL, 
            Email_Address TEXT NOT NULL)"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS markers (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
            lat TEXT NOT NULL,
            lon TEXT NOT NULL,
            text TEXT NOT NULL, 
            icon_path TEXT NOT NULL)"""
    )

    cursor.execute('''CREATE TABLE IF NOT EXISTS FaceEmbeddings 
                 (Face_id INTEGER PRIMARY KEY, 
                  Tenant_IC_Number INTEGER,
                  name TEXT, 
                  embedding BLOB,
                  faceImagePath TEXT,
                  FOREIGN KEY (Tenant_IC_Number) REFERENCES Tenant (Tenant_IC_Number))''')

    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS Attendance (
            Attendance_id INTEGER PRIMARY KEY, 
            Tenant_IC_Number INTEGER, 
            name TEXT, 
            date TEXT, 
            clock_in_time TEXT, 
            clock_out_time TEXT, 
            Clock_In_longitude REAL,
            Clock_In_latitude REAL,
            Clock_Out_longitude REAL,
            Clock_Out_latitude REAL,
            Clock_In_Status TEXT,
            Clock_Out_Status TEXT,
            FOREIGN KEY (Tenant_IC_Number) REFERENCES Tenant (Tenant_IC_Number))''')

    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS notif_sent_reply (
    	    message_id TEXT PRIMARY KEY NOT NULL,
    	    sender TEXT NOT NULL,
    	    recipient TEXT NOT NULL,
    	    subject TEXT NOT NULL,
    	    message TEXT NOT NULL,
    	    attachment TEXT,
    	    timestamp_sent_reply DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)''')

    # Create notif_inbox table with foreign key constraint on message_id
    cursor.execute('''CREATE TABLE IF NOT EXISTS notif_inbox (
    	                message_id TEXT,
    	                sender TEXT NOT NULL,
    	                recipient TEXT NOT NULL,
    	                subject TEXT NOT NULL,
    	                message TEXT NOT NULL,
    	                attachment TEXT,
    	                timestamp_receive DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    	                timestamp_read DATETIME,
    	                status TEXT NOT NULL,
    	                FOREIGN KEY (message_id) REFERENCES notif_sent_reply(message_id))''')

    # Create notif_deleted table with foreign key constraint on message_id
    cursor.execute('''CREATE TABLE IF NOT EXISTS notif_deleted (
    	                message_id TEXT,
    	                sender TEXT NOT NULL,
    	                recipient TEXT NOT NULL,
    	                subject TEXT NOT NULL,
    	                message TEXT NOT NULL,
    	                attachment TEXT,
    	                source TEXT NOT NULL,
    	                timestamp_deleted DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    	                FOREIGN KEY (message_id) REFERENCES notif_sent_reply(message_id))''')
    conn.commit()


@app.route('/')
def index():
    # Get status and tenant_ic from URL parameters
    status = request.args.get('status', 'Clock In')
    tenant_ic = login_profile.get('IC_Number', '')
    return render_template('live_location.html', tenant_ic=tenant_ic, status=status)


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000')


def start_flask(status):
    def run_app():
        app.run(debug=False, use_reloader=False)

    threading.Thread(target=run_app).start()
    time.sleep(1)
    # Get tenant IC from login_profile
    tenant_ic = login_profile.get('IC_Number', '')
    if not tenant_ic:
        print("Warning: No tenant IC found in login_profile")

    # Pass both status and tenant_ic in the URL
    url = f'http://127.0.0.1:5000/?status={status}&tenant_ic={tenant_ic}'
    print(f"Opening URL: {url}")  # Debug print
    webbrowser.open_new(url)


############################################# FUNCTIONS ################################################
def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)


##################################################################################
def tick():
    time_string = time.strftime('%H:%M:%S')
    clock.config(text=time_string)
    clock.after(200, tick)


###################################################################################

def contact():
    contact_info = """
    If you encounter any issues, please contact support:

    Email: support@example.com
    Phone: +1-234-567-8900

    Or visit our support website:
    https://support.example.com
    """
    messagebox.showinfo("Contact Support", contact_info)


###################################################################################

def check_haarcascadefile():
    cascade_file = "haarcascade_frontalface_default.xml"
    cascade_url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"

    if not os.path.isfile(cascade_file):
        try:
            # Download the file if it doesn't exist
            print("Downloading required face detection file...")
            urllib.request.urlretrieve(cascade_url, cascade_file)
            messagebox.showinfo("Success", "Required files have been downloaded successfully!")
            return True
        except Exception as e:
            messagebox.showerror("Error",
                                 f"Could not download required file.\nError: {str(e)}\n\n"
                                 "Please contact support or download the file manually.")
            return False
    return True


def clear():
    txt.delete(0, 'end')
    res = "1)Take Images  >>>  2)Save Profile"
    message1.configure(text=res)


def clear2():
    txt2.delete(0, 'end')
    res = "1)Take Images  >>>  2)Save Profile"
    message1.configure(text=res)


#######################################################################################

def TakeImages():
    Database()

    if not check_haarcascadefile():
        return

    Tenant_IC_Number = (txt.get())
    name = (txt2.get())

    # Validate inputs
    if not Tenant_IC_Number or not name:
        messagebox.showwarning("Warning", "Please enter both Tenant ID and Name!")
        return

    if not ((name.isalpha()) or (' ' in name)):
        messagebox.showwarning("Warning", "Please enter a valid name!")
        return

    try:
        # Check if Tenant_id already exists
        cursor.execute("SELECT Tenant_IC_Number FROM FaceEmbeddings WHERE Tenant_IC_Number=?", (Tenant_IC_Number,))
        if cursor.fetchone() is not None:
            messagebox.showwarning("Warning", "Tenant_IC_Number already exists!")
            return

        cam = cv2.VideoCapture(0)
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(harcascadePath)

        # Create preview window
        cv2.namedWindow("Face Registration", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Face Registration", cv2.WND_PROP_TOPMOST, 1)

        face_detected = False
        while not face_detected:
            ret, img = cam.read()
            if not ret:
                break

            # Show live preview
            preview_img = img.copy()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)

            # Draw rectangle around detected face in preview
            for (x, y, w, h) in faces:
                cv2.rectangle(preview_img, (x, y), (x + w, y + h), (255, 0, 0), 2)

            cv2.imshow("Face Registration", preview_img)

            if len(faces) > 0:
                x, y, w, h = faces[0]  # Take the first detected face
                # Add padding around the face
                padding = 30
                x = max(0, x - padding)
                y = max(0, y - padding)
                w = min(img.shape[1] - x, w + 2 * padding)
                h = min(img.shape[0] - y, h + 2 * padding)

                # Crop face image
                face_img = img[y:y + h, x:x + w]

                try:
                    # Generate embedding
                    temp_path = f"temp_face_{Tenant_IC_Number}.jpg"
                    cv2.imwrite(temp_path, face_img)

                    # Generate embedding using DeepFace
                    embedding = DeepFace.represent(img_path=temp_path,
                                                   model_name="Facenet",
                                                   enforce_detection=False)

                    # Save the face image to a permanent location
                    face_image_dir = "FaceImages"
                    if not os.path.exists(face_image_dir):
                        os.makedirs(face_image_dir)

                    face_image_path = os.path.join(face_image_dir, f"face_{Tenant_IC_Number}.jpg")
                    cv2.imwrite(face_image_path, face_img)

                    # Store in database with image path
                    embedding_bytes = pickle.dumps(embedding[0]["embedding"])
                    cursor.execute("""INSERT INTO FaceEmbeddings 
                                (Tenant_IC_Number, name, embedding, faceImagePath) 
                                VALUES (?, ?, ?, ?)""",
                                   (Tenant_IC_Number, name, embedding_bytes, face_image_path))
                    conn.commit()

                    # Clean up temporary file
                    os.remove(temp_path)
                    face_detected = True

                    # Close only the capture window
                    cv2.destroyWindow("Face Registration")

                    # Show the captured face in a new window
                    cv2.imshow('Captured Face', face_img)
                    cv2.waitKey(2000)  # Show for 2 seconds
                    cv2.destroyWindow('Captured Face')

                    # Release camera
                    cam.release()

                    # Show success message
                    messagebox.showinfo("Success", f"Face registered for {name} (Tenant_IC_Number: {Tenant_IC_Number}")
                    message1.configure(text=f"Face registered for Tenant_IC_Number: {Tenant_IC_Number}")
                    break

                except Exception as e:
                    print(f"Error processing face: {str(e)}")
                    continue

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Clean up if no face was detected
        if not face_detected:
            cam.release()
            cv2.destroyAllWindows()
            messagebox.showwarning("Warning", "No face was detected. Please try again.")
            return

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        print(f"Error: {str(e)}")

    face_scan_register_window.withdraw()
    show_register_frame()


#######################################################################################

def TrackImages():
    global attendance_action

    # 打开摄像头
    cam = cv2.VideoCapture(0)

    Database()

    # Get the camera window
    cv2.namedWindow("Taking Attendance", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Taking Attendance", cv2.WND_PROP_TOPMOST, 1)

    # Set start time
    start_time = time.time()
    recognized = False
    name_recognized = None

    while True:
        ret, im = cam.read()
        if not ret:
            break

        # Show the camera feed
        cv2.imshow("Taking Attendance", im)

        # Check if 20 seconds have passed
        if time.time() - start_time > 20:
            break

        # 检测人脸
        try:
            # Use extract_faces instead of detectFace
            faces = DeepFace.extract_faces(img_path=im, enforce_detection=False, detector_backend='opencv')

            if len(faces) == 0:
                continue

            embedding = DeepFace.represent(im, model_name='Facenet', enforce_detection=False)[0]["embedding"]

            # 从数据库获取已保存的嵌入
            cursor.execute("SELECT Tenant_IC_Number, name, embedding FROM FaceEmbeddings")
            records = cursor.fetchall()

            for record in records:
                saved_Tenant_IC_Number, name, saved_embedding = record
                similarity = (1 - distance) * 100
                if similarity >= 80:  # Only recognize if similarity is 80% or higher
                    ts = time.time()
                    current_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    current_date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')

                    # 更新数据库考勤记录
                    if attendance_action == "Clock In":
                        cursor.execute("""INSERT INTO Attendance 
                                    (Tenant_IC_Number, name, date, clock_in_time) 
                                    VALUES (?, ?, ?, ?)""",
                                       (saved_Tenant_IC_Number, name, current_date, current_time))
                    else:
                        cursor.execute("""UPDATE Attendance 
                                    SET clock_out_time = ? 
                                    WHERE Tenant_IC_Number = ? AND date = ?""",
                                       (current_time, saved_Tenant_IC_Number, current_date))

                    conn.commit()
                    recognized = True
                    name_recognized = name
                    break

            if recognized:
                break

        except Exception as e:
            continue

        if cv2.waitKey(1) == ord('q'):
            break

    # Release camera and close windows
    cam.release()
    cv2.destroyAllWindows()

    # Show result message
    if recognized:
        messagebox.showinfo("Attendance", f"{attendance_action} Successful for {name_recognized}")
    else:
        messagebox.showerror("Attendance", "Face Recognition Failed - No matching face found")

    display_attendance()


def display_attendance():
    global cursor, tv
    for row in tv.get_children():
        tv.delete(row)

    try:
        # Reinitialize database connection if needed
        if not conn or not cursor:
            Database()

        cursor.execute("""SELECT Tenant_IC_Number, name, date, clock_in_time, clock_out_time 
                     FROM Attendance""")
        rows = cursor.fetchall()
        for row in rows:
            tv.insert('', 'end', text=row[0], values=(row[1], row[2], row[3], row[4]))
    except Exception as e:
        print(f"Error: {str(e)}")
        Database()  # Try to reinitialize database connection


latitude = None
longtitude = None


@app.route('/update_location', methods=['POST'])
def update_location():
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    status = data.get('status', "Clock In")  # Default to "Clock In"
    # Retrieve Tenant_IC_Number from login_profile
    tenant_ic_number = login_profile.get('IC_Number')
    print(
        f"Received location update - Latitude: {latitude}, Longitude: {longitude}, Status: {status}, Tenant IC: {tenant_ic_number}")
    if not tenant_ic_number:
        return jsonify({"error": "Tenant IC Number is required"}), 400
    try:
        conn = sqlite3.connect('govRental.db')
        cursor = conn.cursor()

        # Get today's date in the correct format
        current_date = datetime.datetime.now().strftime('%d-%m-%Y')

        # Update location based on status
        if status == "Clock In":
            cursor.execute("""
                UPDATE Attendance 
                SET Clock_In_latitude = ?,
                    Clock_In_longitude = ?
                WHERE Tenant_IC_Number = ? 
                AND date = ?
                AND clock_in_time IS NOT NULL
            """, (latitude, longitude, tenant_ic_number, current_date))
        else:  # Clock Out
            cursor.execute("""
                UPDATE Attendance 
                SET Clock_Out_latitude = ?,
                    Clock_Out_longitude = ?
                WHERE Tenant_IC_Number = ? 
                AND date = ?
                AND clock_out_time IS NOT NULL
            """, (latitude, longitude, tenant_ic_number, current_date))
        # Check if update was successful
        if cursor.rowcount == 0:
            print(f"No attendance record found to update for {tenant_ic_number} on {current_date}")
            return jsonify({"error": "No attendance record found to update"}), 404
        conn.commit()
        # Now get the stall location to determine status
        cursor.execute("""
            SELECT Latitude, Longitude 
            FROM Stall 
            WHERE Tenant_ID = (
                SELECT Tenant_ID 
                FROM Tenant 
                WHERE Tenant_IC_Number = ?
            )
        """, (tenant_ic_number,))

        stall_location = cursor.fetchone()

        if stall_location:
            stall_lat, stall_lon = float(stall_location[0]), float(stall_location[1])
            coords_1 = (float(latitude), float(longitude))
            coords_2 = (stall_lat, stall_lon)
            distance = geopy.distance.geodesic(coords_1, coords_2).meters
            location_status = "Correct" if distance <= 20000 else "Wrong"

            # Update the status in the database
            if status == "Clock In":
                cursor.execute("""
                    UPDATE Attendance 
                    SET Clock_In_Status = ?
                    WHERE Tenant_IC_Number = ? AND date = ?
                """, (location_status, tenant_ic_number, current_date))
            else:
                cursor.execute("""
                    UPDATE Attendance 
                    SET Clock_Out_Status = ?
                    WHERE Tenant_IC_Number = ? AND date = ?
                """, (location_status, tenant_ic_number, current_date))

            conn.commit()

            return jsonify({
                "message": "Location updated successfully",
                "status": location_status,
                "distance": f"{distance:.2f} meters from stall"
            }), 200
        else:
            print(f"No stall found for tenant {tenant_ic_number}")
            return jsonify({
                "message": "Location updated but stall location not found",
                "status": "Wrong",
                "distance": "Unknown"
            }), 200
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


def start_flask(status):
    def run_app():
        app.run(debug=False, use_reloader=False)

    threading.Thread(target=run_app).start()

    # Optional: add a short delay to ensure the server has started
    time.sleep(1)  # Increase if needed

    # Open the browser with the status parameter
    webbrowser.open_new(f'http://127.0.0.1:5000/?status={status}')


def clock_in():
    global status
    status = "Clock In"
    # Ask for Tenant ID
    ic_number = tsd.askstring('IC Verification', 'Please enter your Tenant IC Number:')
    if not ic_number:
        return
    try:
        # Check if Tenant ID exists in database
        cursor.execute("SELECT name, faceImagePath FROM FaceEmbeddings WHERE Tenant_IC_Number=?", (ic_number,))
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "Tenant ID not found in database!")
            return
        name, stored_image_path = result
        # Open camera for face verification
        cam = cv2.VideoCapture(0)
        cv2.namedWindow("Face Verification", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Face Verification", cv2.WND_PROP_TOPMOST, 1)
        face_detected = False
        start_time = time.time()
        while not face_detected and (time.time() - start_time) < 20:  # 20 second timeout
            ret, frame = cam.read()
            if not ret:
                break
            # Show live preview
            cv2.imshow("Face Verification", frame)
            try:
                # Detect face in current frame
                faces = DeepFace.extract_faces(img_path=frame,
                                               enforce_detection=False,
                                               detector_backend='opencv')
                if len(faces) > 0:
                    # Save current frame temporarily
                    temp_path = "temp_verification.jpg"
                    cv2.imwrite(temp_path, frame)
                    # Compare with stored image
                    result = DeepFace.verify(
                        img1_path=stored_image_path,
                        img2_path=temp_path,
                        model_name="Facenet",
                        enforce_detection=False
                    )
                    # Clean up temp file
                    os.remove(temp_path)
                    similarity = (1 - result["distance"]) * 100
                    if similarity >= 80:  # Only verify if similarity is 80% or higher
                        face_detected = True
                        # Record attendance with initial null values for location
                        ts = time.time()
                        current_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                        current_date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
                        cursor.execute("""INSERT INTO Attendance 
                                    (Tenant_IC_Number, name, date, clock_in_time, 
                                     Clock_In_longitude, Clock_In_latitude, Clock_In_Status) 
                                    VALUES (?, ?, ?, ?, NULL, NULL, NULL)""",
                                       (ic_number, name, current_date, current_time))
                        conn.commit()
                        # Close camera window
                        cam.release()
                        cv2.destroyAllWindows()
                        # Show success message
                        messagebox.showinfo("Success",
                                            f"Welcome {name}!\nVerification Successful (Similarity: {similarity:.2f}%)\nTime: {current_time}")
                        # Start Flask server for live location with Clock In status
                        start_flask(status)
                        # Update attendance display
                        display_attendance()
                        return
            except Exception as e:
                print(f"Frame processing error: {str(e)}")
                continue
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        # Clean up
        cam.release()
        cv2.destroyAllWindows()
        if not face_detected:
            messagebox.showerror("Error", "Face verification failed or timeout reached!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        print(f"Error: {str(e)}")


def clock_out():
    global status
    status = "Clock Out"
    # Ask for Tenant ID
    ic_number = tsd.askstring('IC Verification', 'Please enter your Tenant IC Number:')
    if not ic_number:
        return
    try:
        # Check if Tenant ID exists in database
        cursor.execute("SELECT name, faceImagePath FROM FaceEmbeddings WHERE Tenant_IC_Number=?", (ic_number,))
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "Tenant IC Number not found in database!")
            return
        name, stored_image_path = result
        # Check if already clocked in today
        current_date = datetime.datetime.now().strftime('%d-%m-%Y')
        cursor.execute("""SELECT clock_in_time FROM Attendance 
                    WHERE Tenant_IC_Number=? AND date=? AND clock_out_time IS NULL""",
                       (ic_number, current_date))
        if not cursor.fetchone():
            messagebox.showerror("Error", "No clock-in record found for today!")
            return
        # Open camera for face verification
        cam = cv2.VideoCapture(0)
        cv2.namedWindow("Face Verification", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Face Verification", cv2.WND_PROP_TOPMOST, 1)
        face_detected = False
        start_time = time.time()
        while not face_detected and (time.time() - start_time) < 20:  # 20 second timeout
            ret, frame = cam.read()
            if not ret:
                break
            # Show live preview
            cv2.imshow("Face Verification", frame)
            try:
                # Detect face in current frame
                faces = DeepFace.extract_faces(img_path=frame,
                                               enforce_detection=False,
                                               detector_backend='opencv')
                if len(faces) > 0:
                    # Save current frame temporarily
                    temp_path = "temp_verification.jpg"
                    cv2.imwrite(temp_path, frame)
                    # Compare with stored image
                    result = DeepFace.verify(
                        img1_path=stored_image_path,
                        img2_path=temp_path,
                        model_name="Facenet",
                        enforce_detection=False
                    )
                    # Clean up temp file
                    os.remove(temp_path)
                    similarity = (1 - result["distance"]) * 100
                    if similarity >= 80:  # Only verify if similarity is 80% or higher
                        face_detected = True
                        # Start Flask with Clock Out status
                        start_flask(status)
                        # Record clock out with initial null values for location
                        current_time = datetime.datetime.now().strftime('%H:%M:%S')
                        cursor.execute("""UPDATE Attendance 
                                    SET clock_out_time = ?,
                                        Clock_Out_longitude = NULL,
                                        Clock_Out_latitude = NULL,
                                        Clock_Out_Status = NULL
                                    WHERE Tenant_IC_Number = ? 
                                    AND date = ? 
                                    AND clock_out_time IS NULL""",
                                       (current_time, ic_number, current_date))
                        conn.commit()
                        # Close camera window
                        cam.release()
                        cv2.destroyAllWindows()
                        # Show success message
                        messagebox.showinfo("Success",
                                            f"Goodbye {name}!\nVerification Successful (Similarity: {similarity:.2f}%)\nTime: {current_time}")
                        # Update attendance display
                        display_attendance()
                        return
            except Exception as e:
                print(f"Frame processing error: {str(e)}")
                continue
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        # Clean up
        cam.release()
        cv2.destroyAllWindows()
        if not face_detected:
            messagebox.showerror("Error", "Face verification failed or timeout reached!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        print(f"Error: {str(e)}")


def show_main_components(self):
    # 显示顶部栏
    self.top_frame.pack(fill=tk.X)
    # 显示按钮区域
    self.buttons_frame.pack(fill=tk.X)


######################################## USED STUFFS ############################################


######################################## GUI FRONT-END ###########################################
def show_attendance_frame():
    # Hide registration window
    face_scan_register_window.withdraw()
    # Show attendance window
    attendance_window.deiconify()


def show_registration_frame():
    # Hide attendance window
    attendance_window.withdraw()
    # Show registration window
    face_scan_register_window.deiconify()


def attendance():
    global attendance_window, message, tv, key, clock, cursor, conn  # Add c and conn here
    key = ''

    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
    day, month, year = date.split("-")

    mont = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June',
            '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}

    attendance_window = tk.Tk()
    attendance_window.geometry("1920x1080")
    attendance_window.resizable(True, False)
    attendance_window.title("Attendance System")
    attendance_window.configure(background='alice blue')
    attendance_window.state("zoomed")

    frame1 = tk.Frame(attendance_window, bg="LightSkyBlue3")
    frame1.place(relx=0.11, rely=0.17, relwidth=0.75, relheight=0.80)

    message3 = tk.Label(attendance_window, text="Face Recognition Based Attendance Monitoring System", fg="black",
                        bg="alice blue",
                        width=55, height=1, font=('comic', 29, ' bold '))
    message3.place(x=290, y=10)

    frame3 = tk.Frame(attendance_window, bg="LightSkyBlue3")
    frame3.place(relx=0.52, rely=0.09, relwidth=0.09, relheight=0.07)

    frame4 = tk.Frame(attendance_window, bg="")
    frame4.place(relx=0.36, rely=0.09, relwidth=0.16, relheight=0.07)

    datef = tk.Label(frame4, text=day + "-" + mont[month] + "-" + year + "  |  ", fg="grey", bg="alice blue", width=55,
                     height=1, font=('comic', 22, ' bold '))
    datef.pack(fill='both', expand=1)

    clock = tk.Label(frame3, fg="grey", bg="alice blue", width=55, height=1, font=('comic', 22, ' bold '))
    clock.pack(fill='both', expand=1)
    tick()

    head1 = tk.Label(frame1, text="       For Already Registered                       ", fg="black",
                     bg="SkyBlue4", width=110, font=('comic', 17, ' bold '))
    head1.place(x=0, y=0)

    lbl3 = tk.Label(frame1, text="Attendance", width=20, fg="black", bg="LightSkyBlue3", height=1,
                    font=('comic', 17, ' bold '))
    lbl3.place(x=590, y=210)

    ################## TREEVIEW ATTENDANCE TABLE ####################

    tv = ttk.Treeview(frame1, height=16, columns=('name', 'date', 'clock_in_time', 'clock_out_time'))
    tv.column('#0', width=150)
    tv.column('name', width=130)
    tv.column('date', width=130)
    tv.column('clock_in_time', width=130)
    tv.column('clock_out_time', width=130)
    tv.place(x=400, y=280)
    tv.heading('#0', text='ID')
    tv.heading('name', text='NAME')
    tv.heading('date', text='DATE')
    tv.heading('clock_in_time', text='CLOCK IN')
    tv.heading('clock_out_time', text='CLOCK OUT')

    ###################### SCROLLBAR ################################

    # scroll = ttk.Scrollbar(frame1, orient='vertical', command=tv.yview)
    # scroll.place(x=867, y=151)
    # tv.configure(yscrollcommand=scroll.set)

    ###################### BUTTONS ##################################

    clock_in_button = ctk.CTkButton(frame1, text="Clock In", command=clock_in, fg_color="MediumPurple4",
                                    hover_color="#483D8B", width=350, height=40, corner_radius=8,
                                    font=('comic', 25, 'bold'))
    clock_in_button.place(x=280, y=130)

    clock_out_button = ctk.CTkButton(frame1, text="Clock Out", command=clock_out, fg_color="MediumPurple4",
                                     hover_color="#483D8B", width=350, height=40, corner_radius=8,
                                     font=('comic', 25, 'bold'))
    clock_out_button.place(x=830, y=130)

    quit_button = ctk.CTkButton(frame1, text="Quit", command=attendance_window.destroy, fg_color="MediumPurple4",
                                hover_color="#483D8B", width=350, height=40, corner_radius=8,
                                font=('comic', 25, 'bold'))
    quit_button.place(x=550, y=650)

    display_attendance()
    return attendance_window


def face_scan_register():
    global face_scan_register_window, message1, txt, txt2, key, clock, cursor, conn  # Add c and conn here
    key = ''

    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
    day, month, year = date.split("-")

    mont = {'01': 'January', '02': 'February', '03': 'March', '04': 'May', '06': 'June',
            '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}

    face_scan_register_window = tk.Tk()
    face_scan_register_window.geometry("1920x1080")
    face_scan_register_window.resizable(True, False)
    face_scan_register_window.title("Face Registration")
    face_scan_register_window.configure(background='alice blue')
    face_scan_register_window.state("zoomed")

    frame2 = tk.Frame(face_scan_register_window, bg="LightSkyBlue3")
    frame2.place(relx=0.11, rely=0.17, relwidth=0.75, relheight=0.80)

    frame3 = tk.Frame(face_scan_register_window, bg="LightSkyBlue3")
    frame3.place(relx=0.52, rely=0.09, relwidth=0.25, relheight=0.07)

    frame4 = tk.Frame(face_scan_register_window, bg="")
    frame4.place(relx=0.36, rely=0.09, relwidth=0.25, relheight=0.07)

    message3 = tk.Label(face_scan_register_window, text="Face Recognition Based Attendance Monitoring System",
                        fg="black", bg="alice blue",
                        width=55, height=1, font=('comic', 29, ' bold '))
    message3.place(x=290, y=10)

    datef = tk.Label(frame4, text=day + "-" + mont[month] + "-" + year + "  |  ", fg="grey", bg="alice blue", width=55,
                     height=1, font=('comic', 22, ' bold '))
    datef.pack(fill='both', expand=1)

    clock = tk.Label(frame3, fg="grey", bg="alice blue", width=45, height=1, font=('comic', 22, ' bold '))
    clock.pack(fill='both', expand=1)
    tick()

    head2 = tk.Label(frame2, text="              For New Registrations                       ",
                     fg="black", bg="SkyBlue4", width=110, font=('comic', 17, ' bold '))
    head2.place(x=0, y=0)

    # Tenant IC Number Entry
    lbl = tk.Label(frame2, text="Enter Tenant IC Number", width=20, height=1, fg="black",
                   bg="LightSkyBlue3", font=('comic', 17, ' bold '))
    lbl.place(x=600, y=150)

    def fetch_tenant_name(event):
        # Ensure the database connection is open
        Database()

        ic_number = txt.get()
        try:
            cursor.execute("SELECT Tenant_Username FROM Tenant WHERE Tenant_IC_Number=?", (ic_number,))
            result = cursor.fetchone()
            if result:
                txt2.delete(0, 'end')
                txt2.insert(0, result[0])
            else:
                messagebox.showwarning("Warning", "No tenant found with this IC number")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching tenant details: {str(e)}")
        finally:
            if conn:
                conn.close()

    # Replace standard Entry with CTkEntry
    txt = ctk.CTkEntry(frame2, width=300, height=35, corner_radius=10,
                       font=('comic', 15, 'bold'), fg_color="white")
    txt.place(x=600, y=200)
    txt.bind('<FocusOut>', fetch_tenant_name)

    # Name Entry
    lbl2 = tk.Label(frame2, text="Enter Name", width=20, fg="black",
                    bg="LightSkyBlue3", font=('comic', 17, ' bold '))
    lbl2.place(x=600, y=250)

    # Replace standard Entry with CTkEntry
    txt2 = ctk.CTkEntry(frame2, width=300, height=35, corner_radius=10,
                        font=('comic', 15, 'bold'), fg_color="white")
    txt2.place(x=600, y=300)

    message1 = tk.Label(frame2, text="1) Take Images  >>>  2) Save Profile", bg="LightSkyBlue3", fg="black", width=39,
                        height=1,
                        activebackground="LightSkyBlue3", font=('comic', 15, ' bold '))
    message1.place(x=510, y=380)

    message = tk.Label(frame2, text="", bg="LightSkyBlue3", fg="black", width=39, height=1,
                       activebackground="LightSkyBlue3",
                       font=('comic', 16, ' bold '))
    message.place(x=500, y=530)

    res = 0
    exists = os.path.isfile(r"StudentDetails\StudentDetails.csv")  # Use raw string
    if exists:
        with open(r"StudentDetails\StudentDetails.csv", 'r') as csvFile1:  # Use raw string
            reader1 = csv.reader(csvFile1)
            for l in reader1:
                res = res + 1
        res = (res // 2) - 1
        csvFile1.close()
    else:
        res = 0
    message.configure(text='Total Registrations till now  : ' + str(res))

    ##################### MENUBAR #################################

    menubar = tk.Menu(face_scan_register_window, relief='ridge')
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label='Exit', command=face_scan_register_window.destroy)
    menubar.add_cascade(label='Help', font=('comic', 29, ' bold '), menu=filemenu)
    face_scan_register_window.config(menu=menubar)  # Add this line

    # Single clear button to clear both fields
    def clear_fields():
        txt.delete(0, 'end')
        txt2.delete(0, 'end')

    clearButton = ctk.CTkButton(frame2, text="Clear", command=clear_fields, fg_color="MediumPurple4",
                                hover_color="#483D8B", width=120, height=40, corner_radius=8,
                                font=('comic', 18, 'bold'))
    # clearButton.place(x=800, y=250)
    clearButton.place(x=800, y=450)

    takeImg = ctk.CTkButton(frame2, text="Take Images", command=TakeImages, fg_color="MediumPurple4",
                            hover_color="#483D8B", width=340, height=40, corner_radius=8, font=('comic', 18, 'bold'))
    # takeImg.place(x=550, y=450)
    takeImg.place(x=450, y=450)

    return face_scan_register_window


def main():
    global cursor, conn

    # Initialize database connection
    Database()

    # Create both windows
    attendance_window = attendance()
    face_scan_register_window = face_scan_register()

    # Initially hide attendance window
    attendance_window.withdraw()

    # Start with registration window
    face_scan_register_window.mainloop()

    # Don't close the database connection here

    # The connection will be managed by init_database() when needed


def send_verification_email(email_address):
    global VERIFICATION_CODE
    VERIFICATION_CODE = str(random.randint(100000, 999999))  # 生成六数字验证码

    # 电子邮件的内容
    sender_email = "inti.all21115@gmail.com"
    sender_password = "zsmw xujc wvln euvt"
    subject = "Email Verification Code"
    body = f"Your verification code is {VERIFICATION_CODE}. Please enter this code to complete your registration."

    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email_address
    msg['Subject'] = subject

    # 邮件正文
    msg.attach(MIMEText(body, 'plain'))

    # 使用Gmail SMTP服务器
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email_address, msg.as_string())
        server.quit()
        messagebox.showinfo("Email Sent", f"Verification code has been sent to {email_address}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send email: {str(e)}")


# 验证箱格式
def is_valid_email(email_address):
    try:
        valid = validate_email(email_address)
        return True
    except EmailNotValidError as e:
        messagebox.showerror("Invalid Email", str(e))
        return False


def show_verification_frame():
    for widget in root.winfo_children():
        if isinstance(widget, tk.Frame):
            widget.destroy()

    frame = Frame(root, padx=20, pady=50)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    frame.config(bg='#FFCC80')

    # Title label
    Label(frame, text="Enter Verification Code", font=('Arial', 16, 'bold'), bg='#FFCC80').grid(row=0, column=0,
                                                                                                columnspan=2, pady=20)

    # Verification code entry
    verification_code_var = StringVar()
    ctk.CTkEntry(
        frame,
        textvariable=verification_code_var,
        width=200,
        height=35,
        corner_radius=10,
        placeholder_text="Enter 6-digit code"
    ).grid(row=1, column=0, columnspan=2, pady=10, padx=20)

    # Verify button using CustomTkinter
    ctk.CTkButton(
        frame,
        text="Verify",
        command=lambda: verify_code(verification_code_var.get()),
        fg_color="red",
        text_color="black",
        hover_color="darkred",
        width=120,
        height=35,
        corner_radius=8
    ).grid(row=2, column=0, columnspan=2, pady=20)


# 验证用户输入的验证码
def verify_code(user_code):
    if user_code == VERIFICATION_CODE:
        # Verify code successful
        # Destroy the verification frame and main window
        for widget in root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.destroy()

        # Create new main window
        main_window = tk.Toplevel(root)
        main_window.geometry("1920x1080")
        main_window.state("zoomed")

        # Create RentalSystemApp instance
        app = RentalSystemApp(main_window)

        # Show main components
        app.top_frame.pack(fill=tk.X)
        app.buttons_frame.pack(fill=tk.X)

        # Update the database with registration info
        complete_registration()

        # Hide the root window
        root.withdraw()



    else:
        messagebox.showerror("Error", "Invalid verification code.")


# Role Selection Screen
def show_role_selection():
    for widget in root.winfo_children():
        if isinstance(widget, tk.Frame):  # 保留视频背景
            widget.destroy()

    frame = Frame(root, padx=20, pady=50)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # 居中显示
    frame.config(bg='#FAEBD7')

    # 欢迎标签
    Label(frame, text="Welcome!", font=('Impact', 24), bg='#FAEBD7').grid(row=0, column=0, columnspan=2, pady=20)

    # Admin 和 Tenant 按钮
    Button(frame, text="Admin", font=('Palatino', 18, 'bold'), bg="#FFCC80", width=15, bd=18,
           command=show_admin_login_frame).grid(row=1, column=0, padx=20, pady=20)  # link to admin login frame
    Button(frame, text="Tenant", font=('Palatino', 18, 'bold'), bg="#FFCC80", width=15, bd=18,
           command=show_login_frame).grid(row=1, column=1, padx=20, pady=20)


# Admin Login Screen
def show_admin_login_frame():
    try:
        # Get directory of current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        admin_path = os.path.join(current_dir, "Admin.py")

        # Check if admin.py exists
        if not os.path.exists(admin_path):
            messagebox.showerror("Error", "Admin page (Admin.py) not found")
            return

        # Get current user ID
        user_id = USER_IC_NUMBER_LOGIN.get()

        # Save user ID to JSON file
        admin_data = {
            "admin_id": user_id
        }
        json_path = os.path.join(current_dir, "admin_data.json")
        with open(json_path, "w") as f:
            json.dump(admin_data, f)

        # Pass JSON file path as argument
        process = subprocess.Popen([sys.executable, admin_path, "--admin_data", json_path])

        # Optionally, wait for the process to start
        process.wait()

        # Close current window
        root.destroy()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch admin page: {e}")


# Show Login frame for Tenants
def show_login_frame():
    for widget in root.winfo_children():
        if isinstance(widget, tk.Frame):  # 保留视频背景
            widget.destroy()

    frame = Frame(root, padx=60, pady=30)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # 居中显示
    frame.config(bg='#FFCC80')

    Label(frame, text="Login", font=('Impact', 20, "bold"), bg='#FFCC80').grid(row=0, column=0, columnspan=2, pady=20)

    Label(frame, text="Welcome! Tenant", font=('Impact', 20, "bold"), bg='#FFCC80').grid(row=1, column=0, columnspan=2,
                                                                                         pady=10)

    Label(frame, text="User IC Number : ", font=('Segoe Fluent Iconsr', 10, "bold"), bg='#FFCC80').grid(row=2, column=0)
    ctk.CTkEntry(frame, textvariable=USER_IC_NUMBER_LOGIN, width=200, height=30, corner_radius=10).grid(row=2, column=1,
                                                                                                        pady=5)

    Label(frame, text="Password : ", bg='#FFCC80', font=('Segoe Fluent Iconsr', 10, "bold")).grid(row=3, column=0)
    ctk.CTkEntry(frame, textvariable=PASSWORD_LOGIN, show='*', width=200, height=30, corner_radius=10).grid(row=3,
                                                                                                            column=1,
                                                                                                            pady=5)

    # Replace standard Button with CTkButton for Login
    login_button = ctk.CTkButton(
        frame,
        text="Login",
        command=login,
        fg_color="#FD5602",  # Orange color
        text_color="black",
        hover_color="#FF8C00",  # Darker orange for hover
        width=120,
        height=35,
        corner_radius=8
    )
    login_button.grid(row=4, column=0, columnspan=2, pady=10)

    # Replace standard Button with CTkButton for Back
    back_button = ctk.CTkButton(
        frame,
        text="Back",
        command=show_role_selection,
        fg_color="#4B0082",  # Indigo color
        text_color="white",
        hover_color="#2E0854",  # Darker indigo for hover
        width=120,
        height=35,
        corner_radius=8
    )
    back_button.grid(row=5, column=0, columnspan=2, pady=5)


# Show Register frame for Tenants
def show_register_frame():
    for widget in root.winfo_children():
        if isinstance(widget, tk.Frame):  # 保留视频背景
            widget.destroy()

    frame = Frame(root, padx=20, pady=30)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # 居中显示
    frame.config(bg='#FFCC80')

    # 更新界面标题
    Label(frame, text="Tenant Information", font=('Impact', 20), fg='black', bg='#FFCC80').grid(row=0, column=1,
                                                                                                columnspan=1,
                                                                                                pady=20)

    Label(frame, text="Update Your Information And Change Your Password", font=('Constantia', 15), fg='red',
          bg='#FFCC80').grid(row=1, column=1, columnspan=1, pady=20)

    # 用户名
    Label(frame, text="Username : ", bg='#FFCC80', font=('Segoe Fluent Iconsr', 10, "bold")).grid(row=2, column=0)
    username_entry = ctk.CTkEntry(frame, textvariable=USERNAME_REGISTER, width=200, height=30, corner_radius=10,
                                  state='disabled')
    username_entry.grid(row=2, column=1, pady=10)

    # Fetch username from database based on IC number
    conn = sqlite3.connect('govRental.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Tenant_Username FROM Tenant WHERE Tenant_IC_Number=?", (login_profile['IC_Number'],))
    result = cursor.fetchone()
    if result:
        USERNAME_REGISTER.set(result[0])
    conn.close()

    # IC Number (从登录时读取，不允许修改)
    Label(frame, text="IC Number : ", bg='#FFCC80', font=('Segoe Fluent Iconsr', 10, "bold")).grid(row=3, column=0)
    ic_entry = ctk.CTkEntry(frame, textvariable=IC_NUMBER_REGISTER, width=200, height=30, corner_radius=10,
                            state='disabled')
    ic_entry.grid(row=3, column=1, pady=5)
    IC_NUMBER_REGISTER.set(login_profile['IC_Number'])  # 从登录信息读取IC Number

    # 性别
    Label(frame, text="Gender : ", bg='#FFCC80', font=('Segoe Fluent Iconsr', 10, "bold")).grid(row=4, column=0)
    # Replace standard Radiobuttons with CTkRadioButton
    ctk.CTkRadioButton(frame, text="Male", variable=GENDER, value="Male", fg_color="#FD5602",
                       bg_color='#FFCC80').grid(row=4, column=1)
    ctk.CTkRadioButton(frame, text="Female", variable=GENDER, value="Female", fg_color="#FD5602",
                       bg_color='#FFCC80').grid(row=4, column=2)

    # 电话号码
    Label(frame, text="Phone Number : ", bg='#FFCC80', font=('Segoe Fluent Iconsr', 10, "bold")).grid(row=5, column=0)
    ctk.CTkEntry(frame, textvariable=PHONE_NUMBER, width=200, height=30, corner_radius=10).grid(row=5, column=1, pady=5)

    # 邮箱地址
    Label(frame, text="Email Address : ", bg='#FFCC80', font=('Segoe Fluent Iconsr', 10, "bold")).grid(row=6, column=0)
    ctk.CTkEntry(frame, textvariable=EMAIL_ADDRESS, width=200, height=30, corner_radius=10).grid(row=6, column=1,
                                                                                                 pady=5)

    # 密码
    Label(frame, text="Password : ", bg='#FFCC80', font=('Segoe Fluent Iconsr', 10, "bold")).grid(row=7, column=0)
    ctk.CTkEntry(frame, textvariable=PASSWORD_REGISTER, show='*', width=200, height=30, corner_radius=10).grid(row=7,
                                                                                                               column=1,
                                                                                                               pady=5)

    # 确认密码
    Label(frame, text="Confirm Password : ", bg='#FFCC80', font=('Segoe Fluent Iconsr', 10, "bold")).grid(row=8,
                                                                                                          column=0)
    ctk.CTkEntry(frame, textvariable=CONFIRM_PASSWORD, show='*', width=200, height=30, corner_radius=10).grid(row=8,
                                                                                                              column=1,
                                                                                                              pady=5)

    # Replace standard Buttons with CTkButton
    face_scan_button = ctk.CTkButton(
        frame,
        text="Face Scan",
        command=face_scan_register,
        fg_color="#FD5602",  # Orange color
        text_color="black",
        hover_color="#FF8C00",  # Darker orange for hover
        width=120,
        height=35,
        corner_radius=8
    )
    face_scan_button.grid(row=10, column=1, pady=10)

    save_button = ctk.CTkButton(
        frame,
        text="Save",
        command=save_update,
        fg_color="#4B0082",  # Indigo color
        text_color="white",
        hover_color="#2E0854",  # Darker indigo for hover
        width=120,
        height=35,
        corner_radius=8
    )
    save_button.grid(row=11, column=1, pady=10)


def save_update():
    try:
        Database()
        username = USERNAME_REGISTER.get().strip()
        gender = GENDER.get().strip()
        phone_number = PHONE_NUMBER.get().strip()
        email_address = EMAIL_ADDRESS.get().strip()
        password = PASSWORD_REGISTER.get().strip()
        confirm_password = CONFIRM_PASSWORD.get().strip()

        # Validate inputs
        if len(phone_number) > 11:
            messagebox.showerror("Error", "Phone Number must not exceed 11 characters.")
            return

        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long.")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        if not is_valid_email(email_address):
            return

        # Declare TEMP_REGISTER_DATA as global to use it in other functions
        global TEMP_REGISTER_DATA
        TEMP_REGISTER_DATA = {
            'username': username,
            'gender': gender,
            'phone_number': phone_number,
            'email_address': email_address,
            'password': password,
            'ic_number': login_profile['IC_Number']  # Based on the logged-in user
        }

        # Send verification email
        send_verification_email(email_address)

        # Show the verification frame for user to input the verification code
        show_verification_frame()

    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        if conn:
            conn.close()


# Admin login function
def login_admin():
    # Add your admin login logic here
    username = USER_IC_NUMBER_LOGIN.get()
    password = PASSWORD_LOGIN.get()

    if username == "admin" and password == "password":
        messagebox.showinfo("Login Success", "Welcome, Admin!")
    else:
        messagebox.showerror("Login Failed", "Invalid admin credentials.")


# Tenant login function
def login():
    Database()
    ic_number = USER_IC_NUMBER_LOGIN.get()
    password = PASSWORD_LOGIN.get()

    # First query to get all tenant details
    cursor.execute("""
        SELECT Tenant_ID, Tenant_Username, Tenant_IC_Number, Tenant_Gender, 
               Tenant_Phone_Number, Tenant_Email_Address, Tenant_Password 
        FROM Tenant 
        WHERE Tenant_IC_Number=? AND Tenant_Password=?
    """, (ic_number, password))
    tenant = cursor.fetchone()

    if tenant:
        tenant_id = tenant[0]  # Get Tenant_ID from the result
        login_profile["IC_Number"] = ic_number
        login_profile["Password"] = password

        # Print tenant details
        print(f"Login successful for:")
        print(f"Tenant ID: {tenant_id}")
        print(f"IC Number: {ic_number}")
        print(f"Username: {tenant[1]}")

        messagebox.showinfo("Login", "Login Successful!")

        # Check if any of the required fields are null
        if all(tenant[1:6]):
            root.withdraw()
            main_window = tk.Toplevel(root)
            main_window.geometry("1920x1080")
            main_window.state("zoomed")
            # Create RentalSystemApp instance
            app = RentalSystemApp(main_window)
            # Show main components
            app.top_frame.pack(fill=tk.X)
            app.buttons_frame.pack(fill=tk.X)
        else:
            show_register_frame()
    else:
        messagebox.showerror("Login", "Invalid IC Number or Password")
    conn.close()


# Tenant register function
# Tenant register function - 第一次点击"Register"时仅发送验证码

# 完成注册操作 - 验证码正确后执行
def complete_registration():
    try:
        Database()

        global TEMP_REGISTER_DATA
        data = TEMP_REGISTER_DATA

        cursor.execute("SELECT * FROM Tenant WHERE Tenant_IC_Number=?", (data['ic_number'],))
        existing_tenant = cursor.fetchone()

        if existing_tenant:
            # Update user info in the Tenant table
            cursor.execute("""
                UPDATE Tenant
                SET Tenant_Username=?, Tenant_Gender=?, Tenant_Phone_Number=?, Tenant_Email_Address=?, Tenant_Password=?
                WHERE Tenant_IC_Number=?
            """, (data['username'], data['gender'], data['phone_number'], data['email_address'], data['password'],
                  data['ic_number']))
            conn.commit()

            # Update login_profile
            login_profile['Password'] = data['password']

            messagebox.showinfo("Update", "Your Information Updated Successfully!")

        else:
            messagebox.showerror("Error", "IC Number not found.")

    except sqlite3.IntegrityError as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if conn:
            conn.close()


video_file = r"C:/Kai Shuang/Goverment Stall Rental System.mp4"
video_app = VideoApp(root, video_file)

# Setup database
Database()

# Show role selection frame
show_role_selection()

root.mainloop()