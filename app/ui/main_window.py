import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from app import database
from app.config import *
from .add_product_window import AddProductWindow
from .edit_product_window import EditProductWindow
from .order_windows import OrdersListWindow

class MainWindow(tk.Tk):
    def __init__(self, user_data):
        super().__init__()

        self.user_data = user_data
        self.logged_out = False

        self.title("Магазин обуви — каталог")
        self.geometry("850x600")
        self.configure(bg=COLOR_MAIN_BG)

        self.create_header()
        self.create_products_area()


    def create_header(self):
        """инициализация шапки приложения"""
        header = tk.Frame(self, bg=COLOR_ADDITIONAL_BG)
        header.pack(fill="x")

        # заголовок
        title_label = tk.Label(
            header, 
            text = "Каталог товаров",
            bg = COLOR_ADDITIONAL_BG, 
            font = FONT_TITLE
        )
        title_label.pack(side="left", padx=20)

        # кнопка выхода
        tk.Button(header, text="Выход", command=self.logout, bg=COLOR_ACCENT, activebackground=COLOR_ACCENT).pack(side='right', padx=10, pady=5)

        # фио пользователя
        fio_label = tk.Label(
            header, 
            text = self.user_data['full_name'],
            bg = COLOR_ADDITIONAL_BG, 
            font = FONT_PRIMARY_BOLD
        )
        fio_label.pack(side="right", padx=10)


        filter_frame = tk.Frame(self, bg=COLOR_ADDITIONAL_BG)
        filter_frame.pack(fill="x")

        # стили для акцентного цвета
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass

        style.configure(
            "Accent.TCombobox",
            fieldbackground=COLOR_ACCENT,
            background=COLOR_ACCENT,
            foreground="black"
        )
        style.map(
            "Accent.TCombobox",
            fieldbackground=[("readonly", COLOR_ACCENT)],
            foreground=[("readonly", "black")],
            selectbackground=[("readonly", COLOR_ACCENT)],
            selectforeground=[("readonly", "black")]
        )

        style.configure(
            "Accent.TEntry",
            fieldbackground=COLOR_ACCENT,
            foreground="black"
        )

        # запрашиваем товары из бд
        self.products = database.get_all_products()

        # достаем id всех товаров
        self.product_ids = [p["id_product"] for p in self.products]
        
        # фильтрация по поставщику
        suppliers = list(set([product['supplier'] for product in self.products]))
        suppliers_list = ["Все поставщики"] + suppliers
        self.supplier_var = tk.StringVar(value="Все поставщики")
        supplier_cb = ttk.Combobox(
            filter_frame,
            values=suppliers_list,
            state="readonly",
            textvariable=self.supplier_var,
            width=25,
            style="Accent.TCombobox"
        )
        supplier_cb.pack(side="left", padx=5, pady=5)

        supplier_cb.bind("<<ComboboxSelected>>", self.filter_suppliers)

        
        # сортировка
        sort_list = ["По убыванию кол-ва", "По возрастанию кол-ва"]
        self.sort_var = tk.StringVar(value="Отсортировать")
        sort_cb = ttk.Combobox(
            filter_frame,
            values=sort_list,
            state="readonly",
            textvariable=self.sort_var,
            width=25,
            style="Accent.TCombobox"
        )
        sort_cb.pack(side="left", padx=5)

        sort_cb.bind("<<ComboboxSelected>>", self.sort_products)

        # поисковая строка
        tk.Label(filter_frame, text="Поиск:", bg=COLOR_ADDITIONAL_BG).pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5)

        self._search_after_id = None
        search_entry.bind("<KeyRelease>", self.on_search_key)
        
        
        # tk.Button(filter_frame, text="Заказы", command=self.open_orders_list_window, width=10, bg=COLOR_ACCENT).pack(side='left', padx=5)
        # tk.Button(filter_frame, text="Добавить товар", command=self.open_add_prod_window, width=20, bg=COLOR_ACCENT).pack(side='left', padx=5, pady=5)
        
        # в зависимости от роли показываем/не показываем пользователю блок фильтрации
        user_role = self.user_data.get("role")
        if user_role == "Администратор":
            # кнопка просмотра заказов
            tk.Button(filter_frame, text="Заказы", command=self.open_orders_list_window, width=10, bg=COLOR_ACCENT, activebackground=COLOR_ACCENT).pack(side='left', padx=5, pady=5)

            # кнопка добавления товара
            tk.Button(filter_frame, text="Добавить товар", command=self.open_add_prod_window, width=20, bg=COLOR_ACCENT, activebackground=COLOR_ACCENT).pack(side='left', padx=5)
        elif user_role == "Менеджер":
            # кнопка просмотра заказов
            tk.Button(filter_frame, text="Заказы", command=self.open_orders_list_window, width=15, bg=COLOR_ACCENT, activebackground=COLOR_ACCENT).pack(side='right', padx=5, pady=5)
        else:
            # скрываем весь фрейм
            filter_frame.pack_forget()


    def on_search_key(self, event):
        if self._search_after_id:
            self.after_cancel(self._search_after_id)
            
        self._search_after_id = self.after(200, self.perform_search)


    def perform_search(self):
        """реализация поиска (через общий фильтр)"""
        self.apply_filters()
        self._search_after_id = None

    def apply_filters(self):
        """поиск + фильтр + сортировка"""
        # очищаем карточки
        for w in self.content_frame.winfo_children():
            w.destroy()

        products_list = self.products

        # 1. Поиск
        query = self.search_var.get().strip().lower()
        if query:
            words = query.split()  # разложить запрос на отдельные слова

            def matches(product):
                text = (
                    f"{product['name']} "
                    f"{product['category']} "
                    f"{product['manufacturer']} "
                    f"{product['supplier']}"
                ).lower()

                # каждое слово должно встречаться в любом атрибуте
                return all(word in text for word in words)

            products_list = [p for p in products_list if matches(p)]


        # 2. Фильтр по поставщику
        supplier = self.supplier_var.get()
        if supplier != "Все поставщики":
            products_list = [
                p for p in products_list if p["supplier"] == supplier
            ]

        # 3. Сортировка
        sorting_method = self.sort_var.get()
        if sorting_method == "По убыванию кол-ва":
            products_list = sorted(
                products_list,
                key=lambda p: p["stock_quantity"],
                reverse=True
            )
        elif sorting_method == "По возрастанию кол-ва":
            products_list = sorted(
                products_list,
                key=lambda p: p["stock_quantity"]
            )

        # выводим товары
        for product in products_list:
            self.create_product_card(product)

    def filter_suppliers(self, event):
        self.apply_filters()

    def sort_products(self, event):
        self.apply_filters()

    def refresh_products(self):
        # обновляем товары из БД и применяем текущие фильтры
        self.products = database.get_all_products()
        self.apply_filters()

    def create_products_area(self):
        container = tk.Frame(self, bg=COLOR_MAIN_BG)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # фрейм для полосы прокрутки
        canvas = tk.Canvas(container, bg=COLOR_MAIN_BG)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.content_frame = tk.Frame(canvas, bg=COLOR_MAIN_BG)

        self.content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # корректировка ширины окна
        def update_content_width(event):
            canvas.itemconfig(canvas.find_all()[0], width=event.width)
    
        canvas.bind("<Configure>", update_content_width)

        # для каждого продукта формируем карточку товара
        for product in self.products:
            self.create_product_card(product)

    def create_product_card(self, product):
        # фрейм карточки товара
        card = tk.Frame(self.content_frame, bd=1, relief="solid", bg="white")
        card.pack(fill="x", padx=5, pady=5)

        # делим фрейм на три колонки
        card.grid_columnconfigure(0, weight=0)
        card.grid_columnconfigure(1, weight=1)
        card.grid_columnconfigure(2, weight=0)


        # фото товара
        image_path = product["photo"]
        try:
            img = Image.open(resolve_product_image(image_path))
        except Exception:
            img = Image.open(DEFAULT_PRODUCT_IMAGE)

        img = img.resize((120, 120))
        photo = ImageTk.PhotoImage(img)

        img_label = tk.Label(card, image=photo, bg="white")
        img_label.image = photo
        img_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10)

        if self.user_data["role"] == 'Администратор':
            img_label.bind("<Button-1>", lambda e: self.open_edit_prod_window(product))


        # заголовок товара
        name_label = tk.Label(
            card,
            text=product['category'] +" | " + product["name"],
            font=FONT_CARD_TITLE,
            bg=COLOR_MAIN_BG,
        )
        name_label.grid(row=0, column=1, sticky="w")


        # описание товара
        info_frame = tk.Frame(card, bg="white")
        info_frame.grid(row=1, column=1, sticky="w")
        info_frame.grid_columnconfigure(0, weight=1)

        info_text = tk.Text(
            info_frame,
            height=6,
            bg="white",
            border=0,
            font=FONT_CARD_BODY
        )
        info_text.pack()

        base_info = (
            f"Поставщик: {product['supplier']}\n"
            f"Производитель: {product['manufacturer']}\n"
            f"Описание: {product['description'] or 'Нет описания'}\n"
        )
        info_text.insert("end", base_info)

        # строка с ценой
        info_text.insert("end", "Цена: ")
        price_start = info_text.index("end-1c")

        # расчет скидки
        price = float(product["price"])
        discount = float(product["discount"])
        final_price = round(price * (100 - discount) / 100, 2)

        if discount > 0:
            # старая цена
            old_price_text = f"{price:.2f} ₽ "
            info_text.insert("end", old_price_text)

            old_price_end = info_text.index("end-1c")
            info_text.tag_add("old_price", price_start, old_price_end)
            info_text.tag_config(
                "old_price",
                foreground="red",
                font=(FONT_CARD_BODY[0], FONT_CARD_BODY[1], "overstrike")
            )

            # новая цена
            new_price_text = f"{final_price:.2f} ₽"
            info_text.insert("end", new_price_text)

            new_price_start = old_price_end
            new_price_end = info_text.index("end-1c")
            info_text.tag_add("new_price", new_price_start, new_price_end)
            info_text.tag_config("new_price", foreground="black", font=FONT_CARD_BODY)
        else:
            price_text = f"{price:.2f} ₽"
            info_text.insert("end", price_text)

        # перенос строки после цены
        info_text.insert("end", "\n")

        # единица измерения уже отдельной строкой
        info_text.insert("end", f"Единица измерения: {product['unit']}\n")

        info_text.configure(state="disabled")

        # количество на складе
        quantity_frame = tk.Frame(card, bg="white")
        quantity_frame.grid(row=2, column=1, sticky="w", padx=(0, 20), pady=(0, 5))
        
        quantity_label = tk.Label(
            quantity_frame,
            text=f"Количество на складе: {product['stock_quantity']} {product['unit']}",
            font=FONT_CARD_BODY,
            bg="#87CEFA" if product["stock_quantity"] == 0 else "white",
            padx=5,
            pady=2
        )
        quantity_label.pack()

        # меняем цвет карточки в зависимости от скидки и количества
        if product["stock_quantity"] == 0:
            quantity_label.configure(bg="#87CEFA")
        elif discount > 15:
            card.configure(bg=COLOR_DISCOUNT_BG)
            for child in card.winfo_children():
                try:
                    child.configure(bg=COLOR_DISCOUNT_BG)
                except:
                    pass
            
            quantity_frame.configure(bg=COLOR_DISCOUNT_BG)
            quantity_label.configure(bg=COLOR_DISCOUNT_BG)


        # справа указываем действующую скидку
        discount_frame = tk.Frame(card, bg="white")
        discount_frame.grid(row=0, column=2, padx=20)

        tk.Label(
            discount_frame,
            text=f"Скидка: {discount:.0f}%",
            font=FONT_CARD_BODY,
            bg="white"
        ).pack()


        # меняем цвет всех элементов карточки товара
        bg_color = card.cget("bg")

        discount_frame.configure(bg=bg_color)
        for pf_child in discount_frame.winfo_children():
            try:
                pf_child.configure(bg=bg_color)
            except:
                pass

        info_frame.configure(bg=bg_color)
        for pf_child in info_frame.winfo_children():
            try:
                pf_child.configure(bg=bg_color)
            except:
                pass


    def open_add_prod_window(self):
        """открыть окно добавления товара"""
        self.destroy()

        def back_to_main(user_data):
            MainWindow(user_data).mainloop()

        AddProductWindow(self.user_data, back_to_main, self.product_ids).mainloop()


    def open_edit_prod_window(self, product):
        """открыть окно редактирования товара"""
        self.destroy()

        def back_to_main(user_data):
            MainWindow(user_data).mainloop()

        EditProductWindow(self.user_data, back_to_main, product).mainloop()


    def open_orders_list_window(self):
        """открыть окно списка заказов"""
        self.destroy()

        def back_to_main(user_data):
            MainWindow(user_data).mainloop()

        OrdersListWindow(self.user_data, back_to_main).mainloop()


    def logout(self):
        """выход"""
        self.logged_out = True
        self.destroy()