import cv2
import pytesseract
import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


mysql_config = {
    'host': 'localhost',
    'database': 'car_recognition',
    'user': 'root',
    'password': '1234'
}

def insert_plate_number(plate_number):
    try:
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        sql_insert_query = """INSERT INTO plates (plate_number) VALUES (%s)"""
        cursor.execute(sql_insert_query, (plate_number,))
        connection.commit()
        messagebox.showinfo("Success", f"Plate number '{plate_number}' inserted successfully")
    except Error as e:
        messagebox.showerror("Error", f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def retrieve_plate_numbers():
    try:
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        sql_select_query = """SELECT plate_number FROM plates"""
        cursor.execute(sql_select_query)
        rows = cursor.fetchall()
        plate_numbers = [row[0] for row in rows]
        return plate_numbers
    except Error as e:
        messagebox.showerror("Error", f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def check_plate_exists(plate_number):
    try:
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        sql_select_query = """SELECT COUNT(*) FROM plates WHERE plate_number = %s"""
        cursor.execute(sql_select_query, (plate_number,))
        count = cursor.fetchone()[0]
        return count > 0
    except Error as e:
        messagebox.showerror("Error", f"Error: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def recognize_plate(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    custom_config = r'--oem 3 --psm 8'
    text = pytesseract.image_to_string(gray, config=custom_config)

    plate_number = text.strip()
    return plate_number

def open_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")]
    )
    if file_path:
        image_path.set(file_path)

        img = Image.open(file_path)
        img = img.resize((300, 200), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        image_label.config(image=img_tk)
        image_label.image = img_tk

        plate_number = recognize_plate(file_path)
        if plate_number:
            plate_number_var.set(f"Recognized Plate Number: {plate_number}")
            insert_plate_number(plate_number)
        else:
            plate_number_var.set("No plate number recognized.")

def show_saved_data():
    plate_numbers = retrieve_plate_numbers()
    if plate_numbers:
        result_text = "\n".join(plate_numbers)
        messagebox.showinfo("Saved Plate Numbers", result_text)
    else:
        messagebox.showinfo("Saved Plate Numbers", "No plate numbers found.")

def check_user_plate():
    user_plate = user_plate_entry.get()
    if user_plate:
        if check_plate_exists(user_plate):
            messagebox.showinfo("Access Granted", f"Plate number '{user_plate}' found. Access granted.")
        else:
            messagebox.showwarning("Access Denied", f"Plate number '{user_plate}' not found. Access denied.")
    else:
        messagebox.showwarning("Input Error", "Please enter a plate number.")


root = tk.Tk()
root.title("Car Number Plate Recognition")

image_path = tk.StringVar()
plate_number_var = tk.StringVar()

tk.Label(root, text="Select an Image:").pack(pady=10)

open_button = tk.Button(root, text="Open Image", command=open_image)
open_button.pack(pady=5)

image_label = tk.Label(root)
image_label.pack(pady=10)

tk.Label(root, textvariable=plate_number_var).pack(pady=10)

show_data_button = tk.Button(root, text="Show Saved Data", command=show_saved_data)
show_data_button.pack(pady=5)

tk.Label(root, text="Check Plate Number:").pack(pady=10)

user_plate_entry = tk.Entry(root)
user_plate_entry.pack(pady=5)

check_button = tk.Button(root, text="Check Plate Number", command=check_user_plate)
check_button.pack(pady=5)

root.mainloop()
