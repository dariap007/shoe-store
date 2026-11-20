# ShoeStore — система оформления заказов обуви

Учебный проект: десктопное приложение для просмотра каталога обуви и управления заказами.

## Возможности

- просмотр каталога обуви с ценой, скидкой и количеством товара в наличии;
- поиск по названию, категории, производителю и поставщику;
- фильтрация каталога по поставщику;
- сортировка товаров по количеству на складе;
- вход по логину и паролю или просмотр каталога в гостевом режиме;
- просмотр заказов менеджером и администратором;
- добавление и редактирование товаров, а также добавление, редактирование и удаление заказов администратором.

## Требования

- Python 3.10 или новее;
- PostgreSQL 14 или новее;
- библиотеки из файла `requirements.txt`.

## Установка и запуск

1. Клонируйте репозиторий:
   `git clone https://github.com/scapree/shoe_store.git`
2. Создайте и активируйте виртуальное окружение, затем установите зависимости:
   `python -m venv venv`
   `venv\Scripts\activate`
   `pip install -r requirements.txt`
3. Создайте базу данных PostgreSQL.
4. Скопируйте `config.ini.example` в `config.ini` и укажите параметры подключения к базе данных.
5. Запустите приложение из корня проекта:
   `python main.py`

При первом запуске на пустой базе приложение создаёт таблицы по скрипту `database/shoe_store.sql` и загружает начальные данные из `resources/import-data/`.

## Запуск PostgreSQL через Docker Compose

### Требования

- Docker Desktop запущен и использует Linux containers;
- установлен Docker Compose v2 (`docker compose version`);
- Python 3.10 или новее и зависимости проекта установлены в виртуальное окружение для запуска Tkinter-приложения в Windows.

### Настройка и запуск

Все команды выполняются в PowerShell из корня проекта.

1. Если локального `.env` ещё нет, создайте его из примера:

   ```powershell
   if (-not (Test-Path .env)) { Copy-Item .env.example .env }
   ```

   Откройте `.env` и задайте собственный локальный `POSTGRES_PASSWORD`. Если `.env` уже существует, не перезаписывайте его. Не записывайте настоящий пароль в `.env.example` и не отправляйте `.env` в Git: этот файл добавлен в `.gitignore`.

2. Проверьте конфигурацию и запустите контейнеры:

   ```powershell
   docker compose config --quiet
   docker compose up --build -d
   docker compose ps
   ```

   Дождитесь состояния `healthy` у сервиса `db`. Сервис `db-check` выполняет одноразовую проверку и после завершения может иметь состояние `Exited (0)`. При первом запуске пустой базы результат `таблиц=0` ожидаем.

### Импорт схемы и данных

Импортируйте SQL-схему в новую пустую базу один раз:

```powershell
docker compose cp database/shoe_store.sql db:/tmp/shoe_store.sql
docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /tmp/shoe_store.sql'
```

Затем, в активированном виртуальном окружении Python, загрузите данные из Excel-файлов проекта:

```powershell
python -c "from app.db_pars import run_import_from_excel; run_import_from_excel()"
```

Импортёр очищает таблицы перед загрузкой. Запускайте его повторно только если нужно заново загрузить данные.

Проверьте подключение и количество таблиц:

```powershell
docker compose run --rm db-check
```

При успешной проверке вывод начинается с `OK: база=shoe_store`; после импорта количество таблиц должно быть больше нуля.

### Подключение Tkinter-приложения

Приложение запускается в Windows, поэтому в локальном `config.ini` укажите параметры из `.env` и опубликованный порт хоста:

```ini
[database]
dbname = shoe_store
user = shoe_user
password = ваш_локальный_пароль
host = localhost
port = 5433
```

Если вы задали в `.env` другие имя базы, имя пользователя или порт, укажите те же значения в `config.ini`. Параметр приложения называется `dbname`. Файл `config.ini` также исключён из Git. Запустите приложение из корня проекта:

```powershell
python main.py
```

Внутри сети Compose сервисы используют адрес `db:5432`; для Tkinter-приложения в Windows используется `localhost:5433`.

### Остановка

Остановите контейнеры, не удаляя их:

```powershell
docker compose stop
```

Для повторного запуска используйте:

```powershell
docker compose start
```

## Постоянное хранение и сети

### Назначение тома

Сервис `db` хранит данные PostgreSQL в именованном томе `db_data`, который монтируется в `/var/lib/postgresql/data`. Тома сохраняют содержимое базы при остановке и пересоздании контейнера. Точное имя тома Compose имеет префикс проекта, например `shoe-store_db_data`.

Перед изменением или пересозданием хранилища создайте резервную копию работающей базы.

```powershell
docker compose exec db pg_dump -U shoe_user -d shoe_store -f /tmp/shoe_store_before_volume.sql
docker compose cp db:/tmp/shoe_store_before_volume.sql ./backups/shoe_store_before_volume.sql
Get-Item .\backups\shoe_store_before_volume.sql
Get-Content .\backups\shoe_store_before_volume.sql -TotalCount 12
```

Если имена базы или пользователя в `.env` изменены, используйте в команде соответствующие значения из `.env`. Каталог `backups/` исключён из Git и может содержать конфиденциальные данные.

### Восстановление в том

Остановите и удалите контейнеры без удаления томов, примените Compose-конфигурацию с монтированием `db_data` и запустите сервисы:

```powershell
docker compose config --quiet
docker compose down
docker compose up --build -d
docker compose ps
docker volume ls
```

Скопируйте резервную копию в контейнер и восстановите базу:

```powershell
docker compose cp ./backups/shoe_store_before_volume.sql db:/tmp/restore.sql
docker compose exec db psql -v ON_ERROR_STOP=1 -U shoe_user -d shoe_store -f /tmp/restore.sql
docker compose run --rm db-check
```

Проверьте сохранность записи после пересоздания контейнера:

```powershell
docker compose exec db psql -U shoe_user -d shoe_store -c "CREATE TABLE IF NOT EXISTS public.docker_persistence_check (id integer PRIMARY KEY, note text NOT NULL);"
docker compose exec db psql -U shoe_user -d shoe_store -c "INSERT INTO public.docker_persistence_check (id, note) VALUES (13, 'data survives recreation') ON CONFLICT (id) DO UPDATE SET note=EXCLUDED.note;"
docker compose up -d --force-recreate db
docker compose exec db psql -U shoe_user -d shoe_store -c "SELECT * FROM public.docker_persistence_check;"
```

### Команды запуска и остановки

```powershell
docker compose config --quiet
docker compose up --build -d
docker compose ps
docker compose run --rm db-check

docker compose stop       # остановить контейнеры с сохранением тома
docker compose start      # запустить остановленные контейнеры
docker compose down       # удалить контейнеры и сеть, сохранив том
docker compose up -d      # создать контейнеры заново
```

### Сети и адреса

- Сервисы `db` и `db-check` подключены к пользовательской сети bridge `shoe-backend`.
- Внутри сети Compose `db-check` обращается к PostgreSQL по DNS-имени `db` на порту `5432`.
- Для приложения Windows порт PostgreSQL опубликован только на loopback-интерфейсе хоста: `127.0.0.1:5433` → `db:5432`.
- В `config.ini` приложение использует `host = localhost` и `port = 5433`.
- Проверить сеть проекта можно командами `docker network ls` и `docker network inspect <имя-сети-shoe-backend>`.
- Команда `docker compose port db 5432` показывает опубликованный адрес хоста.

> **Важно:** не выполняйте `docker compose down -v`, если не хотите удалить именованные тома проекта. Эта команда может удалить данные базы вместе с контейнерами. Также с осторожностью используйте `docker volume prune` и ручное удаление томов.

## Структура репозитория

- `main.py` — точка входа приложения;
- `app/` — модули приложения и пользовательского интерфейса;
- `resources/` — изображения, иконки и исходные файлы для загрузки данных;
- `database/` — SQL-скрипт базы данных;
- `docs/` — ER-диаграмма и её исходный файл;
- `config.ini.example` — образец настроек подключения к базе данных.

## ER-диаграмма

База данных включает пользователей, товары, пункты выдачи, заказы и позиции заказов. Пользователь оформляет заказы, каждый заказ связан с пунктом выдачи и содержит одну или несколько позиций. Позиция заказа указывает товар и его количество, связывая заказы и товары отношением «многие ко многим». Подробная схема доступна в [`docs/ER-diagram.md`](docs/ER-diagram.md).

## Автор

Пятыго Дарья, ПКС-41
