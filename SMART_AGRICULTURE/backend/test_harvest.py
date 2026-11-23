
from getpass import getpass
from datetime import date

from farmer import login_farmer
from session import start_session, end_session
from harvest import add_harvest, view_harvests


def main():

    print("===== HARVEST MANAGEMENT =====")

    email = input("Enter your email: ")
    password = getpass("Enter your password: ")

    farmer_id = login_farmer(email, password)

    if farmer_id is None:
        print("Login failed!")
        return

    start_session(farmer_id, email)

    try:

        print("\n--- Add Harvest Record ---")

        cycle_id = int(input("Enter Cycle ID: "))

        harvest_date = input("Enter harvest date (YYYY-MM-DD): ")
        date.fromisoformat(harvest_date)

        harvested_quantity = float(
            input("Enter total harvested quantity (KG): ")
        )

        sold_quantity = float(
            input("Enter sold quantity (KG): ")
        )

        price_per_kg = float(
            input("Enter selling price per KG: ")
        )

        description = input("Enter description: ")

        add_harvest(
            cycle_id,
            harvest_date,
            harvested_quantity,
            sold_quantity,
            price_per_kg,
            description
        )

        print("\n--- View My Harvest Records ---")

        view_harvests()

    except ValueError:
        print("Invalid input! Check date, quantity and price.")

    finally:
        end_session()


if __name__ == "__main__":
    main()
