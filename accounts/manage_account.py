import sqlite3
import random
import string
import sys

USER_DB_ABSOLUTE_PATH = '/home/zyh/inception/annotation/accounts/user_accounts.db'

# Function to generate a random 8-digit password
def generate_password():
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return password

# Function to create a new user account
def create_account(username, k=2):
    username = username +'_'+''.join(random.choices(string.ascii_letters, k=k))
    # Generate a random password
    password = generate_password()
    
    # Save the user account to the database
    conn = sqlite3.connect(USER_DB_ABSOLUTE_PATH)  # Connect to the database file
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

    return username,password

# Function to validate a user's credentials
def validate_user(username, password):
    conn = sqlite3.connect(USER_DB_ABSOLUTE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user is None:
        return False  # User not found

    if user[2] == password:
        return True  # Password is correct

    return False  # Password is incorrect

# Function to print all user information
def print_all_users():
    conn = sqlite3.connect(USER_DB_ABSOLUTE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()

    for user in users:
        print("Username:", user[1])
        print("Password:", user[2])
        print()

def main():
    if len(sys.argv) < 2:
        print("Usage: python manage.py [command]")
        print("Available commands:")
        print("- create <username>: Create a new user account")
        print("- validate <username> <password>: Validate user credentials")
        print("- print: Print all user information")
        return

    command = sys.argv[1]

    if command == "create":
        if len(sys.argv) < 3:
            print("Please provide a username")
            return

        username = sys.argv[2]
        username,password = create_account(username)
        print("Account created successfully!")
        print(f"Username:{username},Password: {password}")
        print()

    elif command == "create_formal":
        if len(sys.argv) < 3:
            print("Please provide a username")
            return

        username = sys.argv[2]
        username,password = create_account(username,3)
        print("Formal account created successfully!")
        print(f"Username:{username},Password: {password}")

    elif command == "validate":
        if len(sys.argv) < 4:
            print("Please provide a username and password")
            return

        username = sys.argv[2]
        password = sys.argv[3]
        if validate_user(username, password):
            print("Credentials are correct!")
        else:
            print("Credentials are incorrect!")
        print()

    elif command == "print":
        print("All users:")
        print_all_users()

    else:
        print("Invalid command")
        print("Available commands:")
        print("- create <username>: Create a new user account")
        print("- validate <username> <password>: Validate user credentials")
        print("- print: Print all user information")

if __name__ == '__main__':
    # parse the args to know which function to use:
    main()