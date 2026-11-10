import psycopg2
from tkinter import messagebox
from app.config import DB_CONFIG



def check_user(login, password):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM users 
            WHERE login = %s AND password = %s;
        """, (login, password))

        user = cursor.fetchone()
        
        conn.close()
        
        return {
            "id ": user[0],
            "role": user[1],
            "full_name": user[2],
            "login": user[3],
            "password": user[4]
        }
    
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка подключения к базе:\n{e}")


def get_full_name_by_id(user_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT full_name FROM users WHERE id_user = %s",
            (user_id,)
        )

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result[0]
        else:
            return None

    except Exception as e:
        print("Ошибка при запросе:", e)
        return None


def get_all_products():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM products;
        """)

        result = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        keys = [
        "id_product", "name", "unit", "price", "supplier", "manufacturer",
        "category", "discount", "stock_quantity", "description", "photo"
        ]

        return [dict(zip(keys, row)) for row in result]
    
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка подключения к базе:\n{e}")

    
def get_orders():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM orders;
        """)

        result = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        keys = ["id_order", "order_date", "delivery_date", "id_pickup_point", "id_client", "pickup_code", "status"]

        return [dict(zip(keys, row)) for row in result]
    
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка подключения к базе:\n{e}")


def get_order_items():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM order_items;
        """)

        result = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        keys = ["id_order", "id_product", "quantity"]

        return [dict(zip(keys, row)) for row in result]
    
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка подключения к базе:\n{e}")


def get_pickup_points():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM pickup_points;
        """)

        result = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {id: address for id, address in result}
    
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка подключения к базе:\n{e}")


def add_product(id_product, name, unit, price, supplier, manufacturer, category, discount, stock_quantity, description):
    """запись нового товара в бд"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO products (id_product, name, unit, price, supplier, manufacturer, category, discount, stock_quantity, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (id_product, name, unit, price, supplier, manufacturer, category, discount, stock_quantity, description))

        conn.commit()

        conn.close()

        return True
    
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка подключения к базе:\n{e}")
        return False
    

def update_product(id_product, name, unit, price, supplier, manufacturer, category, discount, stock_quantity, description):
    """изменение заказа в бд"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)

        cursor = conn.cursor()

        cursor.execute("""
            UPDATE products
            SET name = %s,
                supplier = %s,
                category = %s,
                manufacturer = %s,
                price = %s,
                unit = %s,
                discount = %s,
                stock_quantity = %s,
                description = %s
            WHERE id_product = %s;
        """, (name, supplier, category, manufacturer, price, unit, discount, stock_quantity, description, id_product))

        conn.commit()

        conn.close()

        return True
    
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка подключения к базе:\n{e}")
        return False


def delete_product(product_id):
    """удаление товара из бд"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # проверяем есть ли товар в заказах
        cursor.execute("""
            SELECT COUNT(*) FROM order_items 
            WHERE id_product = %s
        """, (product_id,))
        
        order_count = cursor.fetchone()[0]
        
        if order_count > 0:
            conn.close()
            return False
        
        # удаляем товар
        cursor.execute("DELETE FROM products WHERE id_product = %s", (product_id,))
        conn.commit()
        
        # проверяем был ли удален товар
        deleted_rows = cursor.rowcount
        
        conn.close()
        
        return deleted_rows > 0
        
    except Exception as e:
        print(f"Ошибка при удалении товара: {e}")
        return False
    

def delete_order(id_order):
    """удаление заказ из бд"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # удаляем заказ
        cursor.execute("DELETE FROM orders WHERE id_order = %s", (id_order,))
        conn.commit()
        
        # проверяем был ли удален заказ
        deleted_rows = cursor.rowcount
        
        conn.close()
        
        return deleted_rows > 0
        
    except Exception as e:
        print(f"Ошибка при удалении товара: {e}")
        return False


def add_order(order_date, delivery_date, address, full_name, status):
    """запись нового заказа в бд"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)

        cursor = conn.cursor()

        # находим пункт выдачи по адресу 
        cursor.execute(
            "SELECT id_pickup_point FROM pickup_points WHERE address = %s;",
            (address,)
        )
        point = cursor.fetchone()

        if not point:
            cursor.execute(
            "INSERT INTO pickup_points (address)"
            "VALUES (%s) RETURNING id_pickup_point;",
            (address,)
            )
            point = cursor.fetchone()
        
        id_pickup_point = point[0]

        
        # находим айди клиента по ФИО
        cursor.execute(
            "SELECT id_user FROM users WHERE full_name = %s;",
            (full_name,)
        )
        user = cursor.fetchone()

        if not user:
            messagebox.showerror("Ошибка", f"Такого пользователя не существует!")
            return
        
        id_user = user[0]

        
        cursor.execute("""
            INSERT INTO orders (order_date, delivery_date, id_pickup_point, id_client, status)
            VALUES (%s, %s, %s, %s, %s);
        """, (order_date, delivery_date, id_pickup_point, id_user, status))

        conn.commit()

        conn.close()

        return True
    
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка подключения к базе:\n{e}")
        return False
    
def update_order(order_date, delivery_date, address, status, id_order, full_name):
    """изменение заказа в бд"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)

        cursor = conn.cursor()

        # ищем пункт выдачи по адресу
        cursor.execute(
            "SELECT id_pickup_point FROM pickup_points WHERE address = %s;",
            (address,)
        )
        point = cursor.fetchone()

        if not point:
            cursor.execute(
            "INSERT INTO pickup_points (address)"
            "VALUES (%s) RETURNING id_pickup_point;",
            (address,)
            )
            point = cursor.fetchone()
        
        id_pickup_point = point[0]


        # находим айди клиента по ФИО
        cursor.execute(
            "SELECT id_user FROM users WHERE full_name = %s;",
            (full_name,)
        )
        user = cursor.fetchone()

        if not user:
            messagebox.showerror("Ошибка", f"Такого пользователя не существует!")
            return
        
        id_user = user[0]
        

        cursor.execute("""
            UPDATE orders
            SET order_date = %s,
                delivery_date = %s,
                id_pickup_point = %s,
                status = %s,
                id_client = %s
            WHERE id_order = %s;
        """, (order_date, delivery_date, id_pickup_point, status, id_user, id_order))

        conn.commit()

        conn.close()

        return True
    
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка подключения к базе:\n{e}")
        return False