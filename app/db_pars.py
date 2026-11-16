from datetime import date, datetime

import openpyxl
from sqlalchemy import create_engine, MetaData, URL, text, insert

from app.config import DB_CONFIG, IMPORT_DATA_DIR, PRODUCT_IMAGES_DIR, PROJECT_ROOT


# Создаём движок SQLAlchemy на основе DB_CONFIG
engine = create_engine(
    URL.create(
        "postgresql+psycopg2",
        username=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        database=DB_CONFIG["dbname"],
    ),
    echo=False,
)


def get_user_id_by_name(users, fio):
    """По ФИО найти id_user (для id_client в orders)."""
    for person in users:
        if person["full_name"] == fio:
            return person["id_user"]
    return None  # можно заменить на исключение, если нужно


def parse_date(value):
    """Приводим дату из Excel к date (Postgres сам приведёт к timestamp)."""
    if value is None or value == "":
        return None
    
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    s = str(value).strip()
    s_only_date = s.split()[0]
    for fmt in ("%y-%m-%d", "%m/%d/%y", "%d.%m.%y"):
        try:
            return datetime.strptime(s_only_date, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unknown date format: {value}")


def parse_articles(data: str):
    """
    Поле 'Артикул заказа' вида:
    'А112Т4, 2, F635R4, 2'
    -> (['А112Т4', 'F635R4'], [2, 2])
    """
    raw = [x.strip() for x in data.split(',')]
    articles = []
    quantities = []
    for i in range(0, len(raw), 2):
        articles.append(raw[i])
        quantities.append(int(raw[i + 1]))
    return articles, quantities


def run_import_from_excel():
    """
    Полный импорт данных из Excel-файлов в папке resources/import-data/:
      - user_import.xlsx              -> users
      - Tovar.xlsx                    -> products
      - Пункты выдачи_import.xlsx     -> pickup_points
      - Заказ_import.xlsx             -> orders, order_items

    Функция:
      1) очищает таблицы (TRUNCATE),
      2) читает файлы,
      3) вставляет данные в БД.
    """
    # Отражение схемы бд
    metadata = MetaData()
    metadata.reflect(bind=engine)

    Users = metadata.tables["users"]
    Products = metadata.tables["products"]
    PickupPoints = metadata.tables["pickup_points"]
    Orders = metadata.tables["orders"]
    OrderItems = metadata.tables["order_items"]

    # 1. Чистим таблицы (сначала дочерние)
    with engine.begin() as conn:
        conn.execute(text("""
            TRUNCATE TABLE order_items, orders, products, users, pickup_points
            RESTART IDENTITY CASCADE;
        """))

    # 2. Импорт пользователей из resources/import-data/user_import.xlsx
    user_imp_path = IMPORT_DATA_DIR / "user_import.xlsx"
    users_ws = openpyxl.load_workbook(user_imp_path).active
    user_rows = [
        {
            "role": str(row[0].value),
            "full_name": str(row[1].value),
            "login": str(row[2].value),
            "password": str(row[3].value),
        }
        for row in users_ws.iter_rows(min_row=2)
        if row[1].value is not None
    ]

    with engine.begin() as conn:
        conn.execute(insert(Users), user_rows)

    # 3. Импорт товаров из resources/import-data/Tovar.xlsx
    tovar_imp_path = IMPORT_DATA_DIR / "Tovar.xlsx"
    products_ws = openpyxl.load_workbook(tovar_imp_path).active
    product_rows = []

    for row in products_ws.iter_rows(min_row=2):
        if row[1].value is None:
            continue

        photo_name = str(row[10].value) if row[10].value is not None else None
        if photo_name:
            photo_path = str((PRODUCT_IMAGES_DIR / photo_name).relative_to(PROJECT_ROOT))
        else:
            photo_path = None

        product_rows.append(
            {
                "id_product": str(row[0].value),          # артикул (PRIMARY KEY в products)
                "name": str(row[1].value),
                "unit": str(row[2].value),
                "price": float(row[3].value),
                "supplier": str(row[4].value),
                "manufacturer": str(row[5].value),
                "category": str(row[6].value),
                "discount": float(row[7].value),
                "stock_quantity": int(row[8].value),
                "description": str(row[9].value),
                "photo": photo_path,
            }
        )

    with engine.begin() as conn:
        conn.execute(insert(Products), product_rows)

    # 4. Импорт пунктов выдачи из resources/import-data/Пункты_выдачи_import.xlsx
    pickup_imp_path = IMPORT_DATA_DIR / "Пункты_выдачи_import.xlsx"
    pickup_ws = openpyxl.load_workbook(pickup_imp_path).active
    pickup_rows = [
        {
            "address": str(row[0].value)
        }
        for row in pickup_ws.iter_rows(min_row=1)
        if row[0].value is not None
    ]

    with engine.begin() as conn:
        conn.execute(insert(PickupPoints), pickup_rows)

    # 5. Получаем список пользователей (id_user + ФИО), чтобы по ФИО найти id_client
    with engine.begin() as conn:
        result = conn.execute(text("SELECT id_user, full_name FROM users"))
        users_list = [
            {"id_user": row.id_user, "full_name": row.full_name}
            for row in result
        ]

    # 6. Импорт заказов и позиций заказа из resources/import-data/Заказ_import.xlsx
    order_imp_path = IMPORT_DATA_DIR / "Заказ_import.xlsx"
    orders_ws = openpyxl.load_workbook(order_imp_path).active

    orders_to_insert = []
    order_items_to_insert = []

    # структура строки:
    # 0: id_order
    # 1: строка 'артикул, кол-во, артикул, кол-во'
    # 2: дата заказа
    # 3: дата доставки
    # 4: id_pickup_point
    # 5: ФИО клиента
    # 6: код получения (pickup_code)
    # 7: статус ('Новый' / 'Завершен')
    for row in orders_ws.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue

        id_order = int(row[0])
        article_raw = str(row[1])
        order_date = parse_date(row[2])
        delivery_date = parse_date(row[3])
        id_pickup_point = int(row[4])
        full_name = str(row[5])
        id_client = get_user_id_by_name(users_list, full_name)
        pickup_code = int(row[6]) if row[6] is not None else None
        status = str(row[7]).strip()  # убираем пробелы, чтобы пройти CHECK ('Новый', 'Завершен')

        orders_to_insert.append({
            "id_order": id_order,
            "order_date": order_date,
            "delivery_date": delivery_date,
            "id_pickup_point": id_pickup_point,
            "id_client": id_client,
            "pickup_code": pickup_code,
            "status": status
        })

        # парсим строку с артикулами и количествами
        articles, quantities = parse_articles(article_raw)
        for art, qty in zip(articles, quantities):
            order_items_to_insert.append({
                "id_order": id_order,
                "id_product": art,   # артикул = id_product из products
                "quantity": qty
            })

    # 7. Вставляем заказы и позиции в БД
    with engine.begin() as conn:
        if orders_to_insert:
            conn.execute(insert(Orders), orders_to_insert)
        if order_items_to_insert:
            conn.execute(insert(OrderItems), order_items_to_insert)

    print("Импорт из xlsx завершён успешно.")


if __name__ == "__main__":
    # возможность запускать напрямую через:  python db_pars.py
    run_import_from_excel()
