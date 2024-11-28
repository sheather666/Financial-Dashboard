import streamlit as st
import pandas as pd
import plotly.express as px
from etl import users_data, categories_data, transactions_data, user_transaction_count_data, user_summary_data, transactions_extended_data

# Основной заголовок
st.title("Дашборд личных финансов")

# Фильтры
st.sidebar.header("Фильтры")

# Обновляем имена пользователей в фильтре
user_names = users_data['name'].tolist()

# Фильтр по пользователю (мультиселект)
user_filter = st.sidebar.selectbox(
    "Выберите пользователя", 
    options=user_names,
    index=0  # По умолчанию выбирается первый пользователь
)
# Фильтр по категориям
category_filter = st.sidebar.multiselect(
    "Выберите категории расходов", 
    options=categories_data["category_name"].unique(),
    default=categories_data["category_name"].unique()
)

# Фильтр по типу транзакции
transaction_filter = st.sidebar.selectbox(
    "Выберите тип транзакции", 
    options=["Все", "Доход", "Расход"],
    index=0
)

# Фильтр по датам
transactions_data['date'] = pd.to_datetime(transactions_data['date'])  # Убедимся, что даты имеют правильный формат
start_date = pd.to_datetime(st.sidebar.date_input("Начальная дата", value=transactions_data['date'].min()))
end_date = pd.to_datetime(st.sidebar.date_input("Конечная дата", value=transactions_data['date'].max()))

transactions_data['type'] = transactions_data['type'].str.strip().str.lower()

# Применяем фильтры
filtered_user = users_data[users_data["name"] == user_filter]  # Теперь это будет один пользователь
filtered_categories = categories_data[categories_data["category_name"].isin(category_filter)]
filtered_transactions = transactions_data[
    (transactions_data["user_id"].isin(filtered_user["user_id"])) & 
    (transactions_data["category_name"].isin(filtered_categories["category_name"])) & 
    (transactions_data["date"] >= start_date) & 
    (transactions_data["date"] <= end_date)
]

# Преобразуем значения фильтра в соответствующие значения в таблице
if transaction_filter == "Доход":
    transaction_type = "income"
elif transaction_filter == "Расход":
    transaction_type = "expense"
else:
    transaction_type = "all"  # Для случая "Все"

# Применяем фильтр по типу транзакции
if transaction_type != "all":
    filtered_transactions = filtered_transactions[filtered_transactions["type"] == transaction_type]

# Если после фильтрации не осталось данных, показываем предупреждение
if filtered_transactions.empty:
    st.warning("Нет данных для отображения с выбранными фильтрами.")

# Вкладки
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Обзор", "Анализ категорий", "Глубокий анализ",  "Тренды расходов по категориям", "Доходы всех пользователей"])

# Вкладка "Обзор"
with tab1:
    st.header("Общая информация")
    # Извлекаем имя и возраст из отфильтрованного пользователя
    user_name = filtered_user['name'].iloc[0]  # Извлекаем имя из отфильтрованного пользователя
    user_age = filtered_user['age'].iloc[0]  # Извлекаем возраст из отфильтрованного пользователя

    # Отображаем имя и возраст пользователя
    st.markdown(f"<h3 style='text-align: right; font-size: 24px; margin: 5px 0;'>Name: {user_name}</h3>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: right; font-size: 20px; margin: 0;'>Age: {user_age} years</h4>", unsafe_allow_html=True)  

    # Фильтруем транзакции по выбранному пользователю
    filtered_transactions_for_user = filtered_transactions[
        filtered_transactions["user_id"] == filtered_user["user_id"].iloc[0]
    ]

    # Основные данные по доходам и расходам для выбранного пользователя
    total_income = filtered_user['income'].iloc[0]
    total_expense = filtered_transactions_for_user.query("type == 'expense'")["amount"].sum()
    total_savings = total_income - total_expense

    st.metric("Общий доход", f"{total_income:,.2f} ₽")
    st.metric("Общий расход", f"{total_expense:,.2f} ₽")
    st.metric("Сбережения", f"{total_savings:,.2f} ₽")

    if total_savings < 0:
        st.metric("Перерасход", f"{abs(total_savings):,.2f} ₽", delta=-abs(total_savings))
    else:
        st.metric("Экономия", f"{total_savings:,.2f} ₽", delta=abs(total_savings))

    st.subheader("Количество транзакций пользователя")
    user_transaction_count = user_transaction_count_data[user_transaction_count_data['user_id'] == filtered_user['user_id'].iloc[0]]['transaction_count'].iloc[0]
    st.metric("Количество транзакций", f"{user_transaction_count}")
    
    avg_transaction = user_transaction_count_data[
    user_transaction_count_data["user_id"] == filtered_user["user_id"].iloc[0]]["avg_transaction_amount"].iloc[0]
    st.metric("Средняя сумма транзакции", f"{avg_transaction:,.2f} ₽")
    
    min_transaction = user_transaction_count_data[
    user_transaction_count_data["user_id"] == filtered_user["user_id"].iloc[0]]["min_transaction_amount"].iloc[0]
    st.metric("Минимальная сумма транзакции", f"{min_transaction:,.2f} ₽")

    max_transaction = user_transaction_count_data[
    user_transaction_count_data["user_id"] == filtered_user["user_id"].iloc[0]]["max_transaction_amount"].iloc[0]
    st.metric("Максимальная сумма транзакции", f"{max_transaction:,.2f} ₽")


# Вкладка "Анализ категорий"
with tab2:
    st.header("Анализ категорий")

    # Фильтруем данные по расходам
    expense_data = filtered_transactions.query("type == 'expense'")
    income_data = filtered_transactions.query("type == 'income'")

    # График расходов по категориям
    expense_by_category = expense_data.groupby("category_name")["amount"].sum().reset_index()
    fig_expense = px.bar(
        expense_by_category,
        x="category_name",
        y="amount",
        title="Расходы по категориям",
        labels={"category_name": "Категория", "amount": "Сумма"},
        color="category_name",
        color_discrete_sequence=px.colors.qualitative.Set1,
    )
    st.plotly_chart(fig_expense)

    # График доходов по категориям
    income_by_category = income_data.groupby("category_name")["amount"].sum().reset_index()
    fig_income = px.bar(
        income_by_category,
        x="category_name",
        y="amount",
        title="Доходы по категориям",
        labels={"category_name": "Категория", "amount": "Сумма"},
        color="category_name",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    st.plotly_chart(fig_income)

# Вкладка "Глубокий анализ"
with tab3:
    st.header("Глубокий анализ расходов")

    # Фильтруем данные по выбранному пользователю
    user_transactions = transactions_extended_data[
        transactions_extended_data["user_id"] == filtered_user["user_id"].iloc[0]
    ]

    # Анализ по дням недели
    weekday_data = user_transactions.groupby("transaction_weekday")["amount"].sum().reset_index()
    weekday_data["transaction_weekday"] = weekday_data["transaction_weekday"].replace({
        0: "Воскресенье", 1: "Понедельник", 2: "Вторник", 3: "Среда",
        4: "Четверг", 5: "Пятница", 6: "Суббота"
    })
    fig_weekday = px.bar(
        weekday_data,
        x="transaction_weekday",
        y="amount",
        title="Расходы по дням недели",
        labels={"transaction_weekday": "День недели", "amount": "Сумма"}
    )
    st.plotly_chart(fig_weekday)

    # Анализ по месяцам
    monthly_data = user_transactions.groupby("transaction_month")["amount"].sum().reset_index()
    monthly_data["transaction_month"] = monthly_data["transaction_month"].apply(
        lambda x: {1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
                5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
                9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"}[x]
    )
    fig_monthly = px.bar(
        monthly_data,
        x="transaction_month",
        y="amount",
        title="Расходы по месяцам",
        labels={"transaction_month": "Месяц", "amount": "Сумма"}
    )
    st.plotly_chart(fig_monthly)

    # Анализ по кварталам
    quarterly_data = user_transactions.groupby("transaction_quarter")["amount"].sum().reset_index()
    quarterly_data["transaction_quarter"] = quarterly_data["transaction_quarter"].apply(
        lambda x: f"{x}-й квартал"
    )
    fig_quarterly = px.bar(
        quarterly_data,
        x="transaction_quarter",
        y="amount",
        title="Расходы по кварталам",
        labels={"transaction_quarter": "Квартал", "amount": "Сумма"}
    )
    st.plotly_chart(fig_quarterly)

    # Анализ по годам
    yearly_data = user_transactions.groupby("transaction_year")["amount"].sum().reset_index()
    fig_yearly = px.bar(
        yearly_data,
        x="transaction_year",
        y="amount",
        title="Расходы по годам",
        labels={"transaction_year": "Год", "amount": "Сумма"}
    )
    st.plotly_chart(fig_yearly)
        

# Вкладка "Тренды расходов по категориям"
with tab4:
    st.header("Тренды расходов по категориям")

    # Фильтруем только расходы
    expense_transactions = filtered_transactions.query("type == 'expense'")

    if expense_transactions.empty:
        st.warning("Нет данных о расходах для выбранных фильтров.")
    else:
        category_trends = expense_transactions.groupby(
            [expense_transactions['date'].dt.to_period('M'), "category_name"]
        )["amount"].sum().reset_index()

        # Преобразуем период обратно в datetime для отображения на графике
        category_trends["date"] = category_trends["date"].dt.to_timestamp()

        all_categories = expense_transactions["category_name"].unique()
        all_periods = category_trends["date"].unique()

        # Формируем полный список всех возможных комбинаций (период, категория)
        full_combinations = pd.MultiIndex.from_product([all_periods, all_categories], names=["date", "category_name"])

        # Объединяем с существующими данными, чтобы гарантировать наличие всех комбинаций
        category_trends = category_trends.set_index(["date", "category_name"]).reindex(full_combinations, fill_value=0).reset_index()

        fig_trends = px.line(
            category_trends,
            x="date",
            y="amount",
            color="category_name",
            title="Тренды расходов по категориям",
            labels={"date": "Дата", "amount": "Сумма расходов", "category_name": "Категория"},
            line_shape="spline"
        )

        st.plotly_chart(fig_trends)

# Вкладка "Сводка пользователей"
with tab5:
    st.header("Детальная информация о пользователях")

    # Создаем таблицу данных для пользователей
    user_summary_table = user_summary_data.copy()
    user_summary_table["Доход"] = user_summary_table["user_id"].apply(
        lambda uid: users_data[users_data["user_id"] == uid]["income"].iloc[0]
    )

    # Убираем лишнюю информацию из user_summary для отображения
    user_summary_table["Имя"] = user_summary_table["user_summary"].apply(lambda x: x.split(' (')[0])
    user_summary_table.drop(columns=["user_summary", "user_id"], inplace=True)

    # Форматируем данные с помощью pandas
    user_summary_table["Доход"] = user_summary_table["Доход"].map("{:,.2f} ₽".format)

    # Применяем стилизацию
    styled_table = user_summary_table.style.highlight_max(
        subset=["Доход"], color="lightgreen", axis=0
    ).highlight_min(
        subset=["Доход"], color="lightcoral", axis=0
    )

    # Выравниваем таблицу по центру
    st.markdown(
        """
        <style>
        .centered-table {
            display: flex;
            justify-content: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Отображаем таблицу с шириной на весь контейнер
    st.markdown('<div class="centered-table">', unsafe_allow_html=True)
    st.dataframe(user_summary_table, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")  # Разделитель

    st.subheader("Общая статистика по пользователям")

    # Общая статистика по доходам
    total_income = users_data["income"].sum()
    avg_income = users_data["income"].mean()
    max_income = users_data["income"].max()
    min_income = users_data["income"].min()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Суммарный доход", f"{total_income:,.2f} ₽")
    col2.metric("Средний доход", f"{avg_income:,.2f} ₽")
    col3.metric("Максимальный доход", f"{max_income:,.2f} ₽")
    col4.metric("Минимальный доход", f"{min_income:,.2f} ₽")

