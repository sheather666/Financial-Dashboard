CREATE TABLE Users (
    user_id INT PRIMARY KEY,
    name VARCHAR,
    age INT,
    income INT
);

CREATE TABLE ExpenseCategories (
    category_id INT PRIMARY KEY,
    category_name VARCHAR,
    budget INT
);

CREATE TABLE Transactions (
    transaction_id INT PRIMARY KEY,
    user_id INT REFERENCES Users(user_id),
    date DATE,
    amount DOUBLE,
    category INT REFERENCES ExpenseCategories(category_id),
    type VARCHAR
);