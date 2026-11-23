
from database import get_connection
from password_utils import verify_password


# ==========================================
# ADMIN LOGIN
# ==========================================

def login_admin(email, password):

    connection = get_connection()

    if connection is None:
        return None

    cursor = connection.cursor()

    try:

        query = """
            SELECT admin_id, full_name, email, password_hash
            FROM admins
            WHERE email = %s
        """

        cursor.execute(query, (email.strip().lower(),))

        admin = cursor.fetchone()

        if admin is None:
            print("Invalid email or password.")
            return None

        admin_id, full_name, admin_email, stored_hash = admin

        if verify_password(password, stored_hash):

            print("Admin login successful!")

            return {
                "admin_id": admin_id,
                "full_name": full_name,
                "email": admin_email
            }

        print("Invalid email or password.")
        return None

    except Exception as error:

        print("Admin login error:", error)
        return None

    finally:
        cursor.close()
        connection.close()
