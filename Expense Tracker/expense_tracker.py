import sqlite3

def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            amount REAL NOT NULL,
            category_id INTEGER,
            date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY,
            month TEXT NOT NULL,
            amount REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_category(name):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('INSERT INTO categories (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()

def add_expense(amount, category_name, date, description=''):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
    category_id = c.fetchone()
    if category_id:
        print(f"Inserting expense: Amount={amount}, CategoryID={category_id[0]}, Date={date}, Description={description}")
        c.execute('INSERT INTO expenses (amount, category_id, date, description) VALUES (?, ?, ?, ?)',
                  (amount, category_id[0], date, description))
        conn.commit()
        # Check if the expense is added
        c.execute('SELECT * FROM expenses')
        print("Expenses Table:", c.fetchall())
    else:
        print(f"Category '{category_name}' does not exist.")
    conn.close()

def set_budget(month, amount):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('REPLACE INTO budgets (month, amount) VALUES (?, ?)', (month, amount))
    conn.commit()
    conn.close()

def get_monthly_expense(month):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    print(f"Retrieving expenses for month: {month}")
    c.execute('SELECT * FROM expenses')
    print("Expenses Table:", c.fetchall())
    c.execute('SELECT SUM(amount) FROM expenses WHERE strftime("%Y-%m", date) = ?', (month,))
    total = c.fetchone()[0]
    print(f"Total expenses for {month}: {total}")
    conn.close()
    return total if total else 0

def get_budget_status(month):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    print(f"Retrieving budget for month: {month}")
    c.execute('SELECT amount FROM budgets WHERE month = ?', (month,))
    budget = c.fetchone()
    if budget:
        budget = budget[0]
    else:
        budget = 0
    total_expense = get_monthly_expense(month)
    remaining = budget - total_expense
    print(f"Total expense: {total_expense}, Budget: {budget}, Remaining: {remaining}")
    conn.close()
    return total_expense, budget, remaining

def get_daily_spending_goal(month):
    from datetime import datetime
    import calendar
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('SELECT amount FROM budgets WHERE month = ?', (month,))
    budget = c.fetchone()
    if budget:
        budget = budget[0]
    else:
        budget = 0
    now = datetime.now()
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    total_expense = get_monthly_expense(month)
    remaining = budget - total_expense
    days_left = days_in_month - now.day
    daily_goal = remaining / days_left if days_left > 0 else 0
    conn.close()
    return daily_goal

def add_saving_goal(name, amount):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('INSERT INTO saving_goals (name, amount) VALUES (?, ?)', (name, amount))
    conn.commit()
    conn.close()

import pandas as pd
import matplotlib.pyplot as plt

def visualize_expenses():
    conn = sqlite3.connect('expenses.db')
    df = pd.read_sql_query('''
        SELECT e.amount, c.name as category, e.date, e.description
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
    ''', conn)
    conn.close()

    # Pie chart
    pie_data = df.groupby('category').sum()
    pie_data.plot.pie(y='amount', autopct='%1.1f%%')
    plt.title('Expenses by Category')
    plt.ylabel('')
    plt.show()

    # Monthly expenses
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    monthly_data = df.resample('M').sum()
    monthly_data.plot(kind='bar', y='amount')
    plt.title('Monthly Expenses')
    plt.ylabel('Amount')
    plt.show()

def main():
    init_db()

    while True:
        print("\nExpense Tracker Menu")
        print("1. Add Category")
        print("2. Add Expense")
        print("3. Set Budget")
        print("4. View Budget Status")
        print("5. View Daily Spending Goal")
        print("6. Add Saving Goal")
        print("7. Visualize Expenses")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter category name: ")
            add_category(name)
        elif choice == '2':
            amount = float(input("Enter expense amount: "))
            category_name = input("Enter category name: ")
            date = input("Enter date (YYYY-MM-DD): ")
            description = input("Enter description (optional): ")
            add_expense(amount, category_name, date, description)
        elif choice == '3':
            month = input("Enter month (YYYY-MM): ")
            amount = float(input("Enter budget amount: "))
            set_budget(month, amount)
        elif choice == '4':
            month = input("Enter month (YYYY-MM): ")
            total_expense, budget, remaining = get_budget_status(month)
            print(f"Total expense: {total_expense}, Budget: {budget}, Remaining: {remaining}")
        elif choice == '5':
            month = input("Enter month (YYYY-MM): ")
            daily_goal = get_daily_spending_goal(month)
            print(f"Daily spending goal: {daily_goal}")
        elif choice == '6':
            name = input("Enter saving goal name: ")
            amount = float(input("Enter saving goal amount: "))
            add_saving_goal(name, amount)
        elif choice == '7':
            visualize_expenses()
        elif choice == '8':
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()

