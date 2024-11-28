import duckdb
import pandas as pd

# Путь к базе данных
db_path = "my.db"
conn = duckdb.connect(db_path)

# Функция для извлечения данных с помощью SQL-запроса
def get_data(query):
    """Извлечение данных из базы данных по SQL-запросу."""
    return pd.read_sql(query, conn)

# Извлечение данных из вьюшек
users_query = "SELECT * FROM users_view;"
categories_query = "SELECT * FROM categories_view;"
transactions_query = """
SELECT transaction_id, user_id, date, amount, type, category_name, is_income_allowed
FROM transactions_view;
"""
user_transaction_count_query = "SELECT * FROM user_transaction_count;"
user_summary_query = "SELECT * FROM user_summary;"
transactions_extended_query = "SELECT * FROM transactions_extended;"
cumulative_expense_query = "SELECT * FROM cumulative_expense;"
high_spenders_query = "SELECT * FROM high_spenders;"

# Загрузка данных из вьюшек
users_data = get_data(users_query)
categories_data = get_data(categories_query)
transactions_data = get_data(transactions_query)
user_transaction_count_data = get_data(user_transaction_count_query)
user_summary_data = get_data(user_summary_query)
transactions_extended_data = get_data(transactions_extended_query)

conn.close()


print("Данные успешно загружены и подготовлены.")
