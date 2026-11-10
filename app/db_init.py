import psycopg2
from app.config import DB_CONFIG, SCHEMA_FILE
from app.db_pars import run_import_from_excel


def init_if_needed():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'users'
            );
        """)

        exists = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        if not exists:
            init_database()
            run_import_from_excel()

    except Exception as e:
        print("Ошибка подключения:", e)
        return False


def init_database():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    with open(SCHEMA_FILE, "r", encoding="utf-8") as file:
        sql_script = file.read()

    cursor.execute(sql_script)

    conn.commit()
    cursor.close()
    conn.close()
