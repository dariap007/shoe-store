import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from app import database
from app.config import *


class OrdersListWindow(tk.Tk):
    def __init__(self, user_data, perform_back):
        super().__init__()

        self.user_data = user_data
        self.perform_back = perform_back

        self.orders = database.get_orders()
        self.order_items = database.get_order_items()
        self.pickup_points = database.get_pickup_points()

        self.geometry("850x600")
        self.title("ООО «Обувь»")
        self.configure(bg=COLOR_MAIN_BG)

        self.create_header()
        self.create_orders_area()

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
            text="Заказы",
            bg=COLOR_ADDITIONAL_BG,
            font=FONT_TITLE
        ).pack(side="left", padx=5)

        # фио пользователя
        tk.Label(
            header,
            text=f"{self.user_data["full_name"]}",
            bg=COLOR_ADDITIONAL_BG,
            font=FONT_TITLE
        ).pack(side="right", padx=10)

        if self.user_data["role"] == 'Администратор':
            # кнопка добавления заказа
            tk.Button(
                header,
                text="Добавить заказ",
                bg=COLOR_ACCENT,
                activebackground=COLOR_ACCENT,
                command=self.open_add_order_window
            ).pack(side="right", padx=10, pady=5)


    def create_orders_area(self):
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

        # для каждого заказа формируем карточку заказа
        for order in self.orders:
            self.create_order_card(order)


    def create_order_card(self, order):
        """создание карточки заказа"""
        # фрейм карточки заказа
        card = tk.Frame(self.content_frame, bd=1, relief="solid", bg="white")
        card.pack(fill="x", padx=5, pady=5)

        card.grid_columnconfigure(0, weight=1)  # растягивается
        card.grid_columnconfigure(1, weight=0)  # фиксированая

        info_frame = tk.Frame(card, bg="white")
        info_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        # артикул заказа
        id_label = tk.Label(
            info_frame,
            text=f"Заказ №{order['id_order']}",
            font=FONT_CARD_TITLE,
            bg="white",
            anchor="w"
        )
        id_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        # кнопка редактирования заказа
        if self.user_data["role"] == 'Администратор':
            id_label.bind("<Button-1>", lambda e: self.open_edit_order_window(order))

        # информация о заказе
        status_label = tk.Label(
            info_frame,
            text=f"Статус: {order['status']}",
            font=FONT_CARD_BODY,
            bg="white",
            anchor="w"
        )
        status_label.grid(row=1, column=0, sticky="w", pady=2)

        status_label = tk.Label(
            info_frame,
            text=f"Пункт выдачи: {self.pickup_points[order['id_pickup_point']]}",
            font=FONT_CARD_BODY,
            bg="white",
            anchor="w"
        )
        status_label.grid(row=2, column=0, sticky="w", pady=2)

        status_label = tk.Label(
            info_frame,
            text=f"Дата заказа: {str(order['order_date']).split()[0]}",
            font=FONT_CARD_BODY,
            bg="white",
            anchor="w"
        )
        status_label.grid(row=3, column=0, sticky="w", pady=2)

        # дата доставки
        delivery_frame = tk.Frame(card, bg="white")
        delivery_frame.grid(row=0, column=1, sticky="w", padx=10, pady=10)

        delivery_date = str(order['delivery_date']).split()[0]
        delivery_date_label = tk.Label(
            delivery_frame,
            text=f"Дата доставки:\n{delivery_date}",
            font=FONT_CARD_BODY,
            bg="white",
            anchor="e"
        )
        delivery_date_label.pack()


    # def refresh_products(self):
    #     for w in self.content_frame.winfo_children():
    #         w.destroy()

    #     orders = database.get_orders()
    #     for order in orders:
    #         self.create_order_card(order)


    def open_add_order_window(self):
        """открыть окно добавления заказов"""
        self.destroy()

        def back_to_orders(user_data):
            OrdersListWindow(user_data, self.perform_back).mainloop()

        AddOrderWindow(self.user_data, back_to_orders).mainloop()


    def open_edit_order_window(self, order):
        """открыть окно добавления заказов"""
        self.destroy()

        def back_to_orders(user_data):
            OrdersListWindow(user_data, self.perform_back).mainloop()

        EditOrderWindow(self.user_data, back_to_orders, order, self.pickup_points).mainloop()

    
    def back_to_main(self):
        """возвращение на главное окно"""
        self.destroy()
        self.perform_back(self.user_data)


class AddOrderWindow(tk.Tk):
    def __init__(self, user_data, perform_back):
        super().__init__()

        self.user_data = user_data
        self.perform_back = perform_back

        self.geometry("600x400")
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
            command=self.back_to_orders
        ).pack(side="left", padx=10, pady=5)

        # заголовок окна
        tk.Label(
            header,
            text="Добавление заказа",
            bg=COLOR_ADDITIONAL_BG,
            font=FONT_TITLE
        ).pack(side="left", padx=150)


    def create_form(self):
        form = tk.Frame(self, bg=COLOR_MAIN_BG)
        form.pack(fill="x")

        tk.Label(
            form,
            text="Статус заказа: ",
            bg = COLOR_MAIN_BG,
            font=FONT_CARD_BODY
        ).grid(row=1, column=0, padx=30, pady=15)
        self.status = tk.StringVar()
        ttk.Combobox(form, 
                     values=['Новый', 'Завершен'], 
                     textvariable=self.status, 
                     state='readonly'
        ).grid(row=1, column=1)

        tk.Label(
            form,
            text="Адрес пункта выдачи: ",
            bg = COLOR_MAIN_BG,
            font=FONT_CARD_BODY
        ).grid(row=2, column=0, padx=30, pady=15)
        self.address = tk.StringVar()
        ttk.Entry(form, textvariable=self.address, width=45).grid(row=2, column=1)

        tk.Label(
            form,
            text="Дата заказа (ГГГГ-ММ-ДД): ",
            bg = COLOR_MAIN_BG,
            font=FONT_CARD_BODY
        ).grid(row=3, column=0, padx=30, pady=15)
        self.order_date = tk.StringVar()
        ttk.Entry(form, textvariable=self.order_date, width=45).grid(row=3, column=1)

        tk.Label(
            form,
            text="Дата доставки (ГГГГ-ММ-ДД): ",
            bg = COLOR_MAIN_BG,
            font=FONT_CARD_BODY
        ).grid(row=4, column=0, padx=30, pady=15)
        self.delivery_date = tk.StringVar()
        ttk.Entry(form, textvariable=self.delivery_date, width=45).grid(row=4, column=1)

        tk.Label(
            form,
            text="ФИО заказчика: ",
            bg = COLOR_MAIN_BG,
            font=FONT_CARD_BODY
        ).grid(row=5, column=0, padx=30, pady=15)
        self.full_name = tk.StringVar()
        ttk.Entry(form, textvariable=self.full_name, width=45).grid(row=5, column=1)


    def create_bottom(self):
        bottom = tk.Frame(self, bg=COLOR_MAIN_BG)
        bottom.pack(fill="x", side='bottom')

        # кнопка сохранить
        tk.Button(
            bottom,
            text="Сохранить",
            bg=COLOR_ACCENT,
            activebackground=COLOR_ACCENT,
            command=self.save_order
        ).pack(side="right", padx=15, pady=15)


    def save_order(self):
        """проверка корректности введенных данных и сохранение"""
        status = self.status.get().strip()
        address = self.address.get().strip()
        order_date = self.order_date.get().strip()
        delivery_date = self.delivery_date.get().strip()
        full_name = self.full_name.get().strip()

        # проверяем корректность введенных данных
        if not validate_form(status, address, order_date, delivery_date, full_name):
            return

        # сохраняем заказ в бд
        ok = database.add_order(order_date, delivery_date, address, full_name, status)

        # если все корректно
        if ok:
            messagebox.showinfo("Успех", "Заказ успешно сохранён!")
            self.back_to_orders()


    # def validate_form(self, status, address, order_date, delivery_date, full_name):
    #     """проверка введенных данных для записи в бд"""

    #     # проверка статуса
    #     if status not in ["Новый", "Завершен"]:
    #         messagebox.showerror("Ошибка ввода", "Выберите статус заказа из списка.")
    #         return False

    #     # проверка адреса
    #     if not address:
    #         messagebox.showerror("Ошибка ввода", "Адрес пункта выдачи не может быть пустым.")
    #         return False
        
    #     # проверка ФИО
    #     if not full_name:
    #         messagebox.showerror("Ошибка ввода", "ФИО заказчика не может быть пустым.")
    #         return False

    #     # проверка дат
    #     try:
    #         d_order = datetime.strptime(order_date, "%Y-%m-%d")
    #     except ValueError:
    #         messagebox.showerror("Ошибка ввода", "Дата заказа должна быть в формате ГГГГ-ММ-ДД.")
    #         return False

    #     try:
    #         d_delivery = datetime.strptime(delivery_date, "%Y-%m-%d")
    #     except ValueError:
    #         messagebox.showerror("Ошибка ввода", "Дата доставки должна быть в формате ГГГГ-ММ-ДД.")
    #         return False

    #     if d_delivery < d_order:
    #         messagebox.showerror("Ошибка ввода", "Дата доставки не может быть раньше даты заказа.")
    #         return False
        
    #     return True


    def back_to_orders(self):
        """возвращение на главное окно"""
        self.destroy()
        self.perform_back(self.user_data)


class EditOrderWindow(tk.Tk):
    def __init__(self, user_data, perform_back, order, pickup_points):
        super().__init__()

        self.user_data = user_data
        self.perform_back = perform_back
        self.order = order
        self.pickup_points = pickup_points

        self.geometry("600x400")
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
            command=self.back_to_orders
        ).pack(side="left", padx=10, pady=5)

        # заголовок окна
        tk.Label(
            header,
            text="Редактирование заказа",
            bg=COLOR_ADDITIONAL_BG,
            font=FONT_TITLE
        ).pack(side="left", padx=140)


    def create_form(self):
        form = tk.Frame(self, bg=COLOR_MAIN_BG)
        form.pack(fill="x")

        tk.Label(
            form,
            text="Статус заказа: ",
            bg = COLOR_MAIN_BG,
            font=FONT_CARD_BODY
        ).grid(row=1, column=0, padx=30, pady=15)
        self.status = tk.StringVar()
        self.status.set(self.order["status"])
        ttk.Combobox(form, 
                     values=['Новый', 'Завершен'], 
                     textvariable=self.status, 
                     state='readonly'
        ).grid(row=1, column=1)

        tk.Label(
            form,
            text="Адрес пункта выдачи: ",
            bg = COLOR_MAIN_BG,
            font=FONT_CARD_BODY
        ).grid(row=2, column=0, padx=30, pady=15)
        self.address = tk.StringVar()
        self.address.set(self.pickup_points[self.order["id_pickup_point"]])
        ttk.Entry(form, textvariable=self.address, width=45).grid(row=2, column=1)

        tk.Label(
            form,
            text="Дата заказа (ГГГГ-ММ-ДД): ",
            bg = COLOR_MAIN_BG,
            font=FONT_CARD_BODY
        ).grid(row=3, column=0, padx=30, pady=15)
        self.order_date = tk.StringVar()
        self.order_date.set(str(self.order["order_date"]).split()[0])
        ttk.Entry(form, textvariable=self.order_date, width=45).grid(row=3, column=1)

        tk.Label(
            form,
            text="Дата доставки (ГГГГ-ММ-ДД): ",
            bg = COLOR_MAIN_BG,
            font=FONT_CARD_BODY
        ).grid(row=4, column=0, padx=30, pady=15)
        self.delivery_date = tk.StringVar()
        self.delivery_date.set(str(self.order["delivery_date"]).split()[0])
        ttk.Entry(form, textvariable=self.delivery_date, width=45).grid(row=4, column=1)

        tk.Label(
            form,
            text="ФИО заказчика: ",
            bg = COLOR_MAIN_BG,
            font=FONT_CARD_BODY
        ).grid(row=5, column=0, padx=30, pady=15)
        self.full_name = tk.StringVar(value=database.get_full_name_by_id(self.order["id_client"]))
        ttk.Entry(form, textvariable=self.full_name, width=45).grid(row=5, column=1)


    def create_bottom(self):
        bottom = tk.Frame(self, bg=COLOR_MAIN_BG)
        bottom.pack(fill="x", side='bottom')

        # кнопка сохранить
        tk.Button(
            bottom,
            text="Сохранить",
            bg=COLOR_ACCENT,
            activebackground=COLOR_ACCENT,
            command=self.edit_order
        ).pack(side="right", padx=15, pady=15)

        # кнопка удалить заказ
        tk.Button(
            bottom,
            text="Удалить заказ",
            bg=COLOR_ACCENT,
            activebackground=COLOR_ACCENT,
            command=self.delete_order
        ).pack(side="right", padx=15, pady=15)


    def edit_order(self):
        """проверка корректности введенных данных и обновление"""

        status = self.status.get().strip()
        address = self.address.get().strip()
        order_date = self.order_date.get().strip()
        delivery_date = self.delivery_date.get().strip()
        full_name = self.full_name.get().strip()

        # проверяем корректность введенных данных
        if not validate_form(status, address, order_date, delivery_date, full_name):
            return

        # сохраняем заказ в бд
        ok = database.update_order(order_date, delivery_date, address, status, self.order["id_order"], full_name)

        # если все корректно
        if ok:
            messagebox.showinfo("Успех", "Заказ успешно сохранён!")
            self.back_to_orders()


    def delete_order(self):
        """обработчик удаления товара"""
        order = self.order

        # окно подтверждения удаления
        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить заказ №{order['id_order']}?\n\n",
            icon="warning"
        )
        
        if confirm:
            success = database.delete_order(order['id_order'])
            
            if success:
                messagebox.showinfo(
                    "Успешно",
                    f"Заказ №{order['id_order']} успешно удален!"
                )
                
                # OrdersListWindow.refresh_products()
                self.back_to_orders()
            else:
                messagebox.showerror(
                    "Ошибка",
                    f"Не удалось удалить заказ №{order['id_order']}.\n"
                )


    def back_to_orders(self):
        """возвращение на главное окно"""
        self.destroy()
        self.perform_back(self.user_data)


def validate_form(status, address, order_date, delivery_date, full_name):
    """проверка введенных данных для записи в бд"""

    # проверка статуса
    if status not in ["Новый", "Завершен"]:
        messagebox.showerror("Ошибка ввода", "Выберите статус заказа из списка.")
        return False

    # проверка адреса
    if not address:
        messagebox.showerror("Ошибка ввода", "Адрес пункта выдачи не может быть пустым.")
        return False
    
    # проверка ФИО
    if not full_name:
        messagebox.showerror("Ошибка ввода", "ФИО заказчика не может быть пустым.")
        return False

    # проверка дат
    try:
        d_order = datetime.strptime(order_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Ошибка ввода", "Дата заказа должна быть в формате ГГГГ-ММ-ДД.")
        return False

    try:
        d_delivery = datetime.strptime(delivery_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Ошибка ввода", "Дата доставки должна быть в формате ГГГГ-ММ-ДД.")
        return False

    if d_delivery < d_order:
        messagebox.showerror("Ошибка ввода", "Дата доставки не может быть раньше даты заказа.")
        return False
    
    return True