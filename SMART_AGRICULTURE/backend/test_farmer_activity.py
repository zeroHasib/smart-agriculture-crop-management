
from getpass import getpass
from datetime import date

from farmer import login_farmer
from session import start_session, end_session
from farmer_activity import add_activity, view_activities


def main():

    print("===== FARMING ACTIVITY MANAGEMENT =====")

    email = input("Enter your email: ")
    password = getpass("Enter your password: ")

    farmer_id = login_farmer(email, password)

    if farmer_id is None:
        print("Login failed!")
        return

    start_session(farmer_id, email)

    try:

        print("\n--- Add Farming Activity ---")

        cycle_id = int(input("Enter Cycle ID: "))

        print("\n1. Irrigation")
        print("2. Fertilizing")
        print("3. Pesticide")
        print("4. Weeding")
        print("5. Land Preparation")

        choice = input("Choose activity type: ")

        activity_options = {
            "1": "Irrigation",
            "2": "Fertilizing",
            "3": "Pesticide",
            "4": "Weeding",
            "5": "Land Preparation"
        }

        activity_type = activity_options.get(choice)

        if activity_type is None:
            print("Invalid activity choice!")
            return

        activity_date = input("Enter activity date (YYYY-MM-DD): ")

        date.fromisoformat(activity_date)

        description = input("Enter description: ")

        cost = float(input("Enter activity cost: "))

        if cost < 0:
            print("Cost cannot be negative.")
            return

        add_activity(
            cycle_id,
            activity_type,
            activity_date,
            description,
            cost
        )

        print("\n--- View My Activities ---")

        view_activities()

    except ValueError:
        print("Invalid input! Check date, cost and Cycle ID.")

    finally:
        end_session()


if __name__ == "__main__":
    main()
