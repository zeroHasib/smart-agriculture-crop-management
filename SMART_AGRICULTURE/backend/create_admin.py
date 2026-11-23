
from database import get_connection
from password_utils import hash_password
from getpass import getpass


def create_admin():

    print("\n========== CREATE ADMIN ACCOUNT ==========\n")

    full_name = input("Enter admin full name: ").strip()
    email = input("Enter admin email: ").strip().lower()

    password = getpass("Enter admin password: ")
    confirm_password = getpass("Confirm admin password: ")

    # Validation
    if not full_name:
        print("Full name is required.")
        return

    if len(full_name) > 100:
        print("Full name cannot exceed 100 characters.")
        return

    if not email or len(email) > 150:
        print("Enter a valid email.")
        return

    if len(password) < 8:
        print("Password must contain at least 8 characters.")
        return

    if password != confirm_password:
        print("Passwords do not match.")
        return

    connection = get_connection()

    if connection is None:
        print("Database connection failed.")
        return

    cursor = connection.cursor()

    try:

        # Check existing admin
        cursor.execute(
            "SELECT admin_id FROM admins WHERE email = %s",
            (email,)
        )

        if cursor.fetchone():
            print("An admin with this email already exists.")
            return

        # Hash password
        password_hash = hash_password(password)

        # Insert admin
        query = """
            INSERT INTO admins
            (full_name, email, password_hash)
            VALUES (%s, %s, %s)
        """

        cursor.execute(
            query,
            (full_name, email, password_hash)
        )

        connection.commit()

        print("\nAdmin account created successfully!")
        print("Admin ID:", cursor.lastrowid)
        print("Name:", full_name)
        print("Email:", email)

    except Exception as error:

        connection.rollback()
        print("Admin creation failed:", error)

    finally:

        cursor.close()
        connection.close()


if __name__ == "__main__":
    create_admin()
