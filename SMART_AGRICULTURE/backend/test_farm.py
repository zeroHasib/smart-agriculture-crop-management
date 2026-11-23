
from getpass import getpass

from farmer import login_farmer
from session import start_session, end_session

from farm import (
    add_farm,
    view_my_farms,
    add_field,
    view_my_fields
)


def main():

    print("===== FARM MANAGEMENT TEST =====")

    email = input("Enter your email: ")
    password = getpass("Enter your password: ")

    farmer_id = login_farmer(email, password)

    if farmer_id is None:
        print("Login failed!")
        return

    start_session(farmer_id, email)

    try:

        print("\n--- Add Farm ---")

        farm_name = input("Enter farm name: ")
        district = input("Enter district: ")

        farm_id = add_farm(farm_name, district)

        if farm_id:

            print("\n--- Add Field ---")

            field_name = input("Enter field name: ")
            area = float(input("Enter area in acres: "))
            soil_type = input("Enter soil type: ")
            soil_ph = float(input("Enter soil pH: "))

            add_field(
                farm_id,
                field_name,
                area,
                soil_type,
                soil_ph
            )

        print("\n--- View My Farms ---")
        view_my_farms()

        print("\n--- View My Fields ---")
        view_my_fields()

    except ValueError:
        print("Invalid numeric input.")

    finally:
        end_session()


if __name__ == "__main__":
    main()
