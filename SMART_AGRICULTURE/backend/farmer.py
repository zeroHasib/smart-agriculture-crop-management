
from database import get_connection
from password_utils import hash_password, verify_password


# ==========================================
# 1. REGISTER FARMER
# ==========================================

def register_farmer(name, email, phone, password):

    # Validate input
    if not name.strip():
        print("Name is required.")
        return None

    if not email.strip():
        print("Email is required.")
        return None

    if len(password) < 8:
        print("Password must contain at least 8 characters.")
        return None

    connection = get_connection()

    if connection is None:
        return None

    cursor = connection.cursor()

    try:
        # Hash the password before storing it
        password_hash = hash_password(password)

        query = """
            INSERT INTO farmers
            (full_name, email, phone, password_hash)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            name.strip(),
            email.strip(),
            phone.strip() or None,
            password_hash
        )

        cursor.execute(query, values)
        connection.commit()

        farmer_id = cursor.lastrowid

        print("Registration successful!")
        print("Welcome,", name)
        print("Your Farmer ID:", farmer_id)

        return farmer_id

    except Exception as error:

        connection.rollback()

        if getattr(error, "errno", None) == 1062:
            print("This email is already registered.")
        else:
            print("Registration failed:", error)

        return None

    finally:
        cursor.close()
        connection.close()


# ==========================================
# 2. FARMER LOGIN
# ==========================================

def login_farmer(email, password):

    connection = get_connection()

    if connection is None:
        return None

    cursor = connection.cursor()

    try:

        query = """
            SELECT farmer_id, full_name, password_hash
            FROM farmers
            WHERE email = %s
        """

        cursor.execute(query, (email.strip(),))

        farmer = cursor.fetchone()

        # Check whether farmer exists
        if farmer is None:
            print("Invalid email or password.")
            return None

        farmer_id, name, stored_hash = farmer

        # Verify password
        if verify_password(password, stored_hash):

            print("Login successful!")
            print("Welcome,", name)

            return farmer_id

        else:

            print("Invalid email or password.")
            return None

    except Exception as error:

        print("Login error:", error)
        return None

    finally:
        cursor.close()
        connection.close()


# ==========================================
# 3. VIEW ALL FARMERS
# ==========================================

def view_farmers():

    connection = get_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    try:

        query = """
            SELECT farmer_id, full_name, email, phone
            FROM farmers
            ORDER BY farmer_id
        """

        cursor.execute(query)

        farmers = cursor.fetchall()

        print("\n========== FARMER LIST ==========")

        if not farmers:
            print("No farmers found.")
            return

        for farmer in farmers:

            farmer_id, name, email, phone = farmer

            print("--------------------------------")
            print("Farmer ID:", farmer_id)
            print("Name:", name)
            print("Email:", email)
            print("Phone:", phone)

        print("--------------------------------")

    except Exception as error:

        print("Error viewing farmers:", error)

    finally:
        cursor.close()
        connection.close()
