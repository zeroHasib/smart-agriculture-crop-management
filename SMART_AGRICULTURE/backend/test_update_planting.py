
from getpass import getpass

from farmer import login_farmer
from session import start_session, end_session
from planting import update_planting_status, view_planting_cycles


def main():

    print("===== UPDATE PLANTING STATUS =====")

    email = input("Enter your email: ")
    password = getpass("Enter your password: ")

    farmer_id = login_farmer(email, password)

    if farmer_id is None:
        print("Login failed!")
        return

    start_session(farmer_id, email)

    try:

        print("\n--- My Planting Cycles ---")
        view_planting_cycles()

        cycle_id = int(input("\nEnter Cycle ID: "))

        print("\n1. Growing")
        print("2. Harvested")
        print("3. Failed")

        choice = input("Choose new status: ")

        status_options = {
            "1": "Growing",
            "2": "Harvested",
            "3": "Failed"
        }

        new_status = status_options.get(choice)

        if new_status is None:
            print("Invalid choice!")
        else:
            update_planting_status(cycle_id, new_status)

        print("\n--- Updated Planting Cycles ---")
        view_planting_cycles()

    except ValueError:
        print("Invalid input!")

    finally:
        end_session()


if __name__ == "__main__":
    main()
