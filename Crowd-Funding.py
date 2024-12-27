import re
import sqlite3
import datetime

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('crowdfunding.db')
    c = conn.cursor()

    # Create Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    activated INTEGER DEFAULT 0
                )''')

    # Create Projects Table
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT NOT NULL,
                    details TEXT NOT NULL,
                    target_amount REAL NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )''')

    conn.commit()
    conn.close()

# Function to validate Egyptian phone number
def validate_phone(phone):
    pattern = r"^(\+20)[0-9]{10}$"
    return re.match(pattern, phone) is not None

# Function to validate the date
def validate_date(date_str):
    try:
        datetime.datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

# Register User
def register():
    print("Register a new account:")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    confirm_password = input("Confirm password: ")
    phone = input("Enter mobile phone (Egyptian format +20XXXXXXXXXX): ")
    
    if password != confirm_password:
        print("Passwords do not match!")
        return
    
    if not validate_phone(phone):
        print("Invalid phone number format!")
        return
    
    conn = sqlite3.connect('crowdfunding.db')
    c = conn.cursor()

    # Insert user into database
    try:
        c.execute("INSERT INTO users (first_name, last_name, email, password, phone) VALUES (?, ?, ?, ?, ?)",
                  (first_name, last_name, email, password, phone))
        conn.commit()
        print("Registration successful. Please check your email to activate your account.")
    except sqlite3.IntegrityError:
        print("This email is already registered.")
    
    conn.close()

# User Login
def login():
    print("Login:")
    email = input("Enter email: ")
    password = input("Enter password: ")

    conn = sqlite3.connect('crowdfunding.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = c.fetchone()
    conn.close()

    if user:
        print(f"Welcome, {user[1]} {user[2]}!")
        return user
    else:
        print("Invalid login or account not activated.")
        return None

# Activate the account
def activate_account(user):
    conn = sqlite3.connect('crowdfunding.db')
    c = conn.cursor()

    c.execute("UPDATE users SET activated = 1 WHERE id = ?", (user[0],))
    conn.commit()
    conn.close()
    print("Account activated successfully!")

# Create a Project
def create_project(user):
    print("Create a new fundraising project:")
    title = input("Enter project title: ")
    details = input("Enter project details: ")
    target_amount = float(input("Enter target amount in EGP: "))
    start_date = input("Enter start date (dd/mm/yyyy): ")
    end_date = input("Enter end date (dd/mm/yyyy): ")
    
    if not validate_date(start_date) or not validate_date(end_date):
        print("Invalid date format!")
        return
    
    conn = sqlite3.connect('crowdfunding.db')
    c = conn.cursor()

    c.execute("INSERT INTO projects (user_id, title, details, target_amount, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?)",
              (user[0], title, details, target_amount, start_date, end_date))
    conn.commit()
    conn.close()
    print(f"Project '{title}' created successfully!")

# View All Projects
def view_projects():
    print("Viewing all projects:")
    conn = sqlite3.connect('crowdfunding.db')
    c = conn.cursor()

    c.execute("SELECT * FROM projects")
    projects = c.fetchall()
    conn.close()

    for project in projects:
        print(f"ID: {project[0]}, Title: {project[3]}, Target: {project[5]} EGP, Start: {project[6]}, End: {project[7]}")

# Edit Project
def edit_project(user):
    print("Edit a project:")
    project_id = int(input("Enter project ID to edit: "))

    conn = sqlite3.connect('crowdfunding.db')
    c = conn.cursor()

    c.execute("SELECT * FROM projects WHERE id = ? AND user_id = ?", (project_id, user[0]))
    project = c.fetchone()

    if project:
        print("Editing project...")
        new_title = input("New title: ")
        new_details = input("New details: ")
        new_target = float(input("New target amount: "))
        new_start_date = input("New start date (dd/mm/yyyy): ")
        new_end_date = input("New end date (dd/mm/yyyy): ")

        if not validate_date(new_start_date) or not validate_date(new_end_date):
            print("Invalid date format!")
            return

        c.execute("UPDATE projects SET title = ?, details = ?, target_amount = ?, start_date = ?, end_date = ? WHERE id = ?",
                  (new_title, new_details, new_target, new_start_date, new_end_date, project_id))
        conn.commit()
        print("Project updated successfully!")
    else:
        print("You can only edit your own projects.")
    
    conn.close()

# Delete Project
def delete_project(user):
    print("Delete a project:")
    project_id = int(input("Enter project ID to delete: "))

    conn = sqlite3.connect('crowdfunding.db')
    c = conn.cursor()

    c.execute("SELECT * FROM projects WHERE id = ? AND user_id = ?", (project_id, user[0]))
    project = c.fetchone()

    if project:
        c.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()
        print("Project deleted successfully!")
    else:
        print("You can only delete your own projects.")
    
    conn.close()

# Search Projects (Bonus)
def search_projects():
    print("Search projects by start date:")
    search_date = input("Enter date to search for (dd/mm/yyyy): ")
    if not validate_date(search_date):
        print("Invalid date format!")
        return
    
    conn = sqlite3.connect('crowdfunding.db')
    c = conn.cursor()

    c.execute("SELECT * FROM projects WHERE start_date = ?", (search_date,))
    found_projects = c.fetchall()
    conn.close()

    if found_projects:
        print("Found projects:")
        for project in found_projects:
            print(f"ID: {project[0]}, Title: {project[3]}, Target: {project[5]} EGP, Start: {project[6]}, End: {project[7]}")
    else:
        print("No projects found with the given start date.")

# Main Function
def main():
    init_db()  # Initialize the database and tables

    user = None
    while True:
        print("\nMenu:")
        print("1. Register\n2. Login\n3. Create Project\n4. View All Projects\n5. Edit Project\n6. Delete Project\n7. Search Projects\n8. Exit")
        choice = input("Choose an option: ")
        
        if choice == "1":
            register()
        elif choice == "2":
            user = login()
            if user:
                print("Login successful!")
                activate = input("Activate your account? (y/n): ")
                if activate.lower() == 'y':
                    activate_account(user)
        elif choice == "3" and user:
            create_project(user)
        elif choice == "4":
            view_projects()
        elif choice == "5" and user:
            edit_project(user)
        elif choice == "6" and user:
            delete_project(user)
        elif choice == "7":
            search_projects()
        elif choice == "8":
            print("Exiting the application.")
            break
        else:
            print("Invalid option or you need to login first.")

if __name__ == "__main__":
    main()
