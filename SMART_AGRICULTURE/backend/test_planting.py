
from getpass import getpass
from datetime import date

from farmer import login_farmer
from session import start_session, end_session
from planting import add_planting_cycle, view_planting_cycles


def main():

    print("===== PLANTING CYCLE MANAGEMENT =====")

    email = input("Enter your email: ")
    password = getpass("Enter your password: ")

    farmer_id = login_farmer(email, password)

    if farmer_id is None:
        print("Login failed!")
        return

    start_session(farmer_id, email)

    try:
        print("\n--- Add Planting Cycle ---")

        field_id = int(input("Enter your Field ID: "))
        crop_id = int(input("Enter your Crop ID: "))

        planting_date = input("Enter planting date (YYYY-MM-DD): ")
        expected_harvest_date = input(
            "Enter expected harvest date (YYYY-MM-DD): "
        )

        # Validate date format
        date.fromisoformat(planting_date)
        date.fromisoformat(expected_harvest_date)

        if expected_harvest_date < planting_date:
            print("Harvest date cannot be before planting date.")
        else:
            add_planting_cycle(
                field_id,
                crop_id,
                planting_date,
                expected_harvest_date
            )

        print("\n--- View My Planting Cycles ---")

        view_planting_cycles()

    except ValueError:
        print("Invalid input! Check IDs and date format.")

    finally:
        end_session()


if __name__ == "__main__":
    main()
