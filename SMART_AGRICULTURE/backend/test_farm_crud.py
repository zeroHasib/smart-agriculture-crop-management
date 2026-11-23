
from getpass import getpass

from farmer import login_farmer
from session import start_session, end_session
from farm import (
    view_my_farms,
    view_my_fields,
    update_farm,
    update_field
)

def main():

    print("===== FARM UPDATE TEST =====")

    email = input("Enter email: ")
    password = getpass("Enter password: ")

    farmer_id = login_farmer(email, password)

    if not farmer_id:
        print("Login failed!")
        return

    start_session(farmer_id, email)

    try:
        print("\n--- My Farms ---")
        view_my_farms()

        print("\n--- My Fields ---")
        view_my_fields()

        print("\n--- Update Farm ---")

        farm_id = int(input("Enter Farm ID: "))
        farm_name = input("New farm name: ")
        district = input("New district: ")

        update_farm(farm_id, farm_name, district)

        print("\n--- Update Field ---")

        field_id = int(input("Enter Field ID: "))
        field_name = input("New field name: ")
        area = float(input("New area: "))
        soil_type = input("New soil type: ")
        soil_ph = float(input("New soil pH: "))

        update_field(
            field_id,
            field_name,
            area,
            soil_type,
            soil_ph
        )

        print("\n--- Updated Information ---")
        view_my_farms()
        view_my_fields()

    except ValueError:
        print("Invalid input. Enter numeric values correctly.")

    finally:
        end_session()


if __name__ == "__main__":
    main()
