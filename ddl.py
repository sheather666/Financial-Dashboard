import duckdb

# Путь к базе данных
db_path = "my.db"
conn = duckdb.connect(db_path)

# Удаляем существующие вьюшки и таблицы
drop_views_sql = """
DROP VIEW IF EXISTS users_view;
DROP VIEW IF EXISTS categories_view;
DROP VIEW IF EXISTS transactions_view;
"""

drop_tables_sql = """
DROP TABLE IF EXISTS Transactions;
DROP TABLE IF EXISTS ExpenseCategories;
DROP TABLE IF EXISTS Users;
"""

conn.execute(drop_views_sql)
conn.execute(drop_tables_sql)

# Создаём таблицы с учётом новых полей
create_tables_sql = """
-- Таблица пользователей
CREATE TABLE Users (
    user_id INT PRIMARY KEY,
    name VARCHAR,
    age INT,
    income INT
);

-- Таблица категорий расходов
CREATE TABLE ExpenseCategories (
    category_id INT PRIMARY KEY,
    category_name VARCHAR,
    budget INT,
    is_income_allowed BOOLEAN
);

-- Таблица транзакций
CREATE TABLE Transactions (
    transaction_id INT PRIMARY KEY,
    user_id INT REFERENCES Users(user_id),
    date DATE,
    amount DOUBLE,
    category INT REFERENCES ExpenseCategories(category_id),
    type VARCHAR
);
"""

create_views_sql = """
-- Вьюшка для пользователей
CREATE VIEW users_view AS
SELECT user_id, name, age, income, expense
FROM Users;

-- Вьюшка для категорий расходов
CREATE VIEW categories_view AS
SELECT category_id, category_name, budget, is_income_allowed
FROM ExpenseCategories;

-- Вьюшка для транзакций
CREATE VIEW transactions_view AS
SELECT t.transaction_id, t.user_id, t.date, t.amount, t.type, c.category_name, c.is_income_allowed
FROM Transactions t
JOIN ExpenseCategories c ON t.category = c.category_id;

-- Вьюшка для объединения имени и дохода пользователя
CREATE OR REPLACE VIEW user_summary AS
SELECT user_id, CONCAT(name, ' (доход: ', income, ' ₽)') AS user_summary
FROM users_view
GROUP BY user_id;

-- Вьюшка для подсчёта количества транзакций каждого пользователя
CREATE OR REPLACE VIEW user_transaction_count AS
SELECT 
    u.user_id, 
    u.name, 
    COUNT(t.transaction_id) AS transaction_count,
    AVG(t.amount) AS avg_transaction_amount,
    MAX(t.amount) AS max_transaction_amount,
    MIN(t.amount) AS min_transaction_amount
FROM Users u
LEFT JOIN Transactions t ON u.user_id = t.user_id
GROUP BY u.user_id, u.name;

-- Расширенная вьюшка для транзакций с добавлением месяца, года, дня недели и квартала

CREATE OR REPLACE VIEW transactions_extended AS
SELECT 
    t.transaction_id, 
    t.user_id, 
    t.date, 
    EXTRACT(MONTH FROM t.date) AS transaction_month,
    EXTRACT(YEAR FROM t.date) AS transaction_year,
    EXTRACT(DOW FROM t.date) AS transaction_weekday,  -- День недели
    EXTRACT(QUARTER FROM t.date) AS transaction_quarter,  -- Квартал
    t.amount, 
    t.type, 
    c.category_name
FROM Transactions t
JOIN ExpenseCategories c ON t.category = c.category_id;

-- Вьюшка для кумулятивных расходов (не реализовано)
CREATE OR REPLACE VIEW cumulative_expense AS
SELECT 
    t.user_id, 
    t.date, 
    t.amount, 
    SUM(t.amount) OVER (PARTITION BY t.user_id ORDER BY t.date) AS cumulative_sum
FROM Transactions t
WHERE t.type = 'expense';



-- Вьюшка для пользователей с расходами более 10,000 (не реализовано)
CREATE OR REPLACE VIEW high_spenders AS
SELECT 
    u.name, 
    SUM(t.amount) AS total_expense
FROM Users u
JOIN Transactions t ON u.user_id = t.user_id
WHERE t.type = 'expense'
GROUP BY u.user_id, u.name
HAVING SUM(t.amount) > 10000;
"""

conn.execute(create_tables_sql)
conn.execute(create_views_sql)

# Загрузка данных
conn.execute("COPY Users FROM 'source/users.csv' (FORMAT CSV, HEADER TRUE);")
conn.execute("COPY ExpenseCategories FROM 'source/categories.csv' (FORMAT CSV, HEADER TRUE);")
conn.execute("COPY Transactions FROM 'source/transactions.csv' (FORMAT CSV, HEADER TRUE);")

conn.close()

print("Обновлённые таблицы и вьюшки успешно созданы!")
