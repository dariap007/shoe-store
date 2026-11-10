import random
import string
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from app import database
from app.config import *


class AddProductWindow(tk.Tk):
    def __init__(self, user_data, perform_back, product_ids):
        super().__init__()

        self.user_data = user_data
        self.perform_back = perform_back
        self.product_ids = product_ids

        self.geometry("600x450")
        self.title("ООО «Обувь»")
        self.configure(bg=COLOR_MAIN_BG)

        self.create_header()
        self.create_form()
        self.create_bottom()

    def create_header(self):
        header = tk.Frame(self, bg=COLOR_ADDITIONAL_BG)
        header.pack(fill="x")

        # кнопка назад
        tk.Button(
            header,
            text="Назад",
            bg=COLOR_ACCENT,
            activebackground=COLOR_ACCENT,
            command=self.back_to_main
        ).pack(side="left", padx=10, pady=5)

        # заголовок окна
        tk.Label(
            header,
            text="Добавление товара",
            bg=COLOR_ADDITIONAL_BG,
            font=FONT_TITLE
        ).pack(side="left", padx=150)


    def create_form(self):
        """форма добавления товара"""
        form = tk.Frame(self, bg=COLOR_MAIN_BG)
        form.pack(fill="both", expand=True, padx=10, pady=10)


        top_form = tk.Frame(form, bg=COLOR_MAIN_BG)
        top_form.grid(row=0, column=0, sticky="nw")

        # добавление фото
        left_frame = tk.Frame(top_form, bg=COLOR_MAIN_BG)
        left_frame.grid(row=0, column=0, rowspan=2, sticky="nw", padx=(0, 20), pady=(0, 10))

        self.photo_label = tk.Label(
            left_frame,
            bg="white",
            width=150,
            height=150,
            relief="solid"
        )
        self.photo_label.pack(pady=(15, 0), padx=(15, 0))

        self.default_image_path = DEFAULT_PRODUCT_IMAGE
        self.load_image(self.default_image_path)
        self.photo_path = None

        tk.Button(
            left_frame,
            text="Добавить фото",
            bg=COLOR_ACCENT,
            activebackground=COLOR_ACCENT,
            command=self.choose_photo
        ).pack(pady=10)


        # основные поля ввода
        right_top = tk.Frame(top_form, bg=COLOR_MAIN_BG)
        right_top.grid(row=0, column=1, sticky="nw")

        # переменные
        self.name_var = tk.StringVar()
        self.supplier_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.manufacturer_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.unit_var = tk.StringVar()
        self.discount_var = tk.StringVar()
        self.stock_var = tk.StringVar()
        self.description_var = tk.StringVar()

        tk.Label(
            right_top,
            text="Наименование товара:",
            bg=COLOR_MAIN_BG,
            font=FONT_PRIMARY
        ).grid(row=0, column=0, sticky="w", pady=15)
        tk.Entry(
            right_top,
            textvariable=self.name_var,
            width=30
        ).grid(row=0, column=1, sticky="w", pady=2, padx=(5, 0))

        tk.Label(
            right_top,
            text="Категория товара: ",
            bg = COLOR_MAIN_BG,
            font=FONT_CARD_BODY
        ).grid(row=1, column=0, sticky="w", pady=5)
        ttk.Combobox(right_top, 
                     values=['Женская обувь', 'Мужская обувь'], 
                     textvariable=self.category_var, 
                     state='readonly'
        ).grid(row=1, column=1, sticky="w", pady=2, padx=(5, 0))

        tk.Label(
            right_top,
            text="Описание:",
            bg=COLOR_MAIN_BG,
            font=FONT_PRIMARY
        ).grid(row=2, column=0, sticky="w", pady=5)
        tk.Entry(
            right_top,
            textvariable=self.description_var,
            width=30
        ).grid(row=2, column=1, sticky="w", pady=2, padx=(5, 0))

        tk.Label(
            right_top,
            text="Производитель: ",
            bg = COLOR_MAIN_BG,
            font=FONT_CARD_BODY
        ).grid(row=3, column=0, sticky="w", pady=5)
        ttk.Combobox(right_top, 
                     values=['Kari', 'Обувь для вас'], 
                     textvariable=self.supplier_var, 
                     state='readonly'
        ).grid(row=3, column=1, sticky="w", pady=2, padx=(5, 0))

        tk.Label(
            right_top,
            text="Поставщик:",
            bg=COLOR_MAIN_BG,
            font=FONT_PRIMARY
        ).grid(row=4, column=0, sticky="w", pady=5)
        tk.Entry(
            right_top,
            textvariable=self.manufacturer_var,
            width=30
        ).grid(row=4, column=1, sticky="w", pady=2, padx=(5, 0))

        # выравнивание колонок
        right_top.grid_columnconfigure(0, weight=0)
        right_top.grid_columnconfigure(1, weight=1)


        bottom_form = tk.Frame(form, bg=COLOR_MAIN_BG)
        bottom_form.grid(row=1, column=0, sticky="nw", pady=(20, 0))
        
        left_bottom = tk.Frame(bottom_form, bg=COLOR_MAIN_BG)
        left_bottom.grid(row=0, column=0, sticky="nw", padx=20)

        tk.Label(
            left_bottom,
            text="Цена:",
            bg=COLOR_MAIN_BG,
            font=FONT_PRIMARY
        ).grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(
            left_bottom,
            textvariable=self.price_var,
            width=15
        ).grid(row=0, column=1, sticky="w", pady=5, padx=(5, 0))

        tk.Label(
            left_bottom,
            text="Единица измерения:",
            bg=COLOR_MAIN_BG,
            font=FONT_PRIMARY
        ).grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(
            left_bottom,
            textvariable=self.unit_var,
            width=15
        ).grid(row=1, column=1, sticky="w", pady=5, padx=(5, 0))


        right_bottom = tk.Frame(bottom_form, bg=COLOR_MAIN_BG)
        right_bottom.grid(row=0, column=1, sticky="nw")
        
        tk.Label(
            right_bottom,
            text="Действующая скидка (%):",
            bg=COLOR_MAIN_BG,
            font=FONT_PRIMARY
        ).grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(
            right_bottom,
            textvariable=self.discount_var,
            width=10
        ).grid(row=0, column=1, sticky="w", pady=5, padx=(5, 0))

        tk.Label(
            right_bottom,
            text="Количество на складе:",
            bg=COLOR_MAIN_BG,
            font=FONT_PRIMARY
        ).grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(
            right_bottom,
            textvariable=self.stock_var,
            width=10
        ).grid(row=1, column=1, sticky="w", pady=5, padx=(5, 0))

    
    def choose_photo(self):
        """выбор файла с фото товара"""
        file_path = filedialog.askopenfilename(
            title="Выберите фото товара",
            filetypes=[("Изображения", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if file_path:
            self.photo_path = file_path
            self.load_image(file_path)


    def load_image(self, path):
        """загрузка изображения"""
        try:
            img = Image.open(path)
            img = img.resize((150, 150))
            self.photo_tk = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.photo_tk, text="")
        except Exception as e:
            print("Ошибка загрузки изображения:", e)


    def create_bottom(self):
        bottom = tk.Frame(self, bg=COLOR_MAIN_BG)
        bottom.pack(fill="x", side='bottom')

        # кнопка сохранить
        tk.Button(
            bottom,
            text="Сохранить",
            bg=COLOR_ACCENT,
            command=self.save_product
        ).pack(side="right", padx=15, pady=15)


    def save_product(self):
        """проверка корректности введенных данных и сохранение"""
        name = self.name_var.get().strip()
        supplier = self.supplier_var.get().strip()
        category = self.category_var.get().strip()
        manufacturer = self.manufacturer_var.get().strip()
        price = self.price_var.get().strip()
        unit = self.unit_var.get().strip()
        discount = self.discount_var.get().strip()
        stock_quantity = self.stock_var.get().strip()
        description = self.description_var.get().strip()

        # генерация артикула товара
        letters = string.ascii_letters.upper() + string.digits
        while True:
            id_product = "".join([random.choice(letters) for _ in range(6)])
            if id_product not in self.product_ids:
                break

        # проверяем корректность введенных данных
        if not self.validate_form(name, unit, price, supplier, manufacturer, category, discount, stock_quantity, description):
            return

        # сохраняем заказ в бд
        ok = database.add_product(id_product, name, unit, price, supplier, manufacturer, category, discount, stock_quantity, description)

        # если все корректно
        if ok:
            messagebox.showinfo("Успех", "Товар успешно сохранён!")
            self.back_to_main()


    def validate_form(self, name, unit, price, supplier, manufacturer, category, discount, stock_quantity, description):
        """проверка введенных данных для записи в бд"""

        if supplier not in ['Kari', 'Обувь для вас']:
            messagebox.showerror("Ошибка ввода", "Выберите производителя из списка.")
            return False
        
        if category not in ['Женская обувь', 'Мужская обувь']:
            messagebox.showerror("Ошибка ввода", "Выберите категорию из списка.")
            return False

        if not name or not unit or not price or not supplier or not manufacturer or not discount or not stock_quantity or not description:
            messagebox.showerror("Ошибка ввода", "Заполните все поля.")
            return False
        
        return True

    
    def back_to_main(self):
        """возвращение на главное окно"""
        self.destroy()
        self.perform_back(self.user_data)