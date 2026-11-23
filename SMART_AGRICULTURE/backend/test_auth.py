
from getpass import getpass

from farmer import register_farmer, login_farmer

from session import (
    start_session,
    is_logged_in,
    get_current_session,
    require_login,
    end_session
)


# Farmer dashboard
def farmer_dashboard():

    while is_logged_in():

        print("\n===== FARMER DASHBOARD =====")
        print("1. View My Session")
        print("2. Logout")

        choice = input("Choose an option: ").strip()

        if choice == "1":

            session = require_login()

            if session:
                print("\n--- Current Farmer Information ---")
                print("Farmer ID:", session["farmer_id"])
                print("Email:", session["email"])

        elif choice == "2":

            end_session()
            break

        else:
            print("Invalid option. Try again.")


# Main application
def main():

    while True:

        if is_logged_in():
            farmer_dashboard()
            continue

        print("\n===== SMART AGRICULTURE SYSTEM =====")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":

            print("\n--- Farmer Registration ---")

            name = input("Enter your name: ")
            email = input("Enter your email: ")
            phone = input("Enter your phone: ")
            password = getpass("Create password: ")

            register_farmer(name, email, phone, password)

        elif choice == "2":

            print("\n--- Farmer Login ---")

            email = input("Enter your email: ")
            password = getpass("Enter password: ")

            farmer_id = login_farmer(email, password)

            if farmer_id:

                start_session(farmer_id, email)

                farmer_dashboard()

        elif choice == "3":

            if is_logged_in():
                end_session()

            print("Thank you for using Smart Agriculture System!")
            break

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
