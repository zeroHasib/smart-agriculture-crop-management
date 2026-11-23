
from getpass import getpass

from farmer import login_farmer
from session import start_session, end_session
from farm import add_farm, delete_farm, view_my_farms


def main():
    print("===== FARM DELETE TEST =====")

    email = input("Enter email: ")
    password = getpass("Enter password: ")

    farmer_id = login_farmer(email, password)

    if farmer_id is None:
        print("Login failed!")
        return

    start_session(farmer_id, email)

    try:
        print("\n--- Creating Temporary Farm ---")

        farm_id = add_farm(
            "Temporary Test Farm",
            "Cumilla"
        )

        if farm_id is None:
            print("Temporary farm creation failed!")
            return

        print("\n--- Farm Before Delete ---")
        view_my_farms()

        confirm = input(
            "\nDelete Temporary Test Farm? (yes/no): "
        )

        if confirm.lower() == "yes":
            delete_farm(farm_id)
        else:
            print("Delete cancelled.")

        print("\n--- Farms After Delete ---")
        view_my_farms()

    finally:
        end_session()


if __name__ == "__main__":
    main()
