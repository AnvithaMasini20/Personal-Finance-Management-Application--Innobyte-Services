#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sqlite3
import getpass
import datetime

# Database Setup
def init_db():
    conn = sqlite3.connect("finance_manager.db")
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL
                      )''')

    # Transactions Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        type TEXT CHECK(type IN ('income','expense')),
                        category TEXT,
                        amount REAL,
                        date TEXT,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                      )''')

    # Budgets Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS budgets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        category TEXT,
                        monthly_limit REAL,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                      )''')

    conn.commit()
    conn.close()

# User Management
def register():
    conn = sqlite3.connect("finance_manager.db")
    cursor = conn.cursor()

    username = input("Enter a username: ")
    password = getpass.getpass("Enter a password: ")

    try:
        cursor.execute("INSERT INTO users (username,password) VALUES (?,?)", (username, password))
        conn.commit()
        print("Registration successful!")
    except sqlite3.IntegrityError:
        print("Username already exists. Try again.")
    conn.close()

def login():
    conn = sqlite3.connect("finance_manager.db")
    cursor = conn.cursor()

    username = input("Username: ")
    password = getpass.getpass("Password: ")

    cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()

    if result:
        print(f"Welcome, {username}!")
        conn.close()
        return result[0]  # Return user_id
    else:
        print("Invalid credentials.")
        conn.close()
        return None

# Transactions 
def add_transaction(user_id):
    conn = sqlite3.connect("finance_manager.db")
    cursor = conn.cursor()

    t_type = input("Type (income/expense): ").lower()
    category = input("Category (Food, Rent, Salary, etc.): ")
    amount = float(input("Amount: "))
    date = datetime.date.today().isoformat()

    cursor.execute("INSERT INTO transactions (user_id, type, category, amount, date) VALUES (?,?,?,?,?)",
                   (user_id, t_type, category, amount, date))
    conn.commit()
    print("Transaction added successfully!")
    conn.close()

def view_transactions(user_id):
    conn = sqlite3.connect("finance_manager.db")
    cursor = conn.cursor()

    cursor.execute("SELECT type, category, amount, date FROM transactions WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()

    print("\n--- Your Transactions ---")
    for r in rows:
        print(f"{r[3]} | {r[0].upper()} | {r[1]} | ₹{r[2]}")
    conn.close()

# Financial Reports
def generate_report(user_id):
    conn = sqlite3.connect("finance_manager.db")
    cursor = conn.cursor()

    cursor.execute("SELECT type, SUM(amount) FROM transactions WHERE user_id=? GROUP BY type", (user_id,))
    data = dict(cursor.fetchall())

    income = data.get("income", 0)
    expense = data.get("expense", 0)
    savings = income - expense

    print("\n--- Financial Report ---")
    print(f"Total Income : ₹{income}")
    print(f"Total Expense: ₹{expense}")
    print(f"Total Savings: ₹{savings}")
    conn.close()

# Budgeting 
def set_budget(user_id):
    conn = sqlite3.connect("finance_manager.db")
    cursor = conn.cursor()

    category = input("Enter category for budget: ")
    limit = float(input("Enter monthly budget limit: "))

    cursor.execute("INSERT INTO budgets (user_id, category, monthly_limit) VALUES (?,?,?)", 
                   (user_id, category, limit))
    conn.commit()
    print("Budget set successfully!")
    conn.close()

def check_budget(user_id):
    conn = sqlite3.connect("finance_manager.db")
    cursor = conn.cursor()

    cursor.execute("SELECT category, monthly_limit FROM budgets WHERE user_id=?", (user_id,))
    budgets = cursor.fetchall()

    for category, limit in budgets:
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id=? AND category=? AND type='expense'", 
                       (user_id, category))
        spent = cursor.fetchone()[0] or 0

        if spent > limit:
            print(f"You have exceeded your budget for {category}! Spent: ₹{spent}, Limit: ₹{limit}")
    conn.close()

# Main Menu 
def main():
    init_db()
    print("Personal Finance Manager")
    while True:
        choice = input("\n1. Register\n2. Login\n3. Exit\nChoose an option: ")

        if choice == "1":
            register()
        elif choice == "2":
            user_id = login()
            if user_id:
                while True:
                    option = input("\n1. Add Transaction\n2. View Transactions\n3. Generate Report\n4. Set Budget\n5. Check Budget\n6. Logout\nChoose: ")

                    if option == "1":
                        add_transaction(user_id)
                    elif option == "2":
                        view_transactions(user_id)
                    elif option == "3":
                        generate_report(user_id)
                    elif option == "4":
                        set_budget(user_id)
                    elif option == "5":
                        check_budget(user_id)
                    elif option == "6":
                        break
        elif choice == "3":
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()

