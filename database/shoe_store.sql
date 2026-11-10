-- CREATE DATABASE shoese;

-- Таблица пунктов выдачи
CREATE TABLE pickup_points (
    id_pickup_point SERIAL PRIMARY KEY,
    address VARCHAR(255) NOT NULL UNIQUE
);

COMMENT ON TABLE pickup_points IS 'Таблица пунктов выдачи заказов';
COMMENT ON COLUMN pickup_points.id_pickup_point IS 'Уникальный идентификатор пункта выдачи';
COMMENT ON COLUMN pickup_points.address IS 'Адрес пункта выдачи';

-- Таблица пользователей
CREATE TABLE users (
    id_user SERIAL PRIMARY KEY,
    role VARCHAR(50) NOT NULL CHECK (role IN ('Администратор', 'Менеджер', 'Авторизированный клиент')),
    full_name VARCHAR(255) NOT NULL,
    login VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

COMMENT ON TABLE users IS 'Таблица пользователей системы';
COMMENT ON COLUMN users.id_user IS 'Уникальный идентификатор пользователя';
COMMENT ON COLUMN users.role IS 'Роль сотрудника: Администратор, Менеджер, Авторизированный клиент';
COMMENT ON COLUMN users.full_name IS 'Полное ФИО пользователя';
COMMENT ON COLUMN users.login IS 'Логин для входа в систему';
COMMENT ON COLUMN users.password IS 'Пароль пользователя';

-- Таблица товаров
CREATE TABLE products (
    id_product VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    supplier VARCHAR(255) NOT NULL,
    manufacturer VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    discount DECIMAL(5,2) NOT NULL,
    stock_quantity INTEGER NOT NULL,
    description TEXT,
    photo VARCHAR(255)
);

COMMENT ON TABLE products IS 'Таблица товаров магазина';
COMMENT ON COLUMN products.id_product IS 'Артикул товара';
COMMENT ON COLUMN products.name IS 'Наименование товара';
COMMENT ON COLUMN products.unit IS 'Единица измерения';
COMMENT ON COLUMN products.price IS 'Цена товара';
COMMENT ON COLUMN products.supplier IS 'Поставщик товара';
COMMENT ON COLUMN products.manufacturer IS 'Производитель товара';
COMMENT ON COLUMN products.category IS 'Категория товара';
COMMENT ON COLUMN products.discount IS 'Действующая скидка в процентах';
COMMENT ON COLUMN products.stock_quantity IS 'Количество товара на складе';
COMMENT ON COLUMN products.description IS 'Описание товара';
COMMENT ON COLUMN products.photo IS 'Путь к файлу изображения на сервере';

-- Таблица заказов
CREATE TABLE orders (
    id_order SERIAL PRIMARY KEY,
    order_date TIMESTAMP NOT NULL,
    delivery_date TIMESTAMP NOT NULL,
    id_pickup_point INTEGER NOT NULL,
    id_client INTEGER NOT NULL,
    pickup_code VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('Новый', 'Завершен')),
    FOREIGN KEY (id_pickup_point) REFERENCES pickup_points(id_pickup_point),
    FOREIGN KEY (id_client) REFERENCES users(id_user)
);

COMMENT ON TABLE orders IS 'Таблица заказов';
COMMENT ON COLUMN orders.id_order IS 'Уникальный идентификатор заказа';
COMMENT ON COLUMN orders.order_date IS 'Дата оформления заказа';
COMMENT ON COLUMN orders.delivery_date IS 'Дата доставки';
COMMENT ON COLUMN orders.id_pickup_point IS 'Внешний ключ к пункту выдачи';
COMMENT ON COLUMN orders.id_client IS 'Внешний ключ к заказчику';
COMMENT ON COLUMN orders.pickup_code IS 'Код для получения заказа';
COMMENT ON COLUMN orders.status IS 'Статус заказа: Новый, Завершен';

-- Таблица позиций заказа
CREATE TABLE order_items (
    id_order_item SERIAL PRIMARY KEY,
    id_order INTEGER NOT NULL,
    id_product VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (id_order) REFERENCES orders(id_order) ON DELETE CASCADE,
    FOREIGN KEY (id_product) REFERENCES products(id_product)
);

COMMENT ON TABLE order_items IS 'Таблица позиций в заказах';
COMMENT ON COLUMN order_items.id_order_item IS 'Уникальный идентификатор позиции заказа';
COMMENT ON COLUMN order_items.id_order IS 'Внешний ключ к заказу';
COMMENT ON COLUMN order_items.id_product IS 'Внешний ключ к товару';
COMMENT ON COLUMN order_items.quantity IS 'Количество товара в заказе';



-- -- Заполнение пунктов выдачи
-- INSERT INTO pickup_points (address) VALUES
-- ('420151, г. Лесной, ул. Вишневая, 32'),
-- ('125061, г. Лесной, ул. Подгорная, 8'),
-- ('630370, г. Лесной, ул. Шоссейная, 24'),
-- ('400562, г. Лесной, ул. Зеленая, 32'),
-- ('614510, г. Лесной, ул. Маяковского, 47'),
-- ('410542, г. Лесной, ул. Светлая, 46'),
-- ('620839, г. Лесной, ул. Цветочная, 8'),
-- ('443890, г. Лесной, ул. Коммунистическая, 1'),
-- ('603379, г. Лесной, ул. Спортивная, 46'),
-- ('603721, г. Лесной, ул. Гоголя, 41'),
-- ('410172, г. Лесной, ул. Северная, 13'),
-- ('614611, г. Лесной, ул. Молодежная, 50'),
-- ('454311, г. Лесной, ул. Новая, 19'),
-- ('660007, г. Лесной, ул. Октябрьская, 19'),
-- ('603036, г. Лесной, ул. Садовая, 4'),
-- ('394060, г. Лесной, ул. Фрунзе, 43'),
-- ('410661, г. Лесной, ул. Школьная, 50'),
-- ('625590, г. Лесной, ул. Коммунистическая, 20'),
-- ('625683, г. Лесной, ул. 8 Марта'),
-- ('450983, г. Лесной, ул. Комсомольская, 26'),
-- ('394782, г. Лесной, ул. Чехова, 3'),
-- ('603002, г. Лесной, ул. Дзержинского, 28'),
-- ('450558, г. Лесной, ул. Набережная, 30'),
-- ('344288, г. Лесной, ул. Чехова, 1'),
-- ('614164, г. Лесной, ул. Степная, 30'),
-- ('394242, г. Лесной, ул. Коммунистическая, 43'),
-- ('660540, г. Лесной, ул. Солнечная, 25'),
-- ('125837, г. Лесной, ул. Шоссейная, 40'),
-- ('125703, г. Лесной, ул. Партизанская, 49'),
-- ('625283, г. Лесной, ул. Победы, 46'),
-- ('614753, г. Лесной, ул. Полевая, 35'),
-- ('426030, г. Лесной, ул. Маяковского, 44'),
-- ('450375, г. Лесной ул. Клубная, 44'),
-- ('625560, г. Лесной, ул. Некрасова, 12'),
-- ('630201, г. Лесной, ул. Комсомольская, 17'),
-- ('190949, г. Лесной, ул. Мичурина, 26');

-- -- Заполнение пользователей
-- INSERT INTO users (role, full_name, login, password) VALUES
-- ('Администратор', 'Никифорова Весения Николаевна', '94d5ous@gmail.com', 'uzWC67'),
-- ('Администратор', 'Сазонов Руслан Германович', 'uth4iz@mail.com', '2L6KZG'),
-- ('Администратор', 'Одинцов Серафим Артёмович', 'yzls62@outlook.com', 'JlFRCZ'),
-- ('Менеджер', 'Степанов Михаил Артёмович', '1diph5e@tutanota.com', '8ntwUp'),
-- ('Менеджер', 'Ворсин Петр Евгеньевич', 'tjde7c@yahoo.com', 'YOyhfR'),
-- ('Менеджер', 'Старикова Елена Павловна', 'wpmrc3do@tutanota.com', 'RSbvHv'),
-- ('Авторизированный клиент', 'Михайлюк Анна Вячеславовна', '5d4zbu@tutanota.com', 'rwVDh9'),
-- ('Авторизированный клиент', 'Ситдикова Елена Анатольевна', 'ptec8ym@yahoo.com', 'LdNyos'),
-- ('Авторизированный клиент', 'Ворсин Петр Евгеньевич', '1qz4kw@mail.com', 'gynQMT'),
-- ('Авторизированный клиент', 'Старикова Елена Павловна', '4np6se@mail.com', 'AtnDjr');

-- -- Заполнение товаров (без фото)
-- INSERT INTO products (id_product, name, unit, price, supplier, manufacturer, category, discount, stock_quantity, description) VALUES
-- ('А112Т4', 'Ботинки', 'шт.', 4990.00, 'Kari', 'Kari', 'Женская обувь', 3.00, 6, 'Женские Ботинки демисезонные kari'),
-- ('F635R4', 'Ботинки', 'шт.', 3244.00, 'Обувь для вас', 'Marco Tozzi', 'Женская обувь', 2.00, 13, 'Ботинки Marco Tozzi женские демисезонные, размер 39, цвет бежевый'),
-- ('H782T5', 'Туфли', 'шт.', 4499.00, 'Kari', 'Kari', 'Мужская обувь', 4.00, 5, 'Туфли kari мужские классика MYZ21AW-450A, размер 43, цвет: черный'),
-- ('G783F5', 'Ботинки', 'шт.', 5900.00, 'Kari', 'Рос', 'Мужская обувь', 2.00, 8, 'Мужские ботинки Рос-Обувь кожаные с натуральным мехом'),
-- ('J384T6', 'Ботинки', 'шт.', 3800.00, 'Обувь для вас', 'Rieker', 'Мужская обувь', 2.00, 16, 'B3430/14 Полуботинки мужские Rieker'),
-- ('D572U8', 'Кроссовки', 'шт.', 4100.00, 'Обувь для вас', 'Рос', 'Мужская обувь', 3.00, 6, '129615-4 Кроссовки мужские'),
-- ('F572H7', 'Туфли', 'шт.', 2700.00, 'Kari', 'Marco Tozzi', 'Женская обувь', 2.00, 14, 'Туфли Marco Tozzi женские летние, размер 39, цвет черный'),
-- ('D329H3', 'Полуботинки', 'шт.', 1890.00, 'Обувь для вас', 'Alessio Nesca', 'Женская обувь', 4.00, 4, 'Полуботинки Alessio Nesca женские 3-30797-47, размер 37, цвет: бордовый'),
-- ('B320R5', 'Туфли', 'шт.', 4300.00, 'Kari', 'Rieker', 'Женская обувь', 2.00, 6, 'Туфли Rieker женские демисезонные, размер 41, цвет коричневый'),
-- ('G432E4', 'Туфли', 'шт.', 2800.00, 'Kari', 'Kari', 'Женская обувь', 3.00, 15, 'Туфли kari женские TR-YR-413017, размер 37, цвет: черный'),
-- ('S213E3', 'Полуботинки', 'шт.', 2156.00, 'Обувь для вас', 'CROSBY', 'Мужская обувь', 3.00, 6, '407700/01-01 Полуботинки мужские CROSBY'),
-- ('E482R4', 'Полуботинки', 'шт.', 1800.00, 'Kari', 'Kari', 'Женская обувь', 2.00, 14, 'Полуботинки kari женские MYZ20S-149, размер 41, цвет: черный'),
-- ('S634B5', 'Кеды', 'шт.', 5500.00, 'Обувь для вас', 'CROSBY', 'Мужская обувь', 3.00, 0, 'Кеды Caprice мужские демисезонные, размер 42, цвет черный'),
-- ('K345R4', 'Полуботинки', 'шт.', 2100.00, 'Обувь для вас', 'CROSBY', 'Мужская обувь', 2.00, 3, '407700/01-02 Полуботинки мужские CROSBY'),
-- ('O754F4', 'Туфли', 'шт.', 5400.00, 'Обувь для вас', 'Rieker', 'Женская обувь', 4.00, 18, 'Туфли женские демисезонные Rieker артикул 55073-68/37'),
-- ('G531F4', 'Ботинки', 'шт.', 6600.00, 'Kari', 'Kari', 'Женская обувь', 12.00, 9, 'Ботинки женские зимние ROMER арт. 893167-01 Черный'),
-- ('J542F5', 'Тапочки', 'шт.', 500.00, 'Kari', 'Kari', 'Мужская обувь', 13.00, 0, 'Тапочки мужские Арт.70701-55-67син р.41'),
-- ('B431R5', 'Ботинки', 'шт.', 2700.00, 'Обувь для вас', 'Rieker', 'Мужская обувь', 2.00, 5, 'Мужские кожаные ботинки/мужские ботинки'),
-- ('P764G4', 'Туфли', 'шт.', 6800.00, 'Kari', 'CROSBY', 'Женская обувь', 15.00, 15, 'Туфли женские, ARGO, размер 38'),
-- ('C436G5', 'Ботинки', 'шт.', 10200.00, 'Kari', 'Alessio Nesca', 'Женская обувь', 15.00, 9, 'Ботинки женские, ARGO, размер 40'),
-- ('F427R5', 'Ботинки', 'шт.', 11800.00, 'Обувь для вас', 'Rieker', 'Женская обувь', 15.00, 11, 'Ботинки на молнии с декоративной пряжкой FRAU'),
-- ('N457T5', 'Полуботинки', 'шт.', 4600.00, 'Kari', 'CROSBY', 'Женская обувь', 3.00, 13, 'Полуботинки Ботинки черные зимние, мех'),
-- ('D364R4', 'Туфли', 'шт.', 12400.00, 'Kari', 'Kari', 'Женская обувь', 16.00, 5, 'Туфли Luiza Belly женские Kate-lazo черные из натуральной замши'),
-- ('S326R5', 'Тапочки', 'шт.', 9900.00, 'Обувь для вас', 'CROSBY', 'Мужская обувь', 17.00, 15, 'Мужские кожаные тапочки "Профиль С.Дали"'),
-- ('L754R4', 'Полуботинки', 'шт.', 1700.00, 'Kari', 'Kari', 'Женская обувь', 2.00, 7, 'Полуботинки kari женские WB2020SS-26, размер 38, цвет: черный'),
-- ('M542T5', 'Кроссовки', 'шт.', 2800.00, 'Обувь для вас', 'Rieker', 'Мужская обувь', 18.00, 3, 'Кроссовки мужские TOFA'),
-- ('D268G5', 'Туфли', 'шт.', 4399.00, 'Обувь для вас', 'Rieker', 'Женская обувь', 3.00, 12, 'Туфли Rieker женские демисезонные, размер 36, цвет коричневый'),
-- ('T324F5', 'Сапоги', 'шт.', 4699.00, 'Kari', 'CROSBY', 'Женская обувь', 2.00, 5, 'Сапоги замша Цвет: синий'),
-- ('K358H6', 'Тапочки', 'шт.', 599.00, 'Kari', 'Rieker', 'Мужская обувь', 20.00, 2, 'Тапочки мужские син р.41'),
-- ('H535R5', 'Ботинки', 'шт.', 2300.00, 'Обувь для вас', 'Rieker', 'Женская обувь', 2.00, 7, 'Женские Ботинки демисезонные');

-- -- Заполнение заказов (исправляем некорректную дату в заказе 7)
-- INSERT INTO orders (id_order, order_date, delivery_date, id_pickup_point, id_client, pickup_code, status) VALUES
-- (1, '2025-02-27 00:00:00', '2025-04-20 00:00:00', 1, 4, '901', 'Завершен'),
-- (2, '2022-09-28 00:00:00', '2025-04-21 00:00:00', 11, 2, '902', 'Завершен'),
-- (3, '2025-03-21 00:00:00', '2025-04-22 00:00:00', 2, 3, '903', 'Завершен'),
-- (4, '2025-02-20 00:00:00', '2025-04-23 00:00:00', 11, 4, '904', 'Завершен'),
-- (5, '2025-03-17 00:00:00', '2025-04-24 00:00:00', 2, 4, '905', 'Завершен'),
-- (6, '2025-03-01 00:00:00', '2025-04-25 00:00:00', 15, 2, '906', 'Завершен'),
-- (7, '2025-03-30 00:00:00', '2025-04-26 00:00:00', 3, 3, '907', 'Завершен'), -- Исправлена дата 30.02.2025 на 30.03.2025
-- (8, '2025-03-31 00:00:00', '2025-04-27 00:00:00', 19, 4, '908', 'Новый'),
-- (9, '2025-04-02 00:00:00', '2025-04-28 00:00:00', 5, 4, '909', 'Новый'),
-- (10, '2025-04-03 00:00:00', '2025-04-29 00:00:00', 19, 4, '910', 'Новый');

-- -- Заполнение позиций заказов (парсим поле "Артикул заказа")
-- INSERT INTO order_items (id_order, id_product, quantity) VALUES
-- -- Заказ 1: А112Т4, 2, F635R4, 2
-- (1, 'А112Т4', 2),
-- (1, 'F635R4', 2),

-- -- Заказ 2: H782T5, 1, G783F5, 1
-- (2, 'H782T5', 1),
-- (2, 'G783F5', 1),

-- -- Заказ 3: J384T6, 10, D572U8, 10
-- (3, 'J384T6', 10),
-- (3, 'D572U8', 10),

-- -- Заказ 4: F572H7, 5, D329H3, 4
-- (4, 'F572H7', 5),
-- (4, 'D329H3', 4),

-- -- Заказ 5: А112Т4, 2, F635R4, 2
-- (5, 'А112Т4', 2),
-- (5, 'F635R4', 2),

-- -- Заказ 6: H782T5, 1, G783F5, 1
-- (6, 'H782T5', 1),
-- (6, 'G783F5', 1),

-- -- Заказ 7: J384T6, 10, D572U8, 10
-- (7, 'J384T6', 10),
-- (7, 'D572U8', 10),

-- -- Заказ 8: F572H7, 5, D329H3, 4
-- (8, 'F572H7', 5),
-- (8, 'D329H3', 4),

-- -- Заказ 9: B320R5, 5, G432E4, 1
-- (9, 'B320R5', 5),
-- (9, 'G432E4', 1),

-- -- Заказ 10: S213E3, 5, E482R4, 5
-- (10, 'S213E3', 5),
-- (10, 'E482R4', 5);


-- UPDATE products 
-- SET photo = 'resources/products/1.jpg'
-- WHERE id_product = 'А112Т4';

-- UPDATE products 
-- SET photo = 'resources/products/2.jpg'
-- WHERE id_product = 'F635R4';

-- UPDATE products 
-- SET photo = 'resources/products/3.jpg'
-- WHERE id_product = 'H782T5';

-- UPDATE products 
-- SET photo = 'resources/products/4.jpg'
-- WHERE id_product = 'G783F5';

-- UPDATE products 
-- SET photo = 'resources/products/5.jpg'
-- WHERE id_product = 'J384T6';

-- UPDATE products 
-- SET photo = 'resources/products/6.jpg'
-- WHERE id_product = 'D572U8';

-- UPDATE products 
-- SET photo = 'resources/products/7.jpg'
-- WHERE id_product = 'F572H7';

-- UPDATE products 
-- SET photo = 'resources/products/8.jpg'
-- WHERE id_product = 'D329H3';

-- UPDATE products 
-- SET photo = 'resources/products/9.jpg'
-- WHERE id_product = 'B320R5';

-- UPDATE products 
-- SET photo = 'resources/products/10.jpg'
-- WHERE id_product = 'G432E4';


-- CREATE SEQUENCE pickup_code_seq START 901;

-- ALTER TABLE orders 
--     ALTER COLUMN pickup_code TYPE INTEGER USING pickup_code::INTEGER;

-- ALTER TABLE orders 
--     ALTER COLUMN pickup_code SET DEFAULT nextval('pickup_code_seq');
