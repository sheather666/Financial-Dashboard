-- Вьюшка для данных пользователей
CREATE VIEW users_view AS
SELECT user_id, name, age, income
FROM Users;

-- Вьюшка для данных о категориях расходов
CREATE VIEW categories_view AS
SELECT category_id, category_name, budget
FROM ExpenseCategories;

-- Вьюшка для данных о транзакциях с полными данными о категориях
CREATE VIEW transactions_view AS
SELECT t.transaction_id, t.user_id, t.date, t.amount, t.type, c.category_name, t.is_income_allowed
FROM Transactions t
JOIN ExpenseCategories c ON t.category = c.category_id;

-- Количество транзакций для каждого пользователя
CREATE VIEW user_transaction_count AS
SELECT u.user_id, u.name, COUNT(t.transaction_id) AS transaction_count
FROM Users u
LEFT JOIN Transactions t ON u.user_id = t.user_id
GROUP BY u.user_id, u.name;

-- Объединение имени и дохода пользователя в одну строку
CREATE VIEW user_summary AS
SELECT user_id, CONCAT(name, ' (доход: ', income, ' ₽)') AS user_summary
FROM users_view;

-- Расширяем вьюшку транзакций для включения месяца и года
CREATE VIEW transactions_extended AS
SELECT t.transaction_id, t.user_id, t.date, 
       DATE_PART('month', t.date) AS transaction_month,
       DATE_PART('year', t.date) AS transaction_year,
       t.amount, t.type, c.category_name
FROM Transactions t
JOIN ExpenseCategories c ON t.category = c.category_id;

-- Кумулятивная сумма расходов
CREATE VIEW cumulative_expense AS
SELECT t.user_id, t.date, t.amount, 
       SUM(t.amount) OVER (PARTITION BY t.user_id ORDER BY t.date) AS cumulative_sum
FROM Transactions t
WHERE t.type = 'expense';

