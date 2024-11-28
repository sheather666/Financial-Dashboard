COPY Users FROM 'source/users.csv' (AUTO_DETECT TRUE);
COPY ExpenseCategories FROM 'source/categories.csv' (AUTO_DETECT TRUE);
COPY Transactions FROM 'source/transactions.csv' (AUTO_DETECT TRUE);