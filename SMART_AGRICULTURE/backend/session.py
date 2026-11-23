
# Current logged-in farmer
current_session = None


# 1. Create a session
def start_session(farmer_id, email):

    global current_session

    current_session = {
        "farmer_id": farmer_id,
        "email": email
    }

    print("Session created successfully!")


# 2. Check whether farmer is logged in
def is_logged_in():

    return current_session is not None


# 3. Get current session information
def get_current_session():

    if not is_logged_in():
        return None

    return current_session.copy()


# 4. Protect features that require login
def require_login():

    if not is_logged_in():
        print("Access denied! Please login first.")
        return None

    return get_current_session()


# 5. Logout and destroy session
def end_session():

    global current_session

    current_session = None

    print("Logged out successfully!")
