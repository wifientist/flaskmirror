import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
import getpass

# Load environment variables from .env file
load_dotenv()

# Get the database URL from the environment variables
DATABASE_URL = os.getenv('DATABASE_URL')

# Prompt the user for admin email and password
admin_email = input("Enter the admin email: ")
admin_password = getpass.getpass("Enter the admin password: ")  # Hides the password input

# Admin user details
admin_name = admin_email
admin_role = 'admin'

# Hash the password
hashed_password = generate_password_hash(admin_password, method='pbkdf2:sha256')

# flag resetting_pw f
resetting_pw = "f"

# SQL command to check if the user already exists
check_user_query = sql.SQL('SELECT * FROM "user" WHERE email = %s')

# SQL command to insert a new user
insert_user_query = sql.SQL("""
    INSERT INTO "user" (name, email, role, password, resetting_pw)
    VALUES (%s, %s, %s, %s, %s)
""")

try:
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Check if the admin user already exists
    cursor.execute(check_user_query, (admin_email,))
    user = cursor.fetchone()

    if user:
        print(f"Admin user with email {admin_email} already exists.")
    else:
        # Insert the new admin user
        cursor.execute(insert_user_query, (admin_name, admin_email, admin_role, hashed_password, resetting_pw))
        conn.commit()
        print(f"Admin user {admin_name} created successfully.")

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
