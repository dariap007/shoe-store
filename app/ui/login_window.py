import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
from app import database
from app.config import *
from PIL import Image, ImageTk

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry("250x400")
        self.title("Авторизация")
        
        icon = PhotoImage(file=str(ICON_FILE))
        self.iconphoto(True, icon)
        
        style = ttk.Style(self)
        style.configure("TLabel", font=("Times New Roman", 14))
        
        title_label = tk.Label( 
            text = "ООО «Обувь»",
            bg = COLOR_ADDITIONAL_BG, 
            font = FONT_TITLE
        )
        title_label.pack(pady=10)

        image = Image.open(LOGO_FILE)
        image = image.resize((100, 100), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        label = tk.Label(self, image=photo, bg="white")
        label.image = photo
        label.pack(pady=10)

        ttk.Label(text="Логин:", padding=10).pack()
        self.login_entry = ttk.Entry()
        self.login_entry.pack()

        ttk.Label(text="Пароль:", padding=10).pack()
        self.password_entry = ttk.Entry()
        self.password_entry.pack()

        tk.Button(text="Войти", command=self.login,  bg=COLOR_ACCENT, activebackground=COLOR_ACCENT).pack(pady=10)
        tk.Button(text="Войти как гость", command=self.login_as_guest, bg=COLOR_ACCENT, activebackground=COLOR_ACCENT).pack(pady=10)

    def login(self):
        """проверка логина и пароля"""
        login = self.login_entry.get()
        password = self.password_entry.get()

        if not login or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return

        user_data = database.check_user(login, password)
        if user_data:
            self.open_main_window(user_data)
        else:
            messagebox.showerror(
                "Ошибка",
                "Неверный логин или пароль. Проверьте данные и попробуйте снова.",
            )

    def login_as_guest(self):
        guest_data = {"full_name": "Гость", "role": "Гость"}
        self.open_main_window(guest_data)

    def open_main_window(self, user_data):
        self.user_data = user_data
        self.destroy()
